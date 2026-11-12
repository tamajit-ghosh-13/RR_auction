---
name: ball-state-features
description: Build the delivery-level match-state table (score, wickets, legal balls, balls left, target, RRR, CRR, phase, wicket credit) from the raw data. Use after data-profiling and before any pressure modelling.
---
# Ball-state feature table

Run: `python scripts/build_ball_state.py --data data/raw --out data/interim/ball_state.csv.gz [--bye-runs 1]`
(Tested on the pack: 200,961 delivery rows, 867 matches.)

## Columns produced (state is **before** the delivery unless `_after`)
- flags: `is_legal, is_wide, is_noball, is_bye`
- runs: `team_runs` (bat + wide + no-ball + extras_2 + est. byes), `bowler_runs` (bat + wide + no-ball + extras_2; byes/leg-byes not charged to bowler)
- wickets: `is_wkt_team` (any dismissal), `is_wkt_bowler` (excludes RunOut, Retire Out, Obstructing)
- state: `runs_before, wkts_before, wkts_in_hand, legal_before, balls_left, crr, phase` (powerplay ov 1–6 · middle 7–15 · death 16–20)
- chase: `target, target_raw, target_repaired, runs_needed, rrr, rrr_minus_crr, balls_in_innings, dls_flag`
- context: `comp_name, match_format, season, match_date, stage, knock_out, venue_id, venue_country, win_team_id, batting_won`

## Rules & traps
- `target` for innings 2 = inn1_total + 1 (or `revised_target` under DLS). If the chasing side won, target is capped at its own final total (repair).
  ~13% of chase deliveries are touched by the repair; keep `target_raw` and run a ±5-run target-noise sensitivity test.
- `rrr` explodes when `balls_left` is tiny (max 930). Cap RRR (e.g. at 36) or lean on the win-probability model instead of raw RRR.
- `balls_in_innings` uses revised **balls** for DLS chases.
- Never use `innings_ball_num` / `over_ball_num` as legal-ball position.
- Batter "balls faced" = legal deliveries + no-balls faced (wides are not faced). Define once, in one function, reuse everywhere.
- State wickets use all dismissals incl. retire-out; do not reuse `is_wkt_bowler` for state.

## Validate after every rebuild
- totals reproduce `matches.result` margins (see data-profiling); `legal_before` max ≈ 119–123; no negative balls_left.
- save `outputs/ball_state_checks.md` with the numbers.
