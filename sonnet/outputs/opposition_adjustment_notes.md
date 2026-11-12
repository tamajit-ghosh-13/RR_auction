# Format Baselines & Opposition Adjustment Notes (`sonnet`)

## 1. IPL vs T20I vs Emerging Scoring Environments (`outputs/format_baselines.csv`)
Scoring and wicket rates diverge meaningfully across formats:
- **IPL (`367` matches)**: Highest scoring environment — Powerplay Inn 1/2 `8.92 / 9.06 rpo`, Middle `8.59 / 8.71 rpo`, Death `10.92 / 10.26 rpo`; wicket rates `3.82%` (Inn 1 PP) to `7.74%` (Inn 2 Death).
- **T20I (`470` matches)**: Lower scoring and higher wicket hazard — Powerplay Inn 1/2 `8.04 / 8.23 rpo`, Middle `8.03 / 7.95 rpo`, Death `10.07 / 9.22 rpo`; wicket rates `4.54%` (Inn 1 PP) to `8.90%` (Inn 2 Death).
- **Emerging/A-Team T20 (`30` matches, `2670` & `3289`)**: Notably lower middle-overs scoring (`6.76 / 7.14 rpo`) and higher Inn 1 death wicket rate (`9.18%`); excluded from senior IPL+T20I rankings to avoid skewing sample counts and opponent strength.

Treating IPL and T20I without format-specific baselines over-credits IPL strike rates by `+0.8–1.0 rpo` relative to T20Is and penalizes IPL bowlers relative to T20I bowlers. Our Stage 3 expectation model explicitly conditions on `fmt`, `innings`, `phase`, `over_idx`, `balls_left`, `wkts_in_hand`, `crr`, `rrr`, `venue_country`, `pace_or_spin`, `bowling_type`, `batting_type`, and `season` via 5-fold match-grouped Ridge regression.

## 2. Joint Context + Batter + Bowler Opposition Adjustment
- Fitted out-of-fold (`GroupKFold(5, match_id)`) sparse Ridge (`alpha = 150` for runs, `alpha = 250` for wickets) over `189,555` clean IPL + T20I deliveries: `outcome ~ context_features + striker_id + bowler_id`.
- Opponent quality standard deviations:
  - Opponent bowler run-suppression effect on balls faced: `std = 0.0954 runs/ball` (~`9.5 runs per 100 balls` spread between elite death bowlers and replacement bowlers).
  - Opponent batter run-scoring effect faced by bowlers: `std = 0.1101 runs/ball` (~`2.6 runs per 24 balls` spread).
- Context-only baseline calibration check: `x_bat_runs_ctx mean = 1.3960` vs observed `1.3974`; `x_bwl_runs_ctx mean = 1.3854` vs observed `1.3855`.
- Stage 4 checks correlation between unadjusted (`context-only`) and opposition-adjusted (`+ opp_effect`) rankings.
