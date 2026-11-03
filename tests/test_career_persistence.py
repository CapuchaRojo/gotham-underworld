"""M011 persistence boundaries, crash safety, and historical save fixtures."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from career_persistence import decode
from career_state import validate
from game_service import create_career, execute_command, load_career, save_career


class CareerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'career.json'
        self.world = create_career()

    def assert_rejected(self, mutate, message):
        world = deepcopy(self.world)
        mutate(world)
        self.path.write_text(json.dumps(world), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, message):
            load_career(self.path)

    def assert_existing_values_preserved(self, old, new):
        if isinstance(old, dict):
            for key, value in old.items():
                self.assertIn(key, new)
                self.assert_existing_values_preserved(value, new[key])
        elif isinstance(old, list):
            self.assertEqual(len(old), len(new))
            for left, right in zip(old, new):
                self.assert_existing_values_preserved(left, right)
        else:
            self.assertEqual(old, new)

    def test_malformed_nested_state(self):
        mutations = [
            (lambda w: w.update(player=None), 'player'),
            (lambda w: w.update(day='1'), 'day'),
            (lambda w: w.update(day=True), 'day'),
            (lambda w: w['player'].pop('arrested'), 'arrested'),
            (lambda w: w['player'].update(cash=-1), 'cash'),
            (lambda w: w['people']['Mara Voss'].update(memory=[None]), 'memory'),
            (lambda w: w['people']['Mara Voss']['relationship'].update(trust=101), 'trust'),
            (lambda w: w['districts']['Harbor Docks'].update(owner='unknown'), 'owner'),
            (lambda w: w['districts']['Harbor Docks'].update(control=101), 'control'),
            (lambda w: w.update(events=[{'day': 0, 'kind': 'economy', 'message': 'bad', 'income': '4'}]), 'income'),
            (lambda w: w.update(events=[{'day': 0, 'kind': 'district_mission', 'message': 'bad', 'mission': 'expand', 'district': []}]), 'district'),
            (lambda w: w.update(npc_action_last_day={'unknown': 0}), 'NPC'),
            (lambda w: w.update(actions_used=4), 'actions_used'),
            (lambda w: w.update(action_day=1), 'action_day'),
            (lambda w: w.update(command_sequence=-1), 'command_sequence'),
            (lambda w: w.update(faction_strategy={'Harbor Syndicate': None}), 'faction_strategy'),
            (lambda w: w.update(district_intel={'unknown': {}}), 'district'),
        ]
        for mutate, message in mutations:
            with self.subTest(message=message):
                self.assert_rejected(mutate, message)

    def test_rejects_unsupported_and_noninteger_versions(self):
        for key in ('save_version', 'strategy_version', 'warfare_version', 'consequence_version',
                    'npc_action_version', 'district_mission_version'):
            for version in (999, True, '1'):
                with self.subTest(key=key, version=version):
                    self.assert_rejected(lambda w: w.update({key: version}), key)

    def test_rejects_duplicate_keys_nonfinite_and_invalid_json(self):
        for text in ('{"day":0,"day":1}', '{"day":NaN}', '{"day":Infinity}', '{"extension":1e999}', '{'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                decode(text)

    def test_rejects_invalid_utf8(self):
        self.path.write_bytes(b'\xff')
        with self.assertRaisesRegex(ValueError, 'UTF-8'):
            load_career(self.path)

    def test_rejects_missing_versioned_contract_fields(self):
        for key in ('action_day', 'actions_used', 'command_sequence', 'districts',
                    'faction_strategy', 'district_intel', 'npc_action_last_day', 'consequence_version'):
            with self.subTest(key=key):
                self.assert_rejected(lambda w: w.pop(key), key)

    def test_missing_versioned_relationship_data_is_not_silently_recreated(self):
        self.assert_rejected(lambda w: w['people']['Mara Voss'].pop('relationship'), 'relationship')
        self.assert_rejected(lambda w: w['people']['Mara Voss']['relationship'].pop('trust'), 'relationship')

    def test_rejects_inconsistent_custody_and_duplicate_cases(self):
        self.assert_rejected(lambda w: w['player'].update(arrested=True, custody='pretrial'), 'charged case')
        self.assert_rejected(lambda w: w['player'].update(custody='pretrial'), 'custody')
        case = {'id': 1, 'crime': 'robbery', 'suspect': 'Rookie', 'status': 'open', 'evidence': 1}
        self.assert_rejected(lambda w: w.update(cases=[case, case]), 'unique')

    def test_atomic_overwrite_keeps_previous_valid_bytes(self):
        save_career(self.world, self.path)
        previous = self.path.read_bytes()
        execute_command(self.world, 'join', faction='Harbor Syndicate')
        save_career(self.world, self.path)
        self.assertEqual(self.path.with_suffix('.json.bak').read_bytes(), previous)
        self.assertEqual(load_career(self.path), self.world)
        self.assertEqual(list(Path(self.folder.name).glob('*.tmp')), [])

    def test_failed_final_replace_preserves_primary_and_backup(self):
        save_career(self.world, self.path)
        previous = self.path.read_bytes()
        execute_command(self.world, 'join', faction='Harbor Syndicate')
        replace = os.replace
        def fail_primary(source, destination):
            if Path(destination) == self.path:
                raise OSError('injected replacement failure')
            return replace(source, destination)
        with patch('career_persistence.os.replace', side_effect=fail_primary):
            with self.assertRaises(OSError):
                save_career(self.world, self.path)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(self.path.with_suffix('.json.bak').read_bytes(), previous)
        self.assertEqual(load_career(self.path), create_career())
        self.assertEqual(list(Path(self.folder.name).glob('*.tmp')), [])

    def test_failed_backup_replace_does_not_touch_primary(self):
        save_career(self.world, self.path)
        previous = self.path.read_bytes()
        with patch('career_persistence.os.replace', side_effect=OSError('backup failure')):
            with self.assertRaises(OSError):
                save_career(self.world, self.path)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(Path(self.folder.name).glob('*.tmp')), [])

    def test_failed_flush_does_not_touch_primary(self):
        save_career(self.world, self.path)
        previous = self.path.read_bytes()
        with patch('career_persistence.os.fsync', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                save_career(self.world, self.path)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(Path(self.folder.name).glob('*.tmp')), [])

    def test_failed_serialization_does_not_touch_primary(self):
        save_career(self.world, self.path)
        previous = self.path.read_bytes()
        self.world['extension'] = object()
        with self.assertRaisesRegex(ValueError, 'serialize'):
            save_career(self.world, self.path)
        self.assertEqual(self.path.read_bytes(), previous)

    def test_invalid_existing_file_cannot_destroy_backup(self):
        save_career(self.world, self.path)
        save_career(self.world, self.path)
        backup = self.path.with_suffix('.json.bak').read_bytes()
        self.path.write_text('broken', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Existing career is invalid'):
            save_career(self.world, self.path)
        self.assertEqual(self.path.read_text(encoding='utf-8'), 'broken')
        self.assertEqual(self.path.with_suffix('.json.bak').read_bytes(), backup)

    def test_exclusive_new_save_does_not_overwrite_competing_file(self):
        self.path.write_text('other session', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            save_career(self.world, self.path, overwrite=False)
        self.assertEqual(self.path.read_text(encoding='utf-8'), 'other session')
        self.assertEqual(list(Path(self.folder.name).glob('*.tmp')), [])

    def test_exclusive_first_save_is_loadable(self):
        save_career(self.world, self.path, overwrite=False)
        self.assertEqual(load_career(self.path), self.world)

    def test_save_does_not_mutate_caller_and_retains_extensions(self):
        self.world['extension'] = {'future_id': 'enterprise.test', 'values': [1, 2]}
        before = deepcopy(self.world)
        save_career(self.world, self.path)
        self.assertEqual(self.world, before)
        self.assertEqual(load_career(self.path), before)

    def test_historical_fixtures_migrate_without_replaying_events(self):
        fixtures = Path(__file__).parent / 'fixtures'
        for path in sorted(fixtures.glob('m*.json')):
            with self.subTest(milestone=path.stem):
                old = json.loads(path.read_text(encoding='utf-8'))
                world = load_career(path)
                self.assert_existing_values_preserved(old, world)
                self.assertEqual(world['events'], old['events'])
                self.assertEqual(world['day'], old['day'])
                self.assertEqual(world['player']['cash'], old['player']['cash'])
                self.assertEqual(world['player']['heat'], old['player']['heat'])
                self.assertEqual(world['factions'], old['factions'])
                self.assertEqual(world['save_version'], 1)
                before = deepcopy(world)
                import gameplay
                gameplay.prepare(world)
                self.assertEqual(world, before)
                save_career(world, self.path)
                self.assertEqual(load_career(self.path), world)
                execute_command(world, 'wait')
                validate(world)
        self.assertEqual(len(list(fixtures.glob('m*.json'))), 10)

    def test_legacy_same_day_work_does_not_refresh_budget(self):
        world = deepcopy(self.world)
        for key in ('save_version', 'action_day', 'actions_used', 'command_sequence'):
            world.pop(key)
        world['events'] = [{'day': 0, 'kind': 'job', 'message': 'legacy work'} for _ in range(10)]
        self.path.write_text(json.dumps(world), encoding='utf-8')
        restored = load_career(self.path)
        self.assertEqual(restored['actions_used'], 3)
        self.assertEqual(restored['events'], world['events'])

    def test_explicit_legacy_version_is_upgraded(self):
        self.world['save_version'] = 0
        self.path.write_text(json.dumps(self.world), encoding='utf-8')
        self.assertEqual(load_career(self.path)['save_version'], 1)

    def test_investigation_marker_survives_disk_resume(self):
        from consequence_engine import investigate
        self.world['cases'].append({'id': 1, 'crime': 'collection intimidation', 'suspect': 'Rookie',
                                    'status': 'pending', 'evidence': 1, 'witnessed': True,
                                    'source_attempt': 0, 'investigation_days': 0})
        investigate(self.world)
        save_career(self.world, self.path)
        restored = load_career(self.path)
        before = deepcopy(restored)
        investigate(restored)
        self.assertEqual(restored, before)

    def test_command_sequence_cannot_reuse_recorded_ids(self):
        execute_command(self.world, 'join', faction='Harbor Syndicate')
        self.assert_rejected(lambda w: w.update(command_sequence=0), 'command_sequence')
        command_event = deepcopy(self.world['events'][-1])
        self.assert_rejected(lambda w: w['events'].append(command_event), 'command_id')


if __name__ == '__main__':
    unittest.main()
