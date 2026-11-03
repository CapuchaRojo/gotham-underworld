# M013 faction campaign audit

Executed with Python 3.14.2 on Windows using `python -B faction_campaigns.py`.
The default command runs seeds 1, 17, 42, and 99 for 365 days and seed 42 for
1,000 days. No player interventions, state edits, or outcome-balancing rules
are used. The audit calls the same daily reducer as `wait`, without interface
transaction copies or command-envelope events. A regression verifies equivalent
faction effects through the command service.

An organization is **active** here if it performs a non-hold operation in its
last 30 days. Displaced means zero districts, not eliminated. Sole-lead days
exclude ties on district holdings.

| Seed | Days | Harbor districts | Carnival districts | Iron districts | Transfers | Active | Bound violations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 365 | 1 | 0 | 2 | 5 | 3/3 | 0 |
| 17 | 365 | 1 | 0 | 2 | 4 | 3/3 | 0 |
| 42 | 365 | 1 | 0 | 2 | 5 | 3/3 | 0 |
| 99 | 365 | 0 | 0 | 3 | 4 | 3/3 | 0 |
| 42 | 1000 | 2 | 1 | 0 | 9 | 3/3 | 0 |

Iron Mask led all four one-year samples, holding two districts in three runs
and all three in seed 99. Its defensive/recruitment profile has a clear early
advantage in these samples. This is an observed imbalance, not a test assertion.
By day 1,000 in seed 42, Harbor instead held two districts, Carnival one, and
Iron was displaced. That demonstrates a leadership change in this seed, not
a guarantee of eventual turnover in every campaign.

All three organizations continued operations in every sample. Displaced factions
retained resources and launched paid offensives. No campaign produced negative
cash, power outside 0–100, or newly generated reserves above profile caps.
Tests enforce those invariants and credible recovery; they do not require equal
territory, a particular winner, or a minimum number of transfers.

## Endpoint resources and recent operations

| Seed / days | Faction | Cash | Power | Last 30 days | Sole-lead days |
| --- | --- | --- | --- | --- | --- |
| 1 / 365 | Carnival Crew | $26 | 100 | attack: 1, defend: 11, recover: 18 | 0 |
| 1 / 365 | Harbor Syndicate | $17 | 95 | attack: 4, defend: 4, recover: 22 | 0 |
| 1 / 365 | Iron Mask Outfit | $41 | 100 | attack: 3, defend: 12, recover: 15 | 309 |
| 17 / 365 | Carnival Crew | $18 | 99 | attack: 9, recover: 21 | 0 |
| 17 / 365 | Harbor Syndicate | $34 | 100 | attack: 3, defend: 6, recover: 21 | 49 |
| 17 / 365 | Iron Mask Outfit | $8 | 34 | defend: 25, recover: 5 | 270 |
| 42 / 365 | Carnival Crew | $22 | 99 | attack: 9, recover: 21 | 0 |
| 42 / 365 | Harbor Syndicate | $24 | 100 | attack: 5, defend: 5, recover: 20 | 62 |
| 42 / 365 | Iron Mask Outfit | $38 | 32 | defend: 29, regroup: 1 | 236 |
| 99 / 365 | Carnival Crew | $24 | 99 | attack: 8, recover: 22 | 0 |
| 99 / 365 | Harbor Syndicate | $39 | 100 | attack: 5, recover: 25 | 55 |
| 99 / 365 | Iron Mask Outfit | $52 | 47 | defend: 30 | 250 |
| 42 / 1000 | Carnival Crew | $10 | 100 | attack: 2, defend: 11, recover: 17 | 0 |
| 42 / 1000 | Harbor Syndicate | $41 | 100 | attack: 2, defend: 14, recover: 14 | 679 |
| 42 / 1000 | Iron Mask Outfit | $37 | 99 | attack: 2, recover: 28 | 254 |

## Limits

The three-district map and fixed wealth constrain strategic variety. Power is
an abstract readiness score and often reaches its cap during recovery; it does
not represent individually simulated members or combat. Strong defense can
keep districts stable despite repeated raids. Recovery income represents time
spent rebuilding an off-map network, is capped, and consumes that faction’s
operation for the day. No elimination mechanic is required by the default
profiles because every configured participant can rebuild.
The retained legacy feud sampler covers the three original gangs; additional
economic bindings participate in the new economy and warfare, not that sampler.

Four one-year seeds and one long seed do not establish universal balance.
Profile values are explicit tuning choices for human review; no balancing
handicap or catch-up grant is selected from faction rank.

## Reproducibility fingerprints

- Seed 1, 365 days: `ede9597947410d5ddccf680d5331bcc0902da25e420f8505d5ad2602a997ceb5`
- Seed 17, 365 days: `4113d76575a2af7de51adf7c2169b0901289b3424ebd858d1e85eea71438cf10`
- Seed 42, 365 days: `bd2ae8f39b68ff030d9c554207f80a2ca560fb426c8a7715cec9aaf694cfcda4`
- Seed 99, 365 days: `ae28387d7da7b7b91fc50429faf999c08ace3a569d13610fc82d13d77707c09c`
- Seed 42, 1000 days: `dc1474cf169a667a920d4823818cd768a5641314dd32e54f8496048a4146f3f0`
