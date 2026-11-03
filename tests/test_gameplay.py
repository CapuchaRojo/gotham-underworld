import tempfile
import unittest
from pathlib import Path
from simulation import new_world
from gameplay import GANGS, prepare, join, job, next_day, save, load


class GameplayTests(unittest.TestCase):
    def test_join_and_memory(self):
        world = prepare(new_world())
        join(world, GANGS[0])
        self.assertEqual(world['player']['faction'], GANGS[0])
        self.assertEqual(world['people']['Mara Voss']['memory'][-1]['fact'], 'Rookie joined Harbor Syndicate.')

    def test_job_rewards_and_reputation(self):
        world = prepare(new_world())
        join(world, GANGS[0])
        result = job(world, 'collection')
        self.assertEqual(world['player']['cash'], 40 + result['payout'])
        self.assertEqual(world['player']['heat'], 2 + (not result['success']))
        self.assertEqual(world['player']['reputation'][GANGS[0]], 1 + (2 if result['success'] else -1))

    def test_requires_faction(self):
        with self.assertRaises(ValueError):
            job(prepare(new_world()), 'courier')

    def test_cannot_switch_factions(self):
        world = prepare(new_world())
        join(world, GANGS[0])
        with self.assertRaises(ValueError):
            join(world, GANGS[1])

    def test_save_load_and_advance(self):
        world = prepare(new_world())
        join(world, GANGS[1])
        next_day(world)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'save.json'
            save(world, path)
            self.assertEqual(load(path), world)

    def test_m001_save_compatibility(self):
        world = prepare(new_world())
        self.assertIn('reputation', world['player'])
        self.assertIsNone(world['player']['faction'])


if __name__ == '__main__':
    unittest.main()
