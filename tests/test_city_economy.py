"""M006 integration and deterministic city economy tests."""
import copy
import tempfile
import unittest
from pathlib import Path
from simulation import new_world
from gameplay import prepare, join, job, next_day, save, load
from city_economy import advance, summary


class CityEconomyTests(unittest.TestCase):
    def world(self, seed=42):
        return prepare(new_world(seed))

    def test_three_initial_districts(self):
        self.assertEqual(len(summary(self.world())), 3)

    def test_legacy_migration_idempotent(self):
        w = new_world()
        prepare(w)
        original = copy.deepcopy(w['districts'])
        prepare(w)
        self.assertEqual(w['districts'], original)

    def test_daily_income(self):
        w = self.world()
        old = w['factions']['Harbor Syndicate']['cash']
        next_day(w)
        self.assertEqual(w['factions']['Harbor Syndicate']['cash'], old + 4)

    def test_no_double_daily_income(self):
        w = self.world()
        next_day(w)
        before = copy.deepcopy(w['factions'])
        self.assertEqual(advance(w), [])
        self.assertEqual(w['factions'], before)

    def test_successful_job_changes_control(self):
        w = self.world(seed=42)
        join(w, 'Harbor Syndicate')
        before = w['districts']['Harbor Docks']['control']
        for _ in range(5):
            result = job(w, 'courier')
            if result['success']:
                break
        self.assertTrue(result['success'])
        self.assertGreater(w['districts']['Harbor Docks']['control'], before)

    def test_save_load_persists_economy(self):
        w = self.world()
        next_day(w)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'career.json'
            save(w, path)
            restored = load(path)
        self.assertEqual(restored['districts'], w['districts'])
        self.assertEqual(restored['economy_last_day'], w['economy_last_day'])

    def test_reproducible_city(self):
        a, b = self.world(23), self.world(23)
        for _ in range(8):
            next_day(a)
            next_day(b)
        self.assertEqual(a, b)

    def test_territory_transfer_on_exhaustion(self):
        w = self.world()
        w['districts']['Harbor Docks']['control'] = 1
        next_day(w)
        self.assertNotEqual(w['districts']['Harbor Docks']['owner'], 'Harbor Syndicate')
        self.assertTrue(any(e['kind'] == 'territory' and e.get('cause') == 'control_exhausted'
                            for e in w['events']))
