# M008 — Autonomous Faction Warfare

Install `faction_warfare.py`, replace `gameplay.py`, and add `tests/test_faction_warfare.py` in the project root. Do not replace any other existing files.

Run `python -m unittest discover -s tests -v` (62 tests expected).

Play: `python gameplay.py --save career_m008_save.json`. Inside the game: `districts`, `join 1`, `wait`, `wait`, `districts`, `events`, `save`, `quit`.

Day 1 remains a mobilization day to preserve established M006 first-day economy behavior. Beginning day 2, each faction can spend its treasury on one defense or offensive action daily. An NPC is attributed only when affiliated with the acting faction. Warfare uses no randomness and records all actions as `faction_warfare` events. It does not replace the existing passive economy pressure system.

Commit on `feature/m008-faction-warfare` after local validation, push, open PR, and check CI before merging.
