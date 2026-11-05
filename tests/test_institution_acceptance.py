"""Mission 024: independent adversarial checks of institutional source authority."""
from copy import deepcopy
import json
from pathlib import Path
import random
import tempfile
import unittest

from career_state import validate
from game_service import advance_day, execute_command, load_career, save_career
from institution_content import CIVILIAN
from incident_dispatch import WRONG_NOTICE
import test_institutions as scenarios


class InstitutionalSourceAcceptanceTests(unittest.TestCase):
    def source_world(self):
        helper = scenarios.InstitutionTests()
        world = helper.ready(211)
        helper.verify(world)
        helper.submit(world, 'ledger')
        return world

    def acquisition(self, world):
        return next(e for e in world['events'] if e['kind'] == 'incident_transition'
            and e.get('operation') == 'choose' and e['arguments']['stage'] == 'verify')

    def assert_rejected_readonly(self, world):
        before, rng = deepcopy(world), random.getstate()
        with self.assertRaises(ValueError):
            validate(world)
        self.assertEqual(world, before)
        self.assertEqual(random.getstate(), rng)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'edited.json'
            path.write_text(json.dumps(world), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_career(path)

    def test_source_transition_after_its_receipt_cannot_support_reporting(self):
        world = self.source_world()
        source = self.acquisition(world)
        world['events'].remove(source)
        receipt = next(e for e in world['events'] if e['kind'] == 'player_command'
            and e['command_id'] == source['command_id'])
        world['events'].insert(world['events'].index(receipt) + 1, source)
        self.assert_rejected_readonly(world)

    def test_source_transition_before_arrival_cannot_support_reporting(self):
        world = self.source_world()
        source = self.acquisition(world)
        world['events'].remove(source)
        arrival = next(e for e in reversed(world['events']) if e['kind'] == 'travel'
            and e['command_id'] < source['command_id'])
        world['events'].insert(world['events'].index(arrival), source)
        self.assert_rejected_readonly(world)

    def test_nonplayer_acquisition_receipt_cannot_grant_player_knowledge(self):
        world = self.source_world()
        source = self.acquisition(world)
        receipt = next(e for e in world['events'] if e['kind'] == 'player_command'
            and e['command_id'] == source['command_id'])
        receipt['actor'] = 'unrelated_npc'
        self.assert_rejected_readonly(world)

    def test_nonplayer_arrival_receipt_cannot_prove_player_counter_location(self):
        helper = scenarios.InstitutionTests()
        world = helper.ready(211)
        helper.submit(world, 'poster')
        arrival = next(e for e in reversed(world['events']) if e['kind'] == 'travel')
        receipt = next(e for e in world['events'] if e['kind'] == 'player_command'
            and e['command_id'] == arrival['command_id'])
        receipt['actor'] = 'unrelated_npc'
        self.assert_rejected_readonly(world)

    def test_unused_invalid_observation_rejects_before_it_can_be_previewed(self):
        helper = scenarios.InstitutionTests()
        world = helper.ready(211)
        helper.verify(world)
        source = self.acquisition(world)
        world['events'].remove(source)
        receipt = next(e for e in world['events'] if e['kind'] == 'player_command'
            and e['command_id'] == source['command_id'])
        world['events'].insert(world['events'].index(receipt) + 1, source)
        self.assert_rejected_readonly(world)

    def test_adoption_cannot_promote_an_unverifiable_historical_observation(self):
        helper = scenarios.InstitutionTests()
        world = helper.start(211, enabled=False)
        helper.until(world, world['wrong_notice']['information_day'])
        helper.go(world, 'p032')
        execute_command(world, 'discover_incident', incident_id=world['wrong_notice']['id'], channel='public_notice')
        helper.verify(world)
        source = self.acquisition(world)
        receipt = next(e for e in world['events'] if e['kind'] == 'player_command'
            and e['command_id'] == source['command_id'])
        receipt['actor'] = 'unrelated_npc'
        helper.reject(world, 'enable_institutions')

    def test_historical_anchor_requires_player_attributed_adoption(self):
        world = load_career(Path(__file__).parent / 'fixtures' / 'career_m011.json')
        execute_command(world, 'enable_navigation', anchor='n13')
        advance_day(world)
        execute_command(world, 'settle_in')
        advance_day(world)
        execute_command(world, 'enable_institutions')
        receipt = next(e for e in world['events'] if e['kind'] == 'player_command'
            and e['command'] == 'enable_navigation')
        receipt['actor'] = 'unrelated_npc'
        self.assert_rejected_readonly(world)

    def test_valid_modern_journey_sources_remain_readonly_and_roundtrip(self):
        import mobility
        from mobility_content import OVERLAY_ID
        helper = scenarios.InstitutionTests()
        world = helper.start(211)
        execute_command(world, 'enable_mobility', overlay_id=OVERLAY_ID, request_id='audit.source.mobility')
        helper.until(world, world['wrong_notice']['information_day'])
        execute_command(world, 'journey', **mobility.plan_route(world, 'p032', 'free')['arguments'])
        execute_command(world, 'discover_incident', incident_id=world['wrong_notice']['id'], channel='public_notice')
        execute_command(world, 'journey', **mobility.plan_route(world, 'n13', 'free')['arguments'])
        helper.verify(world)
        execute_command(world, 'institution_submit', institution_id=CIVILIAN, source_id=helper.claim(world, 'ledger'))
        before, rng = deepcopy(world), random.getstate()
        validate(world)
        self.assertEqual(world, before)
        self.assertEqual(random.getstate(), rng)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'valid.json'
            save_career(world, path)
            self.assertEqual(load_career(path), world)


if __name__ == '__main__':
    unittest.main()
