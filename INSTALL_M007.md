# M007 — District Missions and Faction Expansion

Extract these files into the project root on `feature/m007-district-missions`, preserving the `tests/` folder. Replace `gameplay.py`.

PowerShell:

```powershell
python -m unittest discover -s tests -v
python gameplay.py --save career_m007_save.json
```

In the game: `districts`, `missions`, `join 1`, `mission scout 2`, `wait`, `mission expand 2`, `districts`, `events`, `save`, `quit`.

Rules: One district mission per game day; scouting costs $5 and stores intel; fortifying costs $15 and adds up to 8 control to owned territory; expanding costs $30 and removes up to 12 control from rival territory, capturing it at zero. Missions are deterministic and save-compatible. They do not alter existing job random rolls.

After local tests pass, commit `gameplay.py`, `district_missions.py`, `tests/test_district_missions.py`, `INSTALL_M007.md`, push, and open a PR. Wait for green CI before merging.
