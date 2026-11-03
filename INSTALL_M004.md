# M004 — Persistent NPC Relationships

Copy `gameplay.py`, `consequence_engine.py`, `relationship_engine.py`, `tests/test_relationships.py`, and `INSTALL_M004.md` into the project, preserving the `tests/` directory. Do not replace `simulation.py` or existing test files.

Run `python -m unittest discover -s tests -v` (26 tests expected), then `python gameplay.py --save career_m004_save.json`. In-game use `relationships` to view NPC scores and explainable decisions. The relationship engine tracks recruitment, jobs, rival retaliation, and investigation evidence; old saves migrate when loaded. The `offer_support` and `refuse_cooperation` decisions are currently informational policies, not yet NPC-initiated missions or actions. Court timing remains simplified.

On `feature/m004-npc-relationships`, stage the five M004 files, commit, push, open a pull request, and merge only after CI passes.
