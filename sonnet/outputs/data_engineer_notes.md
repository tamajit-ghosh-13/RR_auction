# Data Engineer Stage Notes (`sonnet`)

## What Was Executed
1. Linked the 6 raw CSVs cleanly under `sonnet/data/raw/` without duplicating disk files.
2. Executed `scripts/build_ball_state.py --data data/raw --out data/interim/ball_state.csv.gz --bye-runs 1.0`, producing `200,961` rows across `867` matches.
3. Created `scripts/common.py` exposing `balls_faced`, `legal_balls`, `bowler_runs`, `batter_runs`, `is_striker_dismissed`, `canon_player_ids`, `assign_format_bucket`, and loaders.
4. Created and ran `scripts/stage1_profile.py`, producing `outputs/data_profile.md`, `outputs/ball_state_checks.md`, `outputs/stage1_summary.json`, and initializing `outputs/DECISIONS.md`.

## Key Pitfalls Caught & Handled
- **`extras_type == 'other'` (264 rows)**: Behaves like `Overstep` (no-ball: `extras1_runs=1`, `runs` in `0..6`, `extras_2_runs` in `{0,1,4}`), whereas `build_ball_state.py` leaves `is_legal=True` for `'other'`. Verified and documented as Decision D1b (kept consistent with `build_ball_state.py` primary baseline; noted for sensitivity).
- **`extras1_runs` validity in current CSV**: In this export, `runs + extras1_runs + extras_2_runs` yields 303/303 exact run margins (`MAE = 0.00`), whereas `build_ball_state.py` avoids `extras1_runs` (`bye_runs=1.0` default -> `MAE = 2.17`). We retain `build_ball_state.py` as the documented primary `sonnet` pipeline while running sensitivity checks against `extras1_runs` totals and `target_raw` in Stage 2 & Stage 4.
- **ID collisions vs split IDs**: Confirmed 3 homonym pairs (`Rashid Khan`, `Abdul Samad`, `Haider Ali`) and 4 split-ID pairs (`Bashir Ahmad`, `Basil Hameed`, `Mohammad Ali`, `Muhammad Farooq`). Every downstream stage joins strictly on `player_id`.
- **Emerging T20 competitions (`2670`, `3289`)**: Flagged separately from IPL (`{1358, 1715, 2193, 2725, 3298}`) and senior `T20I`.

## Next Stage Handoff
Ready for Stage 2 (`pressure-modeler`): `data/interim/ball_state.csv.gz` and `scripts/common.py` are verified.
