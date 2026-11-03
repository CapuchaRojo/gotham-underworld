import unittest
from simulation import new_world, robbery, advance, resolve_case, run

class SimulationTests(unittest.TestCase):
    def test_reproducible(self):
        self.assertEqual(run(seed=17), run(seed=17))

    def test_memory_and_evidence(self):
        w = new_world()
        robbery(w)
        self.assertEqual(len(w['people']['Mara Voss']['memory']), 1)
        advance(w)
        self.assertEqual(w['cases'][0]['evidence'], 2)

    def test_crime_to_sentence(self):
        w = new_world()
        robbery(w)
        advance(w)
        advance(w)
        self.assertTrue(w['player']['arrested'])
        resolve_case(w)
        self.assertFalse(w['player']['arrested'])
        self.assertEqual(w['cases'][0]['status'], 'convicted')
        self.assertTrue(any(e['kind'] == 'prison' for e in w['events']))

    def test_no_crime_no_cases(self):
        self.assertEqual(run(commit_crime=False)['cases'], [])

if __name__ == '__main__':
    unittest.main()
