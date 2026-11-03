"""Small deterministic command boundary shared by CLI and future interfaces.

Command identifiers and JSON arguments are independent of character names.
Legacy gameplay reducers remain available for simulation tools and old tests;
player-facing integrations must use this boundary to enforce action allowances.
"""
from copy import deepcopy

import gameplay
from career_state import DAILY_ACTION_ALLOWANCE, validate
from district_missions import mission
from simulation import event, new_world

# Stable command IDs; future commands can reuse the same result/event envelope.
COMMANDS = {
    'join': (0, ('faction',), gameplay.join),
    'job': (1, ('kind',), gameplay.job),
    'mission': (1, ('kind', 'district'), mission),
    'wait': (0, (), gameplay.next_day),
}


def create_career(seed=42):
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    world = gameplay.prepare(new_world(seed))
    validate(world)
    return world


def load_career(filename):
    return gameplay.load(filename)


def save_career(world, filename, *, overwrite=True):
    return gameplay.save(world, filename, overwrite=overwrite)


def snapshot(world):
    """Detached JSON-shaped world; edits cannot affect a running career."""
    return deepcopy(world)


def actions_remaining(world):
    used = world['actions_used'] if world['action_day'] == world['day'] else 0
    return DAILY_ACTION_ALLOWANCE - used


def advance_day(world):
    return execute_command(world, 'wait')


def execute_command(world, command, **arguments):
    """Apply one atomic player command, returning detached results and events.

    Input worlds come from create_career/load_career. Rejections do not initialize
    state, spend actions, consume RNG attempts, or append events. Transactions use
    a private copy; callers retain the root dictionary, not nested live references.
    """
    if not isinstance(command, str) or command not in COMMANDS:
        raise ValueError('Unknown player command')
    cost, names, handler = COMMANDS[command]
    if set(arguments) != set(names) or any(not isinstance(arguments[n], str) for n in names):
        raise ValueError(f'{command} requires string arguments: {", ".join(names) or "none"}')
    if actions_remaining(world) < cost:
        raise ValueError('Daily actions exhausted; use wait')
    candidate = deepcopy(world)
    start = len(candidate['events'])
    if candidate['action_day'] != candidate['day']:
        candidate['action_day'] = candidate['day']
        candidate['actions_used'] = 0
    result = handler(candidate, *(arguments[name] for name in names))
    if command == 'wait':
        candidate['action_day'] = candidate['day']
        candidate['actions_used'] = 0
        result = None
    else:
        candidate['actions_used'] += cost
    candidate['command_sequence'] += 1
    sequence = candidate['command_sequence']
    event(candidate, 'player_command', f'Player command {sequence}: {command}.',
          command=command, command_id=sequence, actor='player',
          arguments=deepcopy(arguments), action_cost=cost, cause='player_command')
    response = deepcopy({'command': command, 'sequence': sequence,
                         'day': candidate['day'], 'result': result,
                         'events': candidate['events'][start:],
                         'actions_remaining': actions_remaining(candidate)})
    world.clear()
    world.update(candidate)
    return response
