"""Mission 008 acceptance and corruption regressions, using the public service."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from career_state import validate
from game_service import (advance_day, create_career, execute_command, load_career,
                          location_report, plan_route, save_career)
import location_registry
import navigation


class M014AuditTests(unittest.TestCase):
    def travel(self, world, destination):
        return execute_command(world, 'travel', destination=destination, mode='auto')

    def test_contradictory_location_or_budget_is_rejected_on_disk_load(self):
        world = create_career()
        self.travel(world, 'p032')
        for field, value in (('location_id', 'goon.neighborhood.n31'), ('tu_used', 0)):
            malformed = deepcopy(world)
            malformed['navigation'][field] = value
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'career.json'
                path.write_text(json.dumps(malformed), encoding='utf-8')
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                    load_career(path)

    def test_one_command_cannot_have_duplicate_or_missing_journey_outcomes(self):
        world = create_career()
        self.travel(world, 'p032')
        duplicate = deepcopy(world)
        result = next(e for e in duplicate['events'] if e['kind'] == 'travel')
        duplicate['events'].append(dict(deepcopy(result), journey_id=2))
        duplicate['navigation']['journey_sequence'] = 2
        with self.assertRaisesRegex(ValueError, 'one journey outcome'):
            validate(duplicate)
        missing = deepcopy(world)
        missing['events'] = [e for e in missing['events'] if e['kind'] != 'travel']
        missing['navigation']['journey_sequence'] = 0
        with self.assertRaisesRegex(ValueError, 'every travel command'):
            validate(missing)

    def test_journey_day_must_match_its_command(self):
        world = create_career()
        self.travel(world, 'p032')
        advance_day(world)
        next(e for e in world['events'] if e['kind'] == 'travel')['day'] = 1
        with self.assertRaisesRegex(ValueError, 'travel.day'):
            validate(world)

    def test_detained_preview_and_travel_reject_without_mutation(self):
        world = create_career()
        world['cases'].append(dict(id=1, crime='fixture', suspect='Rookie', status='charged', evidence=3))
        world['player'].update(arrested=True, custody='pretrial')
        validate(world)
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, 'detained'):
            plan_route(world, 'p032')
        with self.assertRaisesRegex(ValueError, 'detained'):
            self.travel(world, 'p032')
        self.assertEqual(world, before)
        self.assertTrue(location_report(world)['current'])
        advance_day(world)
        self.travel(world, 'p032')
        validate(world)

    def test_authorized_corridors_require_an_enforced_receiving_gate(self):
        data = location_registry.load()
        public = next(e for e in data['edges'] if e['id'] == 'goon.edge.e05')
        public['access'] = 'authorized'
        with self.assertRaisesRegex(ValueError, 'restricted receiving endpoint'):
            location_registry.validate(data)
        public['access'] = 'location'
        with self.assertRaisesRegex(ValueError, 'POI access policy'):
            location_registry.validate(data)
        # The unchanged Blackgate definition remains supported; its landing
        # authorization does not grant admission to a separate prison POI.
        world = create_career()
        world['navigation']['location_id'] = 'goon.neighborhood.n43'
        with self.assertRaisesRegex(ValueError, 'Restricted'):
            self.travel(world, 'n46')
        world['navigation']['permissions'].append('goon.neighborhood.n46')
        self.travel(world, 'n46')
        with self.assertRaisesRegex(ValueError, 'Restricted'):
            self.travel(world, 'p112')
        world['navigation']['permissions'].clear()
        self.travel(world, 'n43')
        validate(world)

    def test_return_preview_respects_directional_closure_and_current_budget(self):
        world = create_career()
        self.travel(world, 'n13')
        world['navigation']['closures'].append(dict(id='audit.return', edge_id='goon.edge.e06',
            from_id='goon.neighborhood.n23', mode='bus', start_day=0, end_day=2,
            known=True, cause='audit.fixture'))
        quote = plan_route(world, 'n31', 'bus')
        self.assertEqual((quote['cost'], quote['return_cost']), (6, 8))
        self.assertTrue(quote['return_fits_today'])
        for destination in ('p032', 'n13', 'p032', 'n13'):
            self.travel(world, destination)
        quote = plan_route(world, 'n31', 'bus')
        self.assertTrue(quote['affordable'])
        self.assertFalse(quote['return_fits_today'])
        validate(world)

    def test_unused_navigation_does_not_change_existing_world_outcomes(self):
        enabled = create_career(17)
        legacy = deepcopy(enabled)
        legacy.pop('navigation')
        legacy.pop('navigation_version')
        for world in (enabled, legacy):
            execute_command(world, 'join', faction='Harbor Syndicate')
        for day in range(30):
            for world in (enabled, legacy):
                execute_command(world, 'job', kind='collection')
                pending = [c for c in world['cases'] if c['status'] == 'pending' and
                           str(c['id']) not in world['legal']['responses']]
                if pending and day % 3 == 0:
                    execute_command(world, 'cooperate', case_id=str(pending[0]['id']))
                advance_day(world)
                validate(world)
            normalized = deepcopy(enabled)
            normalized.pop('navigation')
            normalized.pop('navigation_version')
            self.assertEqual(normalized, legacy)

    def test_a_to_d_and_f_playable_acceptance_resume(self):
        world = create_career(42)
        self.travel(world, 'p032')
        self.travel(world, 'home')
        advance_day(world)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(world, path)
            self.assertEqual(load_career(path), world)
            resumed = load_career(path)
            for day in range(8):
                for state in (world, resumed):
                    for index in range(18):
                        self.travel(state, 'p032' if index % 2 == 0 else 'home')
                    before = deepcopy(state)
                    with self.assertRaisesRegex(ValueError, 'TU'):
                        self.travel(state, 'p032')
                    self.assertEqual(state, before)
                    self.assertIn('Saving', location_report(state)['help'])
                self.assertEqual(world, resumed)
                save_career(resumed, path)
                resumed = load_career(path)
                for state in (world, resumed):
                    advance_day(state)
                self.assertEqual(world, resumed)
            self.travel(world, 'n13')
            world['navigation']['closures'].append(dict(id='audit.hidden', edge_id='goon.edge.e06',
                from_id='goon.neighborhood.n18', mode='bus', start_day=world['day'],
                end_day=world['day'] + 2, known=False, cause='audit.fixture'))
            outcome = execute_command(world, 'travel', destination='n31', mode='bus')['result']
            self.assertEqual(outcome['arrived'], 'goon.neighborhood.n18')
            self.assertEqual(outcome['tu_cost'], 2)
            self.assertTrue(outcome['interrupted'])
            save_career(world, path)
            self.assertEqual(load_career(path), world)
            validate(world)


if __name__ == '__main__':
    unittest.main()
