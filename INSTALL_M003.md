# M003 Consequence Engine v1

On `feature/m003-consequence-engine`, back up your career save before applying. Copy the patch files into your project, preserving the `tests` folder. **Do not replace `simulation.py`**; the patch uses the existing one.

Files to replace: `gameplay.py`, `tests/test_gameplay.py`.
Files to add: `consequence_engine.py`, `tests/test_consequences.py`, `INSTALL_M003.md`.

Run `python -m unittest discover -s tests -v` and `python gameplay.py --save career_m003_save.json`.

M003 outcomes are deterministic for seed, day, attempt number, and job kind. Each job records roll and failure threshold. Witness reports open cases, subsequent days add evidence, and cases reaching threshold are charged and handled by the existing accelerated court mechanic. Failed collection jobs affect faction power and rival reputation. Earlier M001/M002 saves load with defaults. No paid dependencies.

Known limitations: investigations are deliberately simplified and add evidence every day; court resolves immediately on arrest; rival selection is a simple fixed rule; job outcomes are game rules, not real-world legal modeling. Existing M002 `career_save.json` is preserved; use a different save name while testing.
