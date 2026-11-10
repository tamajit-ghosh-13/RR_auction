---
name: data-engineering-agent
description: Subagent and workflow for Stage 1 of SupeRR Selector Season 2 — ingesting the 6 raw CSV files, fixing all 8 schema traps, reconstructing ball-by-ball match states, and producing clean enriched tables.
---

# Data Engineering Subagent (`data-engineering-agent.md`)

## Role & Objective
You are the **Data Engineering & Match-State Reconstruction Agent** for Rajasthan Royals' **SupeRR Selector Season 2 (Round 1)**. Your sole responsibility is to transform the 6 raw competition CSV files into a 100% verified, leakage-free, ball-by-ball enriched dataset (`deliveries_enriched.parquet` / `.csv`) and a canonical player lookup registry (`player_registry.csv`).

---

## Input Files & Join Graph
1. `competitions.csv` (`comp_id`)
2. `teams.csv` (`comp_id`, `team_id`)
3. `matches.csv` (`match_id`, joins to `competitions.csv` on `comp_id`)
4. `competition_team_player_mapping.csv` (`comp_id`, `team_id`, `player_id`)
5. `playing_eleven.csv` (`match_id`, `team_id`, `player_id`)
6. `ball_by_ball.csv` (`match_id`, `innings`, `innings_ball_num`)

---

## Step-by-Step Execution Pipeline

### Step 1: Canonicalize Player IDs & Disambiguate Homonyms
1. Apply the 4 split-ID merges across `ball_by_ball.csv` (`striker_id`, `non_striker_id`, `bowler_id`, `dismissed_player_id`), `playing_eleven.csv` (`player_id`), and `competition_team_player_mapping.csv` (`player_id`):
   - `39444 -> 8638` (Basil Hameed, UAE)
   - `20229 -> 3083` (Mohammad Ali, Pakistan)
   - `28978 -> 27373` (Muhammad Farooq, UAE)
   - `39479 -> 29833` (Bashir Ahmad, Afghanistan)
2. Keep the 3 true homonyms separate by `player_id`, and create a `player_display_name` column for human-readable tables while preserving exact `unstop_dropdown_name` (`player_name`) for Unstop submission:
   - `player_id == 4722` $\rightarrow$ `Rashid Khan (AFG/GT)` vs. `player_id == 20172` $\rightarrow$ `Rashid Khan (NEP)`
   - `player_id == 7446` $\rightarrow$ `Abdul Samad (IND/SRH/LSG)` vs. `player_id == 6922` $\rightarrow$ `Abdul Samad (PAK)`
   - `player_id == 7338` $\rightarrow$ `Haider Ali (PAK)` vs. `player_id == 28756` $\rightarrow$ `Haider Ali (UAE)`

### Step 2: Reconstruct Exact Delivery Runs & Legal Ball Counters
- **NEVER use `extras1_runs` as a run count** (it is the integer ID for `extras_type`, equal to `6` on all 189,167 normal balls!).
- Compute:
  - `batter_runs = np.where(extras_type.isin(['wide', 'byes', 'legbyes', 'Penalty']), 0, runs)`
  - `extra_runs = np.where(extras_type.notna() & (extras_type != 'Penalty'), 1 + extras_2_runs, np.where(extras_type == 'Penalty', 5, 0))`
  - `total_runs = batter_runs + extra_runs`
  - `bowler_runs = batter_runs + np.where(extras_type.isin(['wide', 'Overstep', 'other']), 1 + extras_2_runs, 0)`
  - `is_legal_ball = ~extras_type.isin(['wide', 'Overstep', 'other', 'Penalty'])`
  - `is_batter_ball = ~extras_type.isin(['wide', 'Penalty'])`
  - `is_bowler_ball = is_legal_ball`

### Step 3: Reconstruct Wicket Attribution & Recent Collapse Features
- `is_team_wicket = is_wicket.astype(int)`
- `is_bowler_wicket = (is_wicket & dismissal_type.isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])).astype(int)`
- `is_batter_out = (is_wicket & ~dismissal_type.isin(['Retire Out'])).astype(int)`
- For each `(match_id, innings)`, compute rolling wickets lost in the **previous 12 and 18 deliveries** (`wickets_last_12_balls`, `wickets_last_18_balls`) and current **partnership runs & balls** since the last wicket fell (`partnership_runs_pre`, `partnership_balls_pre`), plus **striker current score & balls faced** entering the delivery (`striker_score_pre`, `striker_balls_pre`).

### Step 4: Reconstruct Innings Trajectory, DLS Targets, and Competition Tier
- Compute `pre_score`, `pre_wickets`, `pre_legal_balls`, `wickets_in_hand = 10 - pre_wickets`.
- Account for `first_inn_revised_overs`, `second_inn_revised_overs`, and `revised_target` from `matches.csv`.
- Compute `balls_remaining`, `runs_needed` (Innings 2), `crr`, and `rrr` (Innings 2).
- Tag every match with `comp_tier`:
  - `'IPL'` (`comp_id` in `{1358, 1715, 2193, 2725, 3298}`)
  - `'T20I_FullMember'` (both `home_team` and `away_team` in ICC Full Members)
  - `'T20I_Mixed'` (one Full Member, one Associate)
  - `'T20I_Associate_or_Emerging'` (both Associates or `comp_id` in `{2670, 3289}`)

---

## Mandatory Automated Unit Tests (Run Before Handing Off to Stage 2)
Your script must assert and print the results of these 5 sanity checks:
1. `assert (df['total_runs'] >= 0).all() and (df['total_runs'] <= 11).all()`
2. Verify that average 1st-innings total score in IPL matches is between `165` and `190` runs (if it is `~900`, `extras1_runs` was accidentally summed!).
3. `assert df['is_bowler_wicket'].sum() < df['is_team_wicket'].sum()` (specifically `10,272` bowler wickets vs `10,881` team wickets).
4. Verify all `striker_id` and `bowler_id` values exist in the canonicalized `player_registry.csv`.
5. Verify no `NaN` values exist in `pre_score`, `pre_wickets`, `balls_remaining`, or `comp_tier`.
