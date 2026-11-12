---
name: data-profiling
description: Load, validate and profile the SupeRR data pack (ball_by_ball, matches, competitions, teams, playing_eleven, mapping). Use first, before any modelling, and whenever a number looks odd.
---
# Data profiling & validation

## Steps
1. Load with `pd.read_csv(..., low_memory=False)`. Confirm shapes: ball_by_ball 200,999×33; matches 883×22; competitions 141×4; teams 353×3; playing_eleven 28,381×9; mapping 6,413×6.
2. Run the integrity checks below and save results to `outputs/data_profile.md`.
3. List every deviation as a decision for the human (see "Decisions to surface").

## Schema cheatsheet (ball_by_ball)
`match_id, innings, overid (1–20), over_ball_num, innings_ball_num, batting_team_id, bowling_team_id, striker_id/name, non_striker_id/name,
bowler_id/name, batting_type (RHB/LHB), bowling_type, batting_order, runs, is_four, is_six, is_wicket, dismissal_type_id, dismissal_type,
dismissed_player_id, extras_type, extras1_runs, extras_2_runs, pace_or_spin, bowl_speed, stroke, delivery_style, over_or_around, on_or_off, delivery_ist_time`

## Verified semantics
- `runs`: bat runs only. wide/bye/leg-bye rows have `runs = 0`; no-ball rows keep bat runs; `Overstep` = no-ball.
- `extras_type` values: wide (7,714), legbyes (2,748), Overstep (576), byes (529), other (264), Penalty (1). NaN = no extra.
- `extras1_runs` is a **code**, not runs: 6=none, 2=wide, 3=legbye, 1=Overstep, 4=bye, 5=other, 7=penalty.
- `extras_2_runs` is nonzero in only 36 rows (extra runs on no-ball/other) — add to team runs.
- **Bye/leg-bye runs are absent** (`runs=0`, `extras_2_runs=0`). Team totals are under-counted; default estimate = 1 run per bye/leg-bye delivery.
  Check on "won by N runs" matches: wides+no-balls only → MAE ≈ 4 runs, exact margin ≈ 12%; with the 1-run bye estimate → MAE ≈ 2.6, exact ≈ 25%.
- Legal delivery = not wide and not Overstep. `other` is ambiguous → treated as legal (flag; test sensitivity). A few innings exceed 120 legal balls because of this.
- `innings` ∈ {1,2} for 99.98% of rows; 3/4 are super overs (38 rows / 6 matches).
- `is_wicket` True on 10,881 rows == rows with `dismissal_type`. Types: Caught 7,557; Bowled 1,775; LBW 709; RunOut 600; Stump 214; Hit Wicket 17; Retire Out 6; Obstructing (spelled "Obstracting" in 2 rows) 3.
  One Retire-Out has null `dismissed_player_id`.
- Null counts: stroke 6,158 (3%), delivery_style 391, over_or_around 407.
- `batting_order` in ball_by_ball is the striker's order (1–13); `playing_eleven.batting_order` is NaN for 8,678 non-playing rows.
- `matches.result` is free text with inconsistent case ("Runs"/"runs"), "(D/L method)" variants, "No Result", "Match Abandoned". `win_team_id` is the reliable winner field (NaN for ties/no result).
- `matches.first_inn_revised_overs` / `second_inn_revised_overs` are in **balls** (min 30, max 114). 23 rows have `revised_target`; ~34 matches show some DLS signal.
- `matches.stage`: League 620, Others 226, Final 12, Qualifier 10, Super 4 6, Eliminator 5, Semi Final 4. `knock_out`=1 in 31 matches.
- `matches.match_date` runs 2022-01-22 → 2026-11-01. `venue_id` + `venue_country` only (no venue names).
- competitions: IPL 2022–2026 (comp ids 1358, 1715, 2193, 2725, 3298), plus T20I series 2022–2026 and two non-senior A-team events
  ("Mens T20 Emerging Teams Asia Cup 2024", "Asia Cup Rising Stars 2025") → **decide whether to exclude them**.
- Players: 888 distinct batters, 647 distinct bowlers in ball data; 1,217 in the mapping file.
- Names are not unique keys: `Abdul Samad`, `Basil Hameed`, `Haider Ali` each map to two player_ids. Always group by id; disambiguate by team/competition when displaying.
- `bowl_speed`: sentinels 0 / −1 and impossible values up to 1456 → unusable without cleaning. `delivery_ist_time` is a date at midnight, not a ball timestamp.

## Integrity checks to run (copy into a script)
- every `ball_by_ball.match_id` is in `matches`; the 16 matches without ball data should all be abandoned/no result.
- per (match, innings): legal balls ≤ ~124; wickets ≤ 10; batting_team ≠ bowling_team; innings-2 batting team = innings-1 bowling team.
- chase-win consistency: for matches won by the chasing side by wickets, inn2_total should exceed inn1_total. Un-repaired it fails in ~28% (bye gap) — hence the target repair in `build_ball_state.py`. Report the residual.
- duplicates on (match_id, innings, innings_ball_num).
- player_id ↔ name 1:1 (expect only the 3 known collisions).

## Decisions to surface (do not decide silently)
1. Include/exclude the two non-senior A-team T20 events.
2. Handling of the ~34 DLS-affected matches (default: drop from chase-pressure, keep for unconditional baselines).
3. Bye-run estimate (default 1.0; test 0.8–1.5).
4. Treatment of `other` extras (legal vs not).
5. Include super overs? (default no).
