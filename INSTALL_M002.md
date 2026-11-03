# M002 Player Agency — incremental patch

Copy `gameplay.py` into your existing `gotham_underworld_m001` folder and `tests/test_gameplay.py` into its `tests` folder. Do not replace existing files. Your existing M001.1 `simulation.py` is reused unchanged.

Run `python -m unittest discover -s tests -v` (12 tests total) and `python gameplay.py`.

In the interactive prompt: `help`, `factions`, `join 1`, `jobs`, `job courier`, `job collection`, `wait`, `status`, `events`, `save`, `quit`.

`quit` automatically saves `career_save.json`. Resume using `python gameplay.py --load`. The old `python simulation.py` command still works.

Current scope: deterministic job rewards, basic heat/reputation, NPC memories, and city advancement. Jobs do not yet have risk rolls or evidence generation; faction switching, nuanced arrest, and real-time gameplay remain future milestones.
