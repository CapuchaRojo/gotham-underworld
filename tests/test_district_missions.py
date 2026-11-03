import copy
import tempfile
import unittest
from pathlib import Path

from simulation import new_world
from gameplay import prepare, join, next_day, save, load
from district_missions import mission


class DistrictMissionTests(unittest.TestCase):
    def world(self):
        w = prepare(new_world(42))
        join(w, 'Harbor Syndicate')
        return w

    def test_scout_records_intel(self):
        w = self.world()
        result = mission(w, 'scout', 'Carnival Row')
        self.assertEqual(result['cause'], 'player_district_mission')
        self.assertEqual(w['district_intel']['Carnival Row']['owner'], 'Carnival Crew')

    def test_fortify_increases_control(self):
        w = self.world()
        before = w['districts']['Harbor Docks']['control']
        mission(w, 'fortify', 'Harbor Docks')
        self.assertEqual(w['districts']['Harbor Docks']['control'], before + 8)

    def test_cannot_fortify_rival(self):
        with self.assertRaises(ValueError):
            mission(self.world(), 'fortify', 'Carnival Row')

    def test_cannot_expand_owned(self):
        with self.assertRaises(ValueError):
            mission(self.world(), 'expand', 'Harbor Docks')

    def test_daily_limit_and_no_charge(self):
        w = self.world()
        mission(w, 'scout', 'Carnival Row')
        cash = w['player']['cash']
        with self.assertRaises(ValueError):
            mission(w, 'scout', 'Ironworks')
        self.assertEqual(w['player']['cash'], cash)

    def test_expansion_captures_on_zero(self):
        w = self.world()
        w['districts']['Carnival Row']['control'] = 10
        result = mission(w, 'expand', 'Carnival Row')
        self.assertTrue(result['captured'])
        self.assertEqual(w['districts']['Carnival Row']['owner'], 'Harbor Syndicate')
        self.assertEqual(w['districts']['Carnival Row']['control'], 35)

    def test_save_load_preserves_state(self):
        w = self.world()
        mission(w, 'scout', 'Ironworks')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'career.json'
            save(w, p)
            restored = load(p)
        self.assertEqual(restored['district_intel'], w['district_intel'])
        self.assertEqual(restored['district_mission_last_day'], 0)
        with self.assertRaises(ValueError):
            mission(restored, 'scout', 'Carnival Row')

    def test_reproducible_with_daily_ticks(self):
        def scenario():
            w = self.world()
            mission(w, 'fortify', 'Harbor Docks')
            next_day(w)
            mission(w, 'scout', 'Carnival Row')
            return w
        self.assertEqual(scenario(), scenario())

    def test_legacy_migration(self):
        w = new_world()
        prepare(w)
        self.assertEqual(w['district_intel'], {})
        self.assertEqual(w['district_mission_last_day'], -1)

    def test_invalid_or_unaffordable_is_atomic(self):
        w = self.world()
        original = copy.deepcopy(w)
        with self.assertRaises(ValueError):
            mission(w, 'expand', 'Missing')
        self.assertEqual(w, original)
        w['player']['cash'] = 0
        with self.assertRaises(ValueError):
            mission(w, 'expand', 'Carnival Row')
        self.assertEqual(w['district_mission_last_day'], -1)
