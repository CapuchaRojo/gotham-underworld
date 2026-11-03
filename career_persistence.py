"""Validated JSON careers with atomic replacement and a previous-good backup."""
import json
import math
import os
from pathlib import Path
import tempfile

from career_state import validate


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Invalid save: duplicate JSON key {key!r}')
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f'Invalid save: non-finite JSON number {value}')


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        _invalid_constant(value)
    return number


def decode(text):
    try:
        world = json.loads(text, object_pairs_hook=_unique_object,
                           parse_constant=_invalid_constant, parse_float=_finite_float)
    except json.JSONDecodeError as exc:
        raise ValueError(f'Invalid save JSON: {exc.msg}') from exc
    return validate(world)


def read(filename):
    try:
        return decode(Path(filename).read_text(encoding='utf-8'))
    except UnicodeError as exc:
        raise ValueError('Invalid save: expected UTF-8 JSON') from exc


def _stage(path, payload):
    """Flush a sibling temporary file before making it visible as a save."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', prefix='.' + path.name + '.',
                                         suffix='.tmp', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        return temporary
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def write(world, filename, *, overwrite=True):
    """Keep filename.bak as the last valid replaced career.

    The original destination is untouched until both staging and backup succeed.
    An invalid existing destination is never allowed to destroy a good backup.
    New-career saves use exclusive creation to protect files appearing mid-session.
    """
    validate(world)
    try:
        payload = (json.dumps(world, indent=2, allow_nan=False) + '\n').encode('utf-8')
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Cannot serialize career: {exc}') from exc
    path = Path(filename)
    temporary = _stage(path, payload)
    backup_temporary = None
    try:
        if not overwrite:
            # Hard-link publication is atomic and cannot replace a competing file.
            os.link(temporary, path)
        else:
            if path.exists():
                previous = path.read_bytes()
                try:
                    decode(previous.decode('utf-8'))
                except (ValueError, UnicodeError) as exc:
                    raise ValueError('Existing career is invalid; restore its .bak or choose a different save path') from exc
                backup = path.with_name(path.name + '.bak')
                backup_temporary = _stage(backup, previous)
                os.replace(backup_temporary, backup)
            os.replace(temporary, path)
        return path
    finally:
        temporary.unlink(missing_ok=True)
        if backup_temporary is not None:
            backup_temporary.unlink(missing_ok=True)
