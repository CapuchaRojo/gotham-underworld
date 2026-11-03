import tempfile
import unittest
from pathlib import Path
from simulation import new_world
from gameplay import prepare, join, job, next_day, save, load
from relationship_engine import change, decision


class RelationshipTests(unittest.TestCase):
    def test_legacy_migration(self):
        world = prepare(new_world())
        self.assertEqual(world['people']['Mara Voss']['relationship']['trust'], 0)
        self.assertEqual(world['people']['Mara Voss']['relationship_history'], [])

    def test_recruitment_changes_trust(self):
        world = prepare(new_world())
        join(world, 'Harbor Syndicate')
        self.assertEqual(world['people']['Mara Voss']['relationship']['trust'], 5)
        self.assertEqual(world['people']['Mara Voss']['relationship_history'][0]['cause'], 'recruitment')

    def test_jobs_change_relationships_and_record_attempt(self):
        world = prepare(new_world())
        join(world, 'Harbor Syndicate')
        outcome = job(world, 'collection')
        history = world['people']['Mara Voss']['relationship_history']
        self.assertEqual(history[-1]['source_attempt'], outcome['attempt'])
        self.assertEqual(history[-1]['cause'], 'job_success' if outcome['success'] else 'job_failure')

    def test_bounded_scores(self):
        world = prepare(new_world())
        change(world, 'Mara Voss', {'trust': 500}, 'test')
        change(world, 'Mara Voss', {'trust': -900}, 'test')
        self.assertEqual(world['people']['Mara Voss']['relationship']['trust'], -100)

    def test_decisions_follow_history(self):
        world = prepare(new_world())
        self.assertEqual(decision(world, 'Mara Voss')['action'], 'neutral')
        change(world, 'Mara Voss', {'trust': 11}, 'favor')
        self.assertEqual(decision(world, 'Mara Voss')['action'], 'offer_support')
        change(world, 'Mara Voss', {'hostility': 5}, 'betrayal')
        self.assertEqual(decision(world, 'Mara Voss')['action'], 'refuse_cooperation')

    def test_investigation_increases_suspicion(self):
        world = prepare(new_world())
        join(world, 'Harbor Syndicate')
        for _ in range(30):
            job(world, 'collection')
        self.assertTrue(world['cases'])
        next_day(world)
        self.assertGreater(world['people']['Detective Vale']['relationship']['suspicion'], 0)

    def test_save_load_preserves_relationships(self):
        world = prepare(new_world())
        join(world, 'Harbor Syndicate')
        job(world, 'courier')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'career.json'
            save(world, path)
            self.assertEqual(load(path), world)

    def test_deterministic_relationships(self):
        a, b = prepare(new_world()), prepare(new_world())
        for w in (a, b):
            join(w, 'Harbor Syndicate')
            for _ in range(5):
                job(w, 'collection')
            next_day(w)
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
