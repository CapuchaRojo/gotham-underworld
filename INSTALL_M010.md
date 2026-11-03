# M010 — City Intelligence Dashboard & Player Influence

Copy `city_intelligence.py`, `gameplay.py`, `tests/test_city_intelligence.py`, and this file into the repository root, preserving `tests/`. Existing saves remain compatible; intelligence reads the existing event history and does not modify the world.

Run: `python -m unittest discover -s tests -v` (expected 86 tests).

Play: `python gameplay.py --save career_m010_save.json`; try `intel`, `briefing`, `join 1`, `mission expand 2`, `wait`, `wait`, `intel`, `briefing 1`, `events`, `save`, `quit`.

`intel` ranks factions, displays event-attributed player influence, and lists up to ten recorded ownership transfers. `briefing [day]` reports events and district income for the selected elapsed day. No external dependencies or AI calls.
