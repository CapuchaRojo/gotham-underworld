"""Ephemeral adapters over existing chronological incident records, never truth scans."""
from copy import deepcopy

from incident_dispatch import NIGHT_SHIFT, WRONG_NOTICE, bindings
from institution_content import CIVILIAN, INTAKE


class Sources:
    def __init__(self, seed):
        self.seed = seed
        self.states = {}
        self.player = {}
        self.automatic = {}
        self.specs = bindings()

    def receive_response(self, response, transition_id, position):
        """One explicitly handed-over copy, not inference from an institution's state.

        Validation calls this with the independently replayed response. The live
        catalogue reads already committed response events; no old journal changes.
        """
        if response.get('assistance') != 'dated_correction_copy':
            return
        finding = response['beliefs']['delivery_day']
        if finding['confidence'] != 'documented':
            raise ValueError('A correction copy needs a received documentary basis')
        key = response['id']+'.copy.delivery_day'
        self.player[key] = dict(id=key, incident_id=response['incident_id'], topic='delivery_day',
            value=deepcopy(finding['value']), credibility='documented', observer=response['institution_id'],
            limitation='Certified copy of this desk record only; not primary inspection or legal proof.',
            origin_event=transition_id, observed_day=response['day'], position=position,
            learned_command=response['command_id'])

    def observe(self, event, position):
        if event['kind'] not in ('incident_enabled','notice_enabled','incident_transition'):
            return
        for ident, spec in sorted(self.specs.items()):
            adapter = spec['adapter']
            if event['kind'] == spec['enabled']:
                self.states[ident] = adapter.initial(self.seed, event['day'])
                return
            if event['kind'] != 'incident_transition' or event.get('incident_id') != self.states.get(ident, {}).get('id'):
                continue
            state = self.states[ident]
            before = deepcopy(state)
            adapter.reduce(state, event['operation'], event['day'], event['arguments'], event['context'])

            def source(key, topic, value, credibility, observer, limitation):
                return dict(id=key, incident_id=state['id'], topic=topic, value=value,
                    credibility=credibility, observer=observer, limitation=limitation,
                    origin_event=event['transition_id'], observed_day=event['day'],
                    position=position, learned_command=event.get('command_id'))

            def npc(item, actor, route):
                self.automatic[(actor, item['id'])] = dict(source=deepcopy(item), institution_id=actor,
                    route=route, available_day=event['day'] + 1)

            if ident == NIGHT_SHIFT:
                if 'alarm_observed' not in before['owner_facts'] and 'alarm_observed' in state['owner_facts']:
                    npc(source(state['id']+'.source.public_alarm', 'alarm', 'reported', 'limited',
                        'shop_board', 'A shop alarm notice identifies no cause or offender.'), CIVILIAN, 'shop_board_round')
                if 'owner_alarm_report' not in before['desk_facts'] and 'owner_alarm_report' in state['desk_facts']:
                    npc(source(state['id']+'.source.owner_alarm', 'alarm', 'reported', 'limited',
                        'goon.contact.ada', 'Copy of the owner alarm report, not a finding of guilt.'), INTAKE, 'owner_report_forward')
                if 'owner_review_received' not in before['desk_facts'] and 'owner_review_received' in state['desk_facts']:
                    npc(source(state['id']+'.source.owner_review', 'cause', state['truth'], 'documented',
                        'goon.contact.ada', 'Owner review of this alarm only; no offender identified.'), INTAKE, 'owner_review_forward')
                for fact in state['player_facts']:
                    if fact in before['player_facts']:
                        continue
                    topic, value = ('cause', state['truth']) if fact == 'cause_verified' else ('alarm', 'reported')
                    self.player[state['id']+'.source.'+fact] = source(state['id']+'.source.'+fact,
                        topic, value, 'documented' if fact == 'cause_verified' else 'limited',
                        'player_inspection' if fact != 'alarm_reported' else (
                            'shop_board' if state['discovery']['channel']=='public_notice' else 'goon.contact.tess'),
                        'Only the actually acquired observation; no suspect or legal conclusion.')
            else:
                def claim(key):
                    c = state['claims'][key]
                    return source(c['id'], 'delivery_day', c['delivery_day'],
                        'documented' if key in ('ledger','review') else 'printed' if key == 'poster' else 'limited',
                        c['source'], c['limitation'])
                if before['world_status'] == 'eligible' and state['world_status'] != 'eligible':
                    npc(claim('poster'), CIVILIAN, 'shop_board_round')
                    npc(claim('handbill'), CIVILIAN, 'resident_round')
                if before['aftermath'] is None and state['aftermath'] is not None:
                    npc(claim('review'), CIVILIAN, 'public_circular_round')
                for key in state['player_claims']:
                    if key not in before['player_claims']:
                        item = claim(key)
                        self.player.setdefault(item['id'], item)
            return


def catalogue(world):
    sources = Sources(world['seed'])
    for position, event in enumerate(world['events']):
        sources.observe(event, position)
        if event['kind']=='institution_transition' and event.get('operation')=='followup':
            sources.receive_response(event['result']['response'],event['transition_id'],position)
    return sources
