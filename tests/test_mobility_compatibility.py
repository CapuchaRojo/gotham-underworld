"""Mixed-history, migration, save failures and CLI integration regressions."""
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from career_state import validate
from game_service import advance_day, create_career, execute_command, load_career, save_career
import gameplay
import mobility
from mobility_content import OVERLAY_ID
import navigation
from test_mobility_pilot import adopted, move


class MobilityCompatibilityTests(unittest.TestCase):
    def enroll(self, world, rid='adopt'):
        return execute_command(world, 'enable_mobility', overlay_id=OVERLAY_ID, request_id=rid)

    def roundtrip(self, world):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(world, path)
            resumed = load_career(path)
            self.assertEqual(world, resumed)
            return resumed

    def test_all_historical_fixtures_load_without_mobility_or_replayed_events(self):
        paths = sorted((Path(__file__).parent / 'fixtures').rglob('*.json'))
        paths += sorted((Path(__file__).parent / 'mobility_fixtures').rglob('*.json'))
        self.assertTrue(any(p.parent.name == 'm014' for p in paths))
        self.assertTrue(any(p.parent.name == 'm015' for p in paths))
        for path in paths:
            with self.subTest(path=path):
                original = json.loads(path.read_text(encoding='utf-8'))
                world = load_career(path)
                self.assertNotIn('mobility', world)
                self.assertEqual(original['events'], world['events'])
                before = deepcopy(world)
                mobility.mobility_report(world)
                self.assertEqual(world, before)

    def test_pending_adoption_saves_without_activating_or_replenishing(self):
        world = create_career()
        execute_command(world, 'travel', destination='p032', mode='walk')
        old = deepcopy(world['navigation'])
        self.enroll(world)
        world = self.roundtrip(world)
        self.assertEqual(world['navigation'], old)
        self.assertEqual(world['navigation_version'], 2)
        self.assertEqual(world['mobility']['adoption']['status'], 'pending')
        self.assertEqual(world['navigation']['tu_used'], 1)
        for rid in ('adopt', 'another'):
            before = deepcopy(world)
            with self.assertRaises(ValueError):
                self.enroll(world, rid)
            self.assertEqual(before, world)

    def test_historical_rail_and_pending_travel_survive_new_journeys(self):
        world = create_career()
        execute_command(world, 'travel', destination='p039', mode='auto')
        execute_command(world, 'travel', destination='p071', mode='rail')
        self.enroll(world)
        execute_command(world, 'travel', destination='p039', mode='rail')
        legacy = deepcopy([e for e in world['events'] if e['kind'] == 'travel'])
        advance_day(world)
        checkpoint = world['mobility']['adoption']['legacy_checkpoint']
        self.assertEqual(checkpoint['tu_used'], 17)
        self.assertEqual(world['navigation']['tu_used'], 0)
        move(world, 'p071', 'monorail')
        world = self.roundtrip(world)
        self.assertEqual(legacy, [e for e in world['events'] if e['kind'] == 'travel' and e['schema_version'] == 1])
        self.assertEqual(world['navigation']['location_id'], 'goon.poi.p071')
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            navigation._validate_v1(world)

    def test_empty_legacy_prefix_has_no_invented_home_or_journey(self):
        world = create_career()
        self.enroll(world)
        advance_day(world)
        self.assertIsNone(world['mobility']['adoption']['legacy_checkpoint']['last_journey_id'])
        self.assertEqual(world['navigation']['location_id'], 'goon.poi.p031')
        self.roundtrip(world)

    def test_old_no_navigation_fixture_requires_existing_navigation_adoption(self):
        world = load_career(Path(__file__).parent / 'fixtures' / 'm001.json')
        with self.assertRaises(ValueError):
            self.enroll(world)
        execute_command(world, 'enable_navigation', anchor='n17')
        with self.assertRaises(ValueError):
            self.enroll(world)
        advance_day(world)
        self.enroll(world)
        advance_day(world)
        self.assertIsNone(world['navigation']['home_id'])
        self.roundtrip(world)

    def test_historical_adopter_can_accept_daily_life_home_later(self):
        world = load_career(Path(__file__).parent / 'fixtures' / 'm001.json')
        execute_command(world, 'enable_navigation', anchor='n13')
        advance_day(world)
        self.enroll(world)
        advance_day(world)
        self.assertIsNone(world['navigation']['home_id'])
        execute_command(world, 'settle_in')
        self.assertEqual(world['navigation']['home_id'], 'goon.poi.p031')
        advance_day(world)
        move(world, 'home', 'walk')
        self.roundtrip(world)

    def test_clock_only_load_does_not_activate_and_whole_day_phase_is_once(self):
        world = create_career()
        self.enroll(world)
        world['day'] += 1
        world = self.roundtrip(world)
        self.assertEqual(world['mobility']['adoption']['status'], 'pending')
        advance_day(world)
        self.assertEqual(world['mobility']['adoption']['activation_day'], 2)
        before = deepcopy(world)
        navigation.begin_day(world)
        self.assertEqual(before, world)

    def test_nonservice_reducer_cannot_activate_pending_mobility(self):
        world = create_career()
        self.enroll(world)
        gameplay.next_day(world)
        self.assertEqual(world['mobility']['adoption']['status'], 'pending')
        validate(world)
        advance_day(world)
        self.assertEqual(world['mobility']['adoption']['status'], 'active')

    def test_active_clock_only_resume_retains_spent_allowance(self):
        world = adopted()
        move(world, 'n17', 'walk')
        world['day'] += 1  # supported old batch-tool marker, not a player command
        world = self.roundtrip(world)
        self.assertEqual((world['navigation']['tu_day'], world['navigation']['tu_used']), (1, 1))
        move(world, 'p039', 'walk')
        self.assertEqual((world['navigation']['tu_day'], world['navigation']['tu_used']), (1, 2))
        advance_day(world)
        self.assertEqual((world['navigation']['tu_day'], world['navigation']['tu_used']), (3, 0))

    def test_active_repeated_adoption_and_unknown_overlay_reject(self):
        world = adopted()
        for overlay in (OVERLAY_ID, 'unknown'):
            before = deepcopy(world)
            with self.assertRaises(ValueError):
                execute_command(world, 'enable_mobility', overlay_id=overlay, request_id='again')
            self.assertEqual(before, world)

    def test_mixed_version_corruption_and_receipt_inconsistency_reject(self):
        world = adopted()
        move(world, 'p071', 'monorail')
        def latest(w):
            return next(e for e in w['events'] if e['kind'] == 'travel' and e['schema_version'] == 2)
        mutations = [lambda w: w.update(navigation_version=1),
            lambda w: w.update(mobility_version=2), lambda w: w.pop('mobility_version'),
            lambda w: w['mobility'].update(overlay_fingerprint='bad'),
            lambda w: latest(w).update(schema_version=1),
            lambda w: latest(w).update(journey_id=99),
            lambda w: latest(w)['resources']['cash'].update(cost=0),
            lambda w: latest(w)['resources']['tu'].update(after=0),
            lambda w: latest(w)['legs'][2].update(to_id='goon.neighborhood.n22'),
            lambda w: latest(w)['legs'][1].update(cash_cost=0),
            lambda w: w['mobility']['receipts'].clear(),
            lambda w: w['mobility']['adoption']['legacy_checkpoint'].update(location_id='goon.poi.p071'),
            lambda w: w['mobility']['adoption']['activation_budget'].update(tu_used=18),
            lambda w: w['mobility']['adoption'].update(requested_day=False),
            lambda w: w['mobility']['adoption']['legacy_checkpoint'].update(last_journey_id=True),
            lambda w: next(e for e in w['events'] if e['kind'] == 'travel').update(journey_id=None),
            lambda w: w['navigation'].update(location_id='goon.poi.p039'),
            lambda w: w['mobility']['assets'].update(car={}),
            lambda w: w['events'].append(deepcopy(latest(w)))]
        for mutate in mutations:
            invalid = deepcopy(world)
            mutate(invalid)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                validate(invalid)

    def test_duplicate_global_player_command_ids_cannot_hide_in_domain_indexes(self):
        world = adopted()
        move(world, 'p071', 'monorail')
        commands = [e for e in world['events'] if e['kind'] == 'player_command']
        commands[-1]['command_id'] = commands[0]['command_id']
        with self.assertRaisesRegex(ValueError, 'unique'):
            validate(world)

    def test_missing_mobility_state_never_silently_downgrades(self):
        world = adopted()
        world.pop('mobility')
        with self.assertRaises(ValueError):
            validate(world)

    def test_interrupted_resume_then_retry_and_recovery_are_exactly_once(self):
        world = adopted()
        world['navigation']['closures'].append(dict(id='save.hidden', edge_id='goon.edge.e06',
            from_id='goon.neighborhood.n18', mode='rail', start_day=world['day'], end_day=world['day']+2,
            known=False, cause='fixture'))
        q = mobility.plan_route(world, 'p071', 'monorail')
        execute_command(world, 'journey', **q['arguments'])
        resumed = self.roundtrip(world)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            execute_command(resumed, 'journey', **q['arguments'])
        self.assertEqual(world, resumed)
        move(world, 'p071', 'bus')
        move(resumed, 'p071', 'bus')
        self.assertEqual(world, resumed)

    def test_failed_save_preserves_disk_backup_and_committed_memory(self):
        import career_persistence
        world = adopted(life=True)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(world, path)
            saved = deepcopy(world)
            move(world, 'p071', 'monorail')
            committed = deepcopy(world)
            with patch('career_persistence.os.replace', side_effect=OSError('injected failure')):
                with self.assertRaises(OSError):
                    save_career(world, path)
            self.assertEqual(load_career(path), saved)
            self.assertEqual(world, committed)
            save_career(world, path)
            self.assertEqual(load_career(path), committed)
            self.assertEqual(load_career(Path(str(path)+'.bak')), saved)
            move(world, 'p039', 'monorail')
            committed_again = deepcopy(world)
            actual_replace = career_persistence.os.replace
            def fail_primary(src, destination):
                if Path(destination) == path:
                    raise OSError('injected final publication failure')
                return actual_replace(src, destination)
            for target, effect in (('career_persistence.os.fsync', OSError('injected flush failure')),
                                   ('career_persistence.os.replace', fail_primary)):
                with patch(target, side_effect=effect), self.assertRaises(OSError):
                    save_career(world, path)
                self.assertEqual(load_career(path), committed)
                self.assertEqual(world, committed_again)

    def test_malformed_mixed_history_is_rejected_by_disk_loader(self):
        world = adopted()
        move(world, 'p071', 'monorail')
        next(e for e in world['events'] if e['kind'] == 'travel' and e['schema_version'] == 2)['resources']['cash']['cost'] = 0
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad-career.json'
            path.write_text(json.dumps(world), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'monorail|cash'):
                load_career(path)

    def test_missing_overlay_cannot_reset_loaded_career(self):
        import mobility_content
        world = adopted()
        mobility_content._catalog.cache_clear()
        try:
            with patch('mobility_content.OVERLAY_PATH', Path('absent-mobility.json')):
                with self.assertRaisesRegex(ValueError, 'required local mobility overlay'):
                    validate(world)
        finally:
            mobility_content._catalog.cache_clear()

    def test_unexpected_post_reducer_error_discards_all_effects(self):
        world = adopted()
        q = mobility.plan_route(world, 'p071', 'monorail')
        before = deepcopy(world)
        with patch('game_service.validate', side_effect=ValueError('injected candidate validation')):
            with self.assertRaises(ValueError):
                execute_command(world, 'journey', **q['arguments'])
        self.assertEqual(before, world)

    def test_unused_adoption_preserves_legal_jobs_and_faction_outcomes(self):
        a, b = create_career(17), create_career(17)
        self.enroll(a)
        for world in (a, b):
            advance_day(world)
            execute_command(world, 'join', faction='Harbor Syndicate')
        for _ in range(15):
            for world in (a, b):
                execute_command(world, 'job', kind='collection')
                advance_day(world)
            for key in ('player', 'cases', 'legal', 'factions', 'districts', 'job_attempts'):
                self.assertEqual(a[key], b[key])

    def test_multiday_replay_with_resume_has_identical_whole_world(self):
        a, b = adopted(life=True), adopted(life=True)
        for day in range(12):
            for world in (a, b):
                for end in ('p071', 'p039'):
                    q = mobility.plan_route(world, end, 'fastest')
                    execute_command(world, 'journey', **q['arguments'])
                advance_day(world)
            b = self.roundtrip(b)
            self.assertEqual(a, b)

    def test_cli_reuses_route_and_travel_for_adopted_career(self):
        world = create_career()
        commands = iter(['mobility', 'travel p039', 'adopt_mobility', 'wait', 'route p071 monorail',
                         'travel p071 monorail', 'travel p039 bus', 'quit'])
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cli-career.json'
            with patch('builtins.input', side_effect=lambda _: next(commands)), patch('sys.stdout', output):
                gameplay.play(world, path)
            self.assertEqual(load_career(path), world)
        text = output.getvalue()
        self.assertIn('7 TU / $2 outbound', text)
        self.assertIn('spent 7 TU and $2', text)
        self.assertEqual((world['player']['cash'], world['navigation']['tu_used']), (38, 15))

