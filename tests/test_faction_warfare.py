"""M008 deterministic warfare regression and integration tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from simulation import new_world
from gameplay import prepare, next_day, save, load
from faction_warfare import advance, ATTACK_COST, DEFENSE_COST


class FactionWarfareTests(unittest.TestCase):
    def setUp(self):
        self.world = prepare(new_world(42))

    def test_daily_warfare_produces_auditable_actions(self):
        self.world['day'] = 2
        actions = advance(self.world)
        self.assertTrue(actions)
        self.assertTrue(all(e['kind'] == 'faction_warfare' for e in actions))
        self.assertTrue(all('cause' in e and 'district' in e for e in actions))

    def test_idempotent_on_same_day(self):
        self.world['day'] = 2
        advance(self.world)
        snapshot = copy.deepcopy(self.world)
        self.assertEqual(advance(self.world), [])
        self.assertEqual(self.world, snapshot)

    def test_defense_prioritized_for_weak_district(self):
        self.world['districts']['Harbor Docks']['control'] = 20
        self.world['day'] = 2
        actions = advance(self.world)
        harbor = next(a for a in actions if a['faction'] == 'Harbor Syndicate')
        self.assertEqual(harbor['action'], 'defend')
        self.assertGreater(harbor['control_delta'], 0)
        self.assertEqual(harbor['cost'], DEFENSE_COST)

    def test_attack_targets_weakest_rival(self):
        self.world['districts']['Carnival Row']['control'] = 14
        self.world['districts']['Ironworks']['control'] = 40
        self.world['day'] = 2
        actions = advance(self.world)
        harbor = next(a for a in actions if a['faction'] == 'Harbor Syndicate')
        self.assertEqual(harbor['district'], 'Carnival Row')
        self.assertEqual(harbor['cost'], ATTACK_COST)

    def test_capture_changes_owner(self):
        self.world['districts']['Carnival Row']['control'] = 1
        self.world['day'] = 2
        actions = advance(self.world)
        self.assertTrue(any(a.get('captured') for a in actions))
        self.assertEqual(self.world['districts']['Carnival Row']['owner'], 'Harbor Syndicate')

    def test_no_negative_treasury(self):
        for faction in ('Harbor Syndicate', 'Carnival Crew', 'Iron Mask Outfit'):
            self.world['factions'][faction]['cash'] = 0
        self.world['day'] = 2
        self.assertEqual(advance(self.world), [])
        self.assertTrue(all(v['cash'] >= 0 for v in self.world['factions'].values()))

    def test_npc_memory_tracks_actions(self):
        self.world['day'] = 2
        actions = advance(self.world)
        self.assertTrue(any(a['npc'] == 'Mara Voss' for a in actions))
        self.assertTrue(self.world['people']['Mara Voss']['memory'])

    def test_legacy_migration_does_not_replay(self):
        old = new_world(42)
        old['day'] = 7
        prepare(old)
        self.assertEqual(old['warfare_last_day'], 6)
        self.assertEqual(len([e for e in old['events'] if e['kind'] == 'faction_warfare']), 0)

    def test_save_load_preserves_warfare_state(self):
        self.world['day'] = 2
        advance(self.world)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save(self.world, path)
            restored = load(path)
        self.assertEqual(restored, self.world)
        self.assertEqual(advance(restored), [])

    def test_full_day_integration_and_determinism(self):
        a = prepare(new_world(42))
        b = prepare(new_world(42))
        for _ in range(3):
            next_day(a)
            next_day(b)
        self.assertEqual(a, b)
        self.assertTrue(any(e['kind'] == 'faction_warfare' for e in a['events']))


if __name__ == '__main__':
    unittest.main()
