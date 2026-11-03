"""M011 command atomicity, action economy, deterministic resume, and CLI."""
from copy import deepcopy
import contextlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import gameplay
from career_state import DAILY_ACTION_ALLOWANCE, validate
from game_service import (COMMANDS, actions_remaining, advance_day, create_career,
                          execute_command, load_career, save_career, snapshot)
from simulation import new_world


class GameServiceTests(unittest.TestCase):
    def world(self):
        world = create_career()
        execute_command(world, 'join', faction='Harbor Syndicate')
        return world

    def test_budget_blocks_fourth_job_without_any_mutation(self):
        world = self.world()
        for _ in range(DAILY_ACTION_ALLOWANCE):
            execute_command(world, 'job', kind='courier')
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            execute_command(world, 'job', kind='courier')
        self.assertEqual(world, before)
        self.assertEqual(world['job_attempts'], 3)
        self.assertEqual(world['day'], 0)
        advance_day(world)
        self.assertEqual(actions_remaining(world), 3)
        execute_command(world, 'job', kind='courier')
        self.assertEqual(actions_remaining(world), 2)

    def test_jobs_and_missions_share_allowance_and_mission_limit_remains(self):
        world = self.world()
        execute_command(world, 'mission', kind='scout', district='Carnival Row')
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, 'One district mission'):
            execute_command(world, 'mission', kind='scout', district='Ironworks')
        self.assertEqual(world, before)
        execute_command(world, 'job', kind='courier')
        execute_command(world, 'job', kind='courier')
        self.assertEqual(actions_remaining(world), 0)

    def test_recruitment_and_snapshots_are_free(self):
        world = self.world()
        before = deepcopy(world)
        snapshot(world)
        self.assertEqual(world, before)
        self.assertEqual(actions_remaining(world), 3)

    def test_failed_commands_are_atomic(self):
        world = self.world()
        commands = [('join', {'faction': 'Carnival Crew'}), ('job', {'kind': 'unknown'}),
                    ('mission', {'kind': 'expand', 'district': 'missing'}),
                    ('mission', {'kind': 'fortify', 'district': 'Carnival Row'}),
                    ('wait', {'unexpected': 'value'}), ('job', {'kind': 1}), ('missing', {})]
        for command, arguments in commands:
            before = deepcopy(world)
            with self.subTest(command=command, arguments=arguments), self.assertRaises(ValueError):
                execute_command(world, command, **arguments)
            self.assertEqual(world, before)
        world['player']['cash'] = 0
        before = deepcopy(world)
        with self.assertRaises(ValueError):
            execute_command(world, 'mission', kind='scout', district='Ironworks')
        self.assertEqual(world, before)

    def test_internal_command_failure_cannot_partially_commit(self):
        world = self.world()
        before = deepcopy(world)
        def failing_handler(candidate, kind):
            candidate['player']['cash'] += 999
            candidate['events'].append({'message': 'partial'})
            raise RuntimeError('injected reducer failure')
        with patch.dict(COMMANDS, {'job': (1, ('kind',), failing_handler)}):
            with self.assertRaises(RuntimeError):
                execute_command(world, 'job', kind='courier')
        self.assertEqual(world, before)

    def test_snapshot_and_command_response_are_detached(self):
        world = self.world()
        response = execute_command(world, 'job', kind='courier')
        before = deepcopy(world)
        response['events'][0]['message'] = 'edited'
        response['result']['message'] = 'edited'
        detached = snapshot(world)
        detached['player']['cash'] = -1
        detached['people']['Mara Voss']['memory'].clear()
        self.assertEqual(world, before)

    def test_command_envelope_and_event_are_stable(self):
        world = self.world()
        response = execute_command(world, 'job', kind='collection')
        self.assertEqual(response['sequence'], 2)
        command_event = response['events'][-1]
        self.assertEqual(command_event['kind'], 'player_command')
        self.assertEqual(command_event['command_id'], 2)
        self.assertEqual(command_event['actor'], 'player')
        self.assertEqual(command_event['arguments'], {'kind': 'collection'})
        self.assertEqual(command_event['action_cost'], 1)
        self.assertEqual(response['events'], world['events'][-len(response['events']):])

    def test_save_load_cannot_refresh_allowance_or_sequence(self):
        world = self.world()
        for _ in range(3):
            execute_command(world, 'job', kind='courier')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(world, path)
            restored = load_career(path)
        self.assertEqual(restored, world)
        self.assertEqual(actions_remaining(restored), 0)
        with self.assertRaises(ValueError):
            execute_command(restored, 'job', kind='courier')
        advance_day(restored)
        self.assertEqual(restored['command_sequence'], 5)

    def test_low_level_job_resolution_remains_unbounded_and_matches_m010(self):
        world = gameplay.prepare(new_world(42))
        gameplay.join(world, 'Harbor Syndicate')
        fixture = json.loads((Path(__file__).parent / 'fixtures' / 'm010.json').read_text(encoding='utf-8'))
        expected = [e for e in fixture['events'] if e['kind'] == 'job']
        for old in expected:
            self.assertEqual(gameplay.job(world, 'collection'), old)
        for _ in range(10):
            gameplay.job(world, 'courier')
        self.assertEqual(world['job_attempts'], 13)
        self.assertEqual(world['day'], 0)

    def test_seed_types_and_global_rng_isolation(self):
        for seed in (True, '42', 1.5):
            with self.assertRaises(ValueError):
                create_career(seed)
        state = random.getstate()
        world = self.world()
        execute_command(world, 'job', kind='collection')
        advance_day(world)
        self.assertEqual(random.getstate(), state)

    def test_long_running_resume_and_invariants(self):
        a, b = self.world(), self.world()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            for day in range(365):
                for world in (a, b):
                    execute_command(world, 'job', kind='collection' if day % 5 == 0 else 'courier')
                    advance_day(world)
                if day % 73 == 0:
                    save_career(b, path)
                    b = load_career(path)
                    validate(a)
                    validate(b)
            self.assertEqual(a, b)
            self.assertEqual(a['day'], 365)
            self.assertEqual(a['command_sequence'], 731)
            validate(a)

    def test_fresh_process_hashseed_determinism(self):
        code = (
            'import hashlib,json; from game_service import create_career,execute_command,advance_day; '
            'w=create_career(17); execute_command(w,"join",faction="Harbor Syndicate"); '
            '[(execute_command(w,"job",kind="collection"),advance_day(w)) for _ in range(12)]; '
            'print(hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest())'
        )
        digests = []
        for seed in ('0', '1', '42'):
            env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONDONTWRITEBYTECODE='1')
            digests.append(subprocess.check_output([sys.executable, '-B', '-c', code],
                           cwd=Path(__file__).resolve().parents[1], env=env, text=True).strip())
        self.assertEqual(len(set(digests)), 1)

    def test_cli_new_game_refuses_existing_career(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(create_career(), path)
            previous = path.read_bytes()
            with patch('sys.argv', ['gameplay.py', '--save', str(path)]), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    gameplay.main()
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(path.read_bytes(), previous)

    def test_cli_budget_save_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            output = io.StringIO()
            commands = ['join 1'] + ['job courier'] * 4 + ['status', 'save', 'quit']
            with patch('sys.argv', ['gameplay.py', '--save', str(path)]), patch('builtins.input', side_effect=commands), contextlib.redirect_stdout(output):
                gameplay.main()
            self.assertIn('Daily actions exhausted', output.getvalue())
            self.assertIn('Daily actions remaining: 0', output.getvalue())
            self.assertEqual(load_career(path)['job_attempts'], 3)
            with patch('sys.argv', ['gameplay.py', '--load', '--save', str(path)]), patch('builtins.input', side_effect=['wait', 'job courier', 'quit']), contextlib.redirect_stdout(io.StringIO()):
                gameplay.main()
            self.assertEqual(load_career(path)['job_attempts'], 4)
            self.assertTrue(path.with_suffix('.json.bak').exists())

    def test_script_entry_point_uses_the_command_service(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            script = Path(__file__).resolve().parents[1] / 'gameplay.py'
            commands = 'join 1\nmission scout 2\njob courier\njob courier\njob courier\nwait\nintel\nquit\n'
            completed = subprocess.run([sys.executable, '-B', str(script), '--save', str(path)],
                                       cwd=folder, input=commands, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('Daily actions exhausted', completed.stdout)
            self.assertIn('CITY INTELLIGENCE', completed.stdout)
            world = load_career(path)
            self.assertEqual(world['job_attempts'], 2)
            self.assertEqual(world['day'], 1)


if __name__ == '__main__':
    unittest.main()
