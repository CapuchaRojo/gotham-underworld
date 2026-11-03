# M009 — Living City Intelligence

Install `city_strategy.py`, `faction_warfare.py`, `gameplay.py`, and `tests/test_city_strategy.py` in the project, replacing existing files where applicable. Requires M008.

Run `python -m unittest discover -s tests -v` and `python gameplay.py --save career_m009_save.json`.

In the CLI, run `strategy`, `wait`, `wait`, `strategy`, `events`, `districts`, `save`, `quit`.

Strategy is a deterministic daily plan. The existing warfare executor applies it only when its day matches the current day; direct calls to M008 warfare without a current plan retain M008 behavior. Existing save files are migrated without replaying old planning days. No external packages required.
