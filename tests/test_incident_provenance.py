"""M017-B: discovery claims must have historical navigation/contact sources."""
from copy import deepcopy
import json
from pathlib import Path
import random
import tempfile
import unittest

from career_state import validate
from game_service import (advance_day, create_career, execute_command, incident_report,
                          load_career, save_career)
import world_incidents


class IncidentProvenanceTests(unittest.TestCase):
    def fresh(self, seed=907):
        w = create_career(seed)
        execute_command(w, 'settle_in')
        advance_day(w)
        return w

    def until(self, w, day):
        while w['day'] < day:
            advance_day(w)

    def ready(self, w):
        execute_command(w, 'enable_incidents')
        self.until(w, w['incidents']['information_day'])
        return w

    def public(self):
        w = self.ready(self.fresh())
        execute_command(w, 'travel', destination='p032', mode='walk')
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='public_notice')
        return w

    def contact(self, *, moved=False):
        w = self.fresh()
        execute_command(w, 'choose', choice_id='goon.choice.0.promise', option_id='promise')
        advance_day(w)
        execute_command(w, 'choose', choice_id='goon.choice.0.crossroads', option_id='renegotiate' if moved else 'help')
        if moved:
            self.until(w, 4)
            execute_command(w, 'choose', choice_id='goon.choice.0.rescheduled_help', option_id='help')
        self.ready(w)
        execute_command(w, 'travel', destination='n13', mode='walk')
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='contact')
        return w

    def discovery(self, w):
        return next(e for e in w['events'] if e['kind'] == 'incident_transition' and e.get('operation') == 'discover')

    def change_channel(self, w, channel, location, reference):
        e = self.discovery(w)
        e['arguments']['channel'] = channel
        e['context'].update(location=location, tess_reference=reference)
        command = next(c for c in w['events'] if c['kind'] == 'player_command' and c['command_id'] == e['command_id'])
        command['arguments']['channel'] = channel
        w['incidents']['discovery']['channel'] = channel

    def bad(self, w):
        before, rng = deepcopy(w), random.getstate()
        with self.assertRaises(ValueError):
            validate(w)
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'contradictory.json'
            path.write_text(json.dumps(w), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_career(path)

    def roundtrip(self, w):
        before = deepcopy(w)
        validate(w)
        self.assertEqual(w, before)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'valid.json'
            save_career(w, path)
            self.assertEqual(load_career(path), w)

    def move_after_discovery(self, w, event):
        w['events'].remove(event)
        w['events'].insert(w['events'].index(self.discovery(w)) + 1, event)

    def test_valid_public_notice_uses_past_arrival_not_current_location(self):
        w = self.public()
        execute_command(w, 'travel', destination='home', mode='walk')
        self.roundtrip(w)
        self.assertEqual(w['navigation']['location_id'], 'goon.poi.p031')
        self.assertEqual(self.discovery(w)['context']['location'], 'goon.poi.p032')

    def test_valid_tess_reference_and_rescheduled_promise(self):
        for moved in (False, True):
            with self.subTest(rescheduled=moved):
                w = self.contact(moved=moved)
                # Existing save contracts retain unrelated additive metadata;
                # proving a fact must compare its canonical fields only.
                memory = next(m for m in w['daily_life']['contacts']['goon.contact.tess']['memories']
                              if m['fact'] == 'promise_kept')
                memory['annotation'] = {'local_note': 'retained optional metadata'}
                self.roundtrip(w)

    def test_exact_forged_tess_reference_reproducer(self):
        w = self.public()
        self.change_channel(w, 'contact', 'goon.neighborhood.n13', True)
        self.bad(w)
        # Isolate the reference check from location: preserve a real arrival at
        # the hub, but transplant a coherently edited discovery with no reference.
        public = self.public()
        hub = self.ready(self.fresh())
        execute_command(hub, 'travel', destination='n13', mode='walk')
        self.change_channel(public, 'contact', 'goon.neighborhood.n13', True)
        discovery = self.discovery(public)
        receipt = next(e for e in public['events'] if e['kind'] == 'player_command' and e['command_id'] == discovery['command_id'])
        hub['events'].extend(deepcopy([discovery, receipt]))
        hub['incidents'] = deepcopy(public['incidents'])
        hub['command_sequence'] = public['command_sequence']
        self.assertEqual(hub['navigation']['location_id'], discovery['context']['location'])
        self.bad(hub)

    def test_real_reference_does_not_prove_forged_location_or_channel(self):
        w = self.contact()
        self.change_channel(w, 'public_notice', 'goon.poi.p032', True)
        self.bad(w)

    def test_future_arrival_cannot_support_earlier_discovery(self):
        w = self.contact()
        execute_command(w, 'travel', destination='p032', mode='walk')
        self.change_channel(w, 'public_notice', 'goon.poi.p032', True)
        self.bad(w)

    def test_reference_source_memory_cannot_be_reordered_after_discovery(self):
        w = self.contact()
        event = next(e for e in w['events'] if e['kind'] == 'life_memory' and e.get('fact') == 'promise_kept')
        self.move_after_discovery(w, event)
        self.bad(w)

    def test_reference_choice_and_receipt_cannot_be_reordered(self):
        for kind in ('life_choice', 'player_command'):
            w = self.contact()
            record = w['daily_life']['choices']['goon.choice.0.crossroads']
            command_id = record['selection']['command_id']
            event = next(e for e in w['events'] if e['kind'] == kind and e.get('command_id') == command_id)
            self.move_after_discovery(w, event)
            with self.subTest(kind=kind):
                self.bad(w)

    def test_original_invitation_is_not_a_future_source(self):
        w = self.contact()
        event = next(e for e in w['events'] if e['kind'] == 'life_choice' and e.get('choice_id') == 'goon.choice.0.promise')
        self.move_after_discovery(w, event)
        self.bad(w)

    def test_travel_outcome_cannot_be_reordered_after_discovery(self):
        w = self.public()
        self.move_after_discovery(w, next(e for e in w['events'] if e['kind'] == 'travel'))
        self.bad(w)

    def test_discovery_must_precede_its_receipt(self):
        w = self.public()
        event = self.discovery(w)
        command = next(e for e in w['events'] if e['kind'] == 'player_command' and e['command_id'] == event['command_id'])
        w['events'].remove(event)
        w['events'].insert(w['events'].index(command) + 1, event)
        self.bad(w)

    def test_missing_and_duplicated_supporting_sources_reject(self):
        for kind in ('life_memory', 'life_promise', 'life_choice', 'travel'):
            for operation in ('missing', 'duplicate'):
                w = self.contact()
                events = [e for e in w['events'] if e['kind'] == kind]
                source = next((e for e in events if e.get('fact') == 'promise_kept'), events[-1])
                if operation == 'missing':
                    w['events'].remove(source)
                else:
                    w['events'].insert(w['events'].index(source), deepcopy(source))
                with self.subTest(kind=kind, operation=operation):
                    self.bad(w)

    def test_no_trace_cannot_fall_back_to_current_position(self):
        w = self.public()
        travel = next(e for e in w['events'] if e['kind'] == 'travel')
        w['events'] = [e for e in w['events'] if e is not travel and not
            (e['kind'] == 'player_command' and e['command_id'] == travel['command_id'])]
        w['navigation'].update(journey_sequence=0, tu_used=0)
        self.bad(w)

    def test_later_same_day_reference_is_not_backfilled(self):
        seed = next(s for s in range(20) if world_incidents.initial(s, 1)['occurrence_day'] == 2)
        w = self.fresh(seed)
        execute_command(w, 'choose', choice_id='goon.choice.0.promise', option_id='promise')
        execute_command(w, 'enable_incidents')
        advance_day(w)
        execute_command(w, 'travel', destination='p032', mode='walk')
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='public_notice')
        execute_command(w, 'travel', destination='home', mode='walk')
        execute_command(w, 'choose', choice_id='goon.choice.0.crossroads', option_id='help')
        self.assertFalse(self.discovery(w)['context']['tess_reference'])
        self.roundtrip(w)
        self.discovery(w)['context']['tess_reference'] = True
        self.bad(w)

    def test_legacy_daily_pipeline_without_wait_receipt_remains_valid(self):
        from gameplay import next_day
        w = self.fresh()
        execute_command(w, 'enable_incidents')
        while w['day'] < w['incidents']['information_day']:
            next_day(w)
        execute_command(w, 'travel', destination='p032', mode='walk')
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='public_notice')
        self.roundtrip(w)

    def test_real_historical_navigation_adoption_supports_contact_discovery(self):
        w = load_career(Path(__file__).parent / 'fixtures/career_m011.json')
        execute_command(w, 'enable_navigation', anchor='n13')
        advance_day(w)
        execute_command(w, 'settle_in')
        advance_day(w)
        execute_command(w, 'travel', destination='home', mode='walk')
        execute_command(w, 'choose', choice_id='goon.choice.0.promise', option_id='promise')
        advance_day(w)
        execute_command(w, 'choose', choice_id='goon.choice.0.crossroads', option_id='help')
        self.ready(w)
        execute_command(w, 'travel', destination='n13', mode='walk')
        execute_command(w, 'discover_incident', incident_id=w['incidents']['id'], channel='contact')
        self.roundtrip(w)

    def test_future_modern_journey_does_not_rewrite_legacy_discovery(self):
        import mobility
        from mobility_content import OVERLAY_ID
        w = self.contact()
        execute_command(w, 'enable_mobility', overlay_id=OVERLAY_ID, request_id='provenance.modern')
        advance_day(w)
        execute_command(w, 'journey', **mobility.plan_route(w, 'p032', 'free')['arguments'])
        self.roundtrip(w)
        self.change_channel(w, 'public_notice', 'goon.poi.p032', True)
        self.bad(w)

    def test_occurrence_requires_prior_daily_source_and_validation_is_readonly(self):
        w = self.public()
        before, rng = deepcopy(w), random.getstate()
        for _ in range(3):
            validate(w)
            incident_report(w)
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)
        tick = next(e for e in w['events'] if e['kind'] == 'incident_transition' and e.get('operation') == 'tick')
        source = next(e for e in w['events'] if e['kind'] == 'life_day' and e['day'] == tick['day'])
        self.move_after_discovery(w, source)
        self.bad(w)

    def test_rejected_command_on_contradictory_context_preserves_state_and_rng(self):
        w = self.public()
        self.change_channel(w, 'contact', 'goon.neighborhood.n13', True)
        before, rng = deepcopy(w), random.getstate()
        with self.assertRaises(ValueError):
            execute_command(w, 'join', faction='Harbor Syndicate')
        self.assertEqual(w, before)
        self.assertEqual(random.getstate(), rng)


if __name__ == '__main__':
    unittest.main()
