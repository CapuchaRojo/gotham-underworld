"""M005 regression checks for autonomous NPC actions."""
import json
import tempfile
import unittest
from pathlib import Path

from simulation import new_world
from gameplay import prepare, join, next_day, save, load
from relationship_engine import change
from npc_actions import act


class NPCActionsTests(unittest.TestCase):
    def setUp(self):
        self.world = prepare(new_world(42))

    def test_mara_support_and_cooldown(self):
        join(self.world, 'Harbor Syndicate')
        change(self.world, 'Mara Voss', {'trust': 5}, 'test')
        self.world['day'] = 1
        before = self.world['player']['cash']
        self.assertEqual(len(act(self.world)), 1)
        self.assertEqual(self.world['player']['cash'], before + 15)
        self.assertEqual(act(self.world), [])
        self.world['day'] = 3
        self.assertEqual(act(self.world), [])
        self.world['day'] = 4
        self.assertEqual(len(act(self.world)), 1)

    def test_eli_obstruction(self):
        join(self.world, 'Harbor Syndicate')
        change(self.world, 'Eli Crowe', {'hostility': 5}, 'test')
        before = self.world['factions']['Harbor Syndicate']['power']
        self.world['day'] = 1
        result = act(self.world)
        self.assertEqual(result[0]['npc'], 'Eli Crowe')
        self.assertEqual(self.world['factions']['Harbor Syndicate']['power'], before - 2)

    def test_vale_requires_documented_case(self):
        change(self.world, 'Detective Vale', {'suspicion': 16}, 'test')
        self.world['day'] = 1
        self.assertEqual(act(self.world), [])
        self.world['cases'].append({'id': 1, 'status': 'pending', 'witnessed': True,
                                    'evidence': 1, 'source_attempt': 0})
        self.assertEqual(act(self.world)[0]['case_id'], 1)
        self.assertEqual(self.world['cases'][0]['evidence'], 2)

    def test_vale_can_charge_with_traceable_evidence(self):
        change(self.world, 'Detective Vale', {'suspicion': 16}, 'test')
        self.world['cases'].append({'id': 1, 'status': 'pending', 'witnessed': True,
                                    'evidence': 2, 'source_attempt': 3})
        self.world['day'] = 1
        act(self.world)
        self.assertTrue(self.world['player']['arrested'])
        self.assertEqual(self.world['cases'][0]['status'], 'charged')
        self.assertTrue(any(e['kind'] == 'arrest' and e['cause'] == 'npc_evidence_review'
                            for e in self.world['events']))

    def test_save_load_preserves_cooldown(self):
        join(self.world, 'Harbor Syndicate')
        change(self.world, 'Mara Voss', {'trust': 5}, 'test')
        self.world['day'] = 1
        act(self.world)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'career.json'
            save(self.world, path)
            restored = load(path)
        self.assertEqual(restored['npc_action_last_day'], {'Mara Voss': 1})
        self.assertEqual(act(restored), [])

    def test_determinism(self):
        a = prepare(new_world(42))
        b = prepare(new_world(42))
        for world in (a, b):
            join(world, 'Harbor Syndicate')
            change(world, 'Mara Voss', {'trust': 5}, 'test')
            for _ in range(4):
                next_day(world)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_legacy_world_initializes(self):
        self.assertEqual(act(self.world), [])
        self.assertEqual(self.world['npc_action_last_day'], {})

    def test_no_support_while_detained(self):
        join(self.world, 'Harbor Syndicate')
        change(self.world, 'Mara Voss', {'trust': 5}, 'test')
        self.world['player']['arrested'] = True
        self.world['day'] = 1
        self.assertEqual(act(self.world), [])


if __name__ == '__main__':
    unittest.main()
