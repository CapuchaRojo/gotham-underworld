import tempfile
import unittest
from pathlib import Path
from simulation import new_world
from gameplay import prepare, join, job, next_day, save, load


class ConsequenceTests(unittest.TestCase):
    def world(self, seed=42):
        w = prepare(new_world(seed))
        join(w, 'Harbor Syndicate')
        return w

    def test_reproducible_job_rolls(self):
        a, b = self.world(), self.world()
        for _ in range(8):
            self.assertEqual(job(a, 'collection'), job(b, 'collection'))
        self.assertEqual(a, b)

    def test_outcomes_have_causes(self):
        w = self.world()
        outcome = job(w, 'collection')
        self.assertEqual(outcome['cause'], 'player_job')
        self.assertIn('roll', outcome)
        self.assertIn('failure_chance', outcome)

    def test_witness_cases_trace_to_job(self):
        w = self.world()
        for _ in range(30):
            job(w, 'collection')
        self.assertTrue(w['cases'])
        self.assertTrue(all('source_attempt' in c for c in w['cases']))
        self.assertTrue(all(c['witnessed'] for c in w['cases']))

    def test_evidence_arrest_and_court(self):
        w = self.world()
        for _ in range(30):
            job(w, 'collection')
        next_day(w)
        next_day(w)
        self.assertTrue(any(c['status'] == 'convicted' for c in w['cases']))
        kinds = [e['kind'] for e in w['events']]
        self.assertLess(kinds.index('arrest'), kinds.index('court'))
        self.assertLess(kinds.index('court'), kinds.index('sentencing'))

    def test_save_load_preserves_roll_sequence(self):
        w = self.world()
        job(w, 'courier')
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'save.json'
            save(w, path)
            restored = load(path)
            self.assertEqual(job(w, 'collection'), job(restored, 'collection'))
            self.assertEqual(w, restored)

    def test_legacy_save_migration(self):
        w = new_world()
        self.assertNotIn('job_attempts', w)
        prepare(w)
        self.assertEqual(w['job_attempts'], 0)


if __name__ == '__main__':
    unittest.main()
