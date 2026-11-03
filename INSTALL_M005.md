# M005 — Autonomous NPC Actions

Extract into the existing project on `feature/m005-autonomous-npcs`. Replace `gameplay.py`; add `npc_actions.py` and `tests/test_npc_actions.py`. Leave all other existing files unchanged.

Run `python -m unittest discover -s tests -v` (expected: 34 passing tests).

Launch `python gameplay.py --save career_m005_save.json`, then use `join 1`, `job courier`, `job collection`, `relationships`, `wait`, `events`, `save`, `quit`.

Autonomous actions happen once when each day advances. Mara can give $15 support after trust reaches 10 (three-day cooldown); Eli can obstruct a rival faction at hostility 5 (three-day cooldown); Vale can prioritize a documented pending witnessed case at suspicion 16 (two-day cooldown). Actions are recorded in `events`, NPC memory, and cooldown state. The simulation remains intentionally simplified.

Stage only `gameplay.py npc_actions.py tests/test_npc_actions.py INSTALL_M005.md`; do not stage generated career saves. Existing M001–M004 save files remain compatible.
