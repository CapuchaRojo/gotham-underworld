# Gotham Underworld — Milestone 001

A zero-cost, original-IP **terminal simulation** proving event logging, NPC memory, autonomous gang feuds, evidence, arrests, court outcomes, accelerated incarceration, and JSON saves.

This is a **prototype**, not a playable 3D game. All characters and factions in the executable are original placeholders; DC characters belong in a separate private creative reference.

## Windows quick start

1. Install Python 3.14 from https://www.python.org/downloads/windows/
2. Extract this ZIP to `Documents\GothamUnderworld`.
3. Open PowerShell in the extracted `gotham_underworld_m001` directory (Shift+right-click in Explorer → Open in Terminal).
4. Run `python simulation.py --days 10 --seed 42` (or `py simulation.py --days 10 --seed 42`).
5. Run `python -m unittest discover -s tests -v` to run tests.
6. Inspect `world_save.json` in VS Code to see event records and memories.

No `pip install` or internet connection required after Python installation.

## Parameters

- `--days 10`: number of simulated days; the court process may advance time further.
- `--seed 42`: deterministic seed.
- `--no-crime`: observe gang feuds without player crime.
- `--save custom.json`: output filename.

## Known limitations

- Fixed scripted player crime, no interactive choices yet.
- Evidence accumulation and sentencing are intentionally simplified; not a realistic court simulator.
- No graphical world, dialogue AI, character combat, economy balancing, or genuine prison gameplay yet.
- Every run starts a fresh world; JSON saves are inspectable but not yet reloadable.

## Next milestone

Add an interactive command loop, player faction affiliation, differentiated witnesses and investigation probabilities, and loading saved games. Keep deterministic tests.
