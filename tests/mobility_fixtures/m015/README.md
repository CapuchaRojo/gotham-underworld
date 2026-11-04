# Frozen M015 compatibility career

`career.json` was generated using only Python/content files read from audited
commit `3251381177bf11c0b07cd940329ebd0be3a7bb52` in a separate temporary
directory, not the M016-A implementation. Script: create seed42; `settle_in`;
`advance_day`; `travel p032 auto`; serialize world to JSON. It contains active
daily life and a genuine schema1 journey, with no mobility fields. Tests require
unchanged events on load and no implicit adoption. Do not regenerate to mask an
incompatible implementation.
