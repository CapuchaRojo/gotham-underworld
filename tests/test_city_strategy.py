import copy
import tempfile
import unittest
from pathlib import Path
from simulation import new_world
from gameplay import prepare, next_day, save, load
from city_strategy import assess, advance, summary
from faction_warfare import advance as warfare_advance


class CityStrategyTests(unittest.TestCase):
    def world(self):
        return prepare(new_world(42))

    def test_initial_migration(self):
        w = self.world()
        self.assertEqual(w['strategy_last_day'], 0)
        self.assertEqual(w['faction_strategy'], {})

    def test_assess_is_read_only(self):
        w = self.world()
        before = copy.deepcopy(w)
        self.assertEqual(assess(w, 'Harbor Syndicate'), assess(w, 'Harbor Syndicate'))
        self.assertEqual(w, before)

    def test_expansion_at_high_treasury(self):
        w = self.world()
        self.assertEqual(assess(w, 'Harbor Syndicate')['objective'], 'expand')

    def test_low_treasury_recovers(self):
        w = self.world()
        w['factions']['Harbor Syndicate']['cash'] = 10
        self.assertEqual(assess(w, 'Harbor Syndicate')['objective'], 'recover')

    def test_weak_district_defense(self):
        w = self.world()
        w['districts']['Harbor Docks']['control'] = 30
        plan = assess(w, 'Harbor Syndicate')
        self.assertEqual((plan['objective'], plan['district']), ('defend', 'Harbor Docks'))

    def test_player_pressure_triggers_defense(self):
        w = self.world()
        w['districts']['Harbor Docks']['control'] = 50
        w['events'].append({'day': 0, 'kind': 'district_mission', 'mission': 'expand',
                            'faction': 'Carnival Crew', 'district': 'Harbor Docks'})
        self.assertEqual(assess(w, 'Harbor Syndicate')['objective'], 'defend')

    def test_daily_idempotence(self):
        w = self.world()
        w['day'] = 2
        first = advance(w)
        self.assertEqual(len(first), 3)
        self.assertEqual(advance(w), [])
        self.assertEqual(len([e for e in w['events'] if e['kind'] == 'faction_strategy']), 3)

    def test_strategy_controls_warfare(self):
        w = self.world()
        w['day'] = 2
        w['factions']['Harbor Syndicate']['cash'] = 10
        advance(w)
        actions = warfare_advance(w)
        self.assertFalse(any(e['faction'] == 'Harbor Syndicate' for e in actions))
        self.assertTrue(all('strategy_objective' in e for e in actions))

    def test_full_day_determinism(self):
        a, b = self.world(), self.world()
        for _ in range(4):
            next_day(a)
            next_day(b)
        self.assertEqual(a, b)
        self.assertTrue(any(e['kind'] == 'faction_strategy' for e in a['events']))

    def test_save_load_and_no_replay(self):
        w = self.world()
        next_day(w)
        next_day(w)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'save.json'
            save(w, p)
            restored = load(p)
            self.assertEqual(restored, w)
            self.assertEqual(advance(restored), [])
            self.assertEqual(summary(restored), summary(w))

    def test_old_save_migrates_without_replay(self):
        w = self.world()
        w['day'] = 7
        del w['strategy_last_day']
        del w['strategy_version']
        del w['faction_strategy']
        prepare(w)
        self.assertEqual(w['strategy_last_day'], 7)
        self.assertEqual(advance(w), [])

    def test_invalid_faction(self):
        with self.assertRaises(ValueError):
            assess(self.world(), 'Unknown')


if __name__ == '__main__':
    unittest.main()
