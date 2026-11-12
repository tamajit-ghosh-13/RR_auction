# AGENTS.md — SupeRR Selector Season 2 (Round 1) Master Agent Blueprint

## 1. Mission & Competition Context
You are an elite Cricket Analytics & Talent Scouting Agent system built for **Rajasthan Royals' SupeRR Selector Season 2 (Round 1)** ahead of the **IPL 2027 Auction**.

- **Core Problem Statement**: Build a transparent, reproducible, data-driven system that measures how batters and bowlers perform in **high-pressure match situations** compared with their **usual (baseline) performance levels**, and identify the players who deliver most consistently when the game is on the line.
- **Required Final Deliverables**:
  1. **Unstop Player Rankings (Dropdown Lists)**:
     - **Top 10 Batters Under Pressure** (ordered Rank 1 to Rank 10, no duplicate players).
     - **Top 10 Bowlers Under Pressure** (ordered Rank 1 to Rank 10, no duplicate players).
     - *Hard Constraint*: Every player selected must exist in `competition_team_player_mapping.csv`, and the dropdown ordering on Unstop must match the Methodology Report 1-for-1.
  2. **Methodology Report (PDF / PPT / Dashboard Document)**:
     - Must explicitly address all five official evaluation pillars:
       1. **Pressure Definition**: Match situations and mathematical indicators used, why they are meaningful, and how they separate pressure situations from ordinary ones for both batting and bowling.
       2. **Performance Measurement**: Batting and bowling metrics, player baseline construction (how a player's pressure performance is compared against their own usual performance and contextual expectation), and rating/scoring logic.
       3. **Fair Comparisons**: Sample size thresholds, Empirical Bayes shrinkage / regularization, player eligibility, match contexts, and relative weighting of IPL vs. T20I (Full Member vs. Associate) data.
       4. **Evidence for Your Top 10**: Concrete tables, visual charts, phase breakdowns, and case-study match moments from the supplied data supporting your Top 10 Batters and Top 10 Bowlers.
       5. **Reliability & Limitations**: Match-to-match consistency checks (e.g., bootstrap confidence intervals, split-half or season-by-season stability, IQR/variance penalties) and transparent discussion of model uncertainty.

---

## 2. Workspace Data Inventory & Exact Schema
All competition data files reside in the project root directory. Never guess column names—use this exact schema map:

| File Name | Rows | Columns | Primary Key / Granularity | Description & Join Keys |
| :--- | :---: | :---: | :--- | :--- |
| `competitions.csv` | 141 | 4 | `comp_id` | `comp_id` (int), `comp_name` (str), `match_format` (`T20` [7 comps] or `T20I` [134 comps]), `season` (`2022` to `2026`, plus `2022/23`, `2023/24`, `2024/25`). |
| `teams.csv` | 353 | 3 | `(comp_id, team_id)` | `comp_id` (int), `team_id` (int), `team_name` (str). Note: `team_id` is unique per franchise/country, repeated per `comp_id`. |
| `matches.csv` | 883 | 22 | `match_id` | Match metadata (`2022-01-22` to `2026-11-01`). Joins to `competitions.csv` via `comp_id`. Note: 867 matches have delivery rows in `ball_by_ball.csv` (16 abandoned/no-ball matches have no BBB rows). |
| `competition_team_player_mapping.csv` | 6,413 | 6 | `(comp_id, team_id, player_id)` | Official roster registry of **1,217 unique `player_id`s**. Columns: `comp_id`, `comp_name`, `team_id`, `team_name`, `player_id`, `player_name`. |
| `playing_eleven.csv` | 28,381 | 9 | `(match_id, team_id, player_id)` | Squad & XI sheet per match. Columns: `match_id`, `team_id`, `player_id`, `batting_order` (float, 1–11), `is_played` (bool), `is_captain` (bool/obj), `is_wk` (bool/obj), `is_impact` (int 0/1), `is_impact_off` (int 0/1). |
| `ball_by_ball.csv` | 200,999 | 33 | `(match_id, innings, innings_ball_num)` | Delivery-level tracking across 867 matches (`innings` 1, 2, plus 38 Super Over balls in `innings` 3 and 4). |

### Full Column Specification for `ball_by_ball.csv` (33 Columns)
- **Identifiers & Ordering**: `match_id` (int), `innings` (int: 1, 2, 3, 4), `overid` (int: 1 to 20, 1-indexed!), `over_ball_num` (int: 1 to 13, 1-indexed delivery counter in over), `innings_ball_num` (int: monotonic delivery counter in innings).
- **Teams & Players**: `batting_team_id` (int), `bowling_team_id` (int), `striker_id` (int), `striker_name` (str), `non_striker_id` (int), `non_striker_name` (str), `bowler_id` (int), `bowler_name` (str).
- **Roles & Handedness**: `batting_type` (`RHB` or `LHB`), `bowling_type` (e.g., `Right-arm fast`, `Slow left-arm orthodox`, `Legbreak googly`), `batting_order` (int: 1 to 11), `pace_or_spin` (`Pace` or `Spin`).
- **Scoring & Wickets**: `runs` (int: runs off the bat, 0–6), `is_four` (bool), `is_six` (bool), `is_wicket` (bool), `dismissal_type_id` (float), `dismissal_type` (str/NaN), `dismissed_player_id` (float/NaN), `extras_type` (str/NaN: `wide`, `legbyes`, `Overstep`, `byes`, `other`, `Penalty`), `extras1_runs` (**TRAP—SEE BELOW**), `extras_2_runs` (int: 0, 1, 4).
- **Ball Tracking & Shot Metadata**: `bowl_speed` (float, km/h), `stroke` (str/NaN), `delivery_style` (str/NaN), `over_or_around` (`Over` or `Around`), `on_or_off` (`Off-side`, `On-side`, `Middle`), `delivery_ist_time` (UTC timestamp string).

---

## 3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE)

> **CRITICAL WARNING**: Any agent or script that ignores these 8 forensic findings will produce silently corrupted totals, wrong required run rates, and invalid player aggregations.

### Trap 1: `extras1_runs` is a Categorical ID (`extras_type_id`), NOT Run Counts!
In `ball_by_ball.csv`, the column `extras1_runs` was exported as the integer foreign key for `extras_type`:
- `extras1_runs == 1` $\rightarrow$ `Overstep` (576 rows)
- `extras1_runs == 2` $\rightarrow$ `wide` (7,714 rows)
- `extras1_runs == 3` $\rightarrow$ `legbyes` (2,748 rows)
- `extras1_runs == 4` $\rightarrow$ `byes` (529 rows)
- `extras1_runs == 5` $\rightarrow$ `other` (264 rows, non-overstep no-ball)
- `extras1_runs == 6` $\rightarrow$ `NaN` / Normal legal delivery (**189,167 rows!**)
- `extras1_runs == 7` $\rightarrow$ `Penalty` (1 row)

**Rule**: **NEVER** sum `extras1_runs`! Doing so adds `+6` runs to every legal ball in the dataset.
- **Batter Runs**: `batter_runs = np.where(extras_type.isin(['wide', 'byes', 'legbyes', 'Penalty']), 0, runs)`
- **Extra Runs on Delivery**: `extra_runs = np.where(extras_type.notna() & (extras_type != 'Penalty'), 1 + extras_2_runs, np.where(extras_type == 'Penalty', 5, 0))`
- **Total Team Runs on Delivery**: `total_runs = batter_runs + extra_runs`
- **Bowler Runs Conceded**: `bowler_runs = batter_runs + np.where(extras_type.isin(['wide', 'Overstep', 'other']), 1 + extras_2_runs, 0)` (byes, legbyes, and penalty runs are not charged to the bowler).

### Trap 2: `over_ball_num` Increments on Wides and No-Balls
`over_ball_num` ranges from `1` to `13` because it counts total deliveries in the over, not legal balls.
- **Legal Ball Flag for Team/Over Count**: `is_legal_ball = ~extras_type.isin(['wide', 'Overstep', 'other', 'Penalty'])`
- **Batter Balls Faced (`is_batter_ball`)**: `is_batter_ball = ~extras_type.isin(['wide', 'Penalty'])` (No-balls (`Overstep`, `other`), `byes`, and `legbyes` count as balls faced by the batter; `wide` does not).
- **Bowler Legal Balls (`is_bowler_ball`)**: `is_bowler_ball = ~extras_type.isin(['wide', 'Overstep', 'other', 'Penalty'])`.
- **Legal Balls Remaining in Innings**: Compute cumulative `is_legal_ball` grouped by `(match_id, innings)` and subtract from `max_balls` (`120`, or `second_inn_revised_overs * 6` / `first_inn_revised_overs * 6` when DLS applies).

### Trap 3: Player Name Homonyms vs. Split Player IDs (7 Collisions)
Never group players by `player_name` alone! However, you must also fix 4 split IDs where the same player was given a second `player_id` in Emerging/A-Team tournaments:
- **3 True Homonyms (Different People — Keep Separate via `player_id`)**:
  - `Rashid Khan`: `4722` (Afghanistan / Gujarat Titans superstar) vs. `20172` (Nepal pacer).
  - `Abdul Samad`: `7446` (India / SRH & LSG finisher) vs. `6922` (Pakistan batter).
  - `Haider Ali`: `7338` (Pakistan batter) vs. `28756` (UAE left-arm spinner).
- **4 Split IDs (Same Person — Canonicalize Before Aggregation)**:
  - `Basil Hameed` (UAE): Map `39444` $\rightarrow$ `8638`
  - `Mohammad Ali` (Pakistan): Map `20229` $\rightarrow$ `3083`
  - `Muhammad Farooq` (UAE): Map `28978` $\rightarrow$ `27373`
  - `Bashir Ahmad` (Afghanistan): Map `39479` $\rightarrow$ `29833`

### Trap 4: Bowler Wicket Attribution & Spelling Typo in `dismissal_type`
`is_wicket == True` (10,881 rows) includes team dismissals that do **not** credit the bowler:
- `RunOut` (600), `Retire Out` (6), `Obstracting the field` (2 — note spelling typo!), `Obstructing the field` (1).
- Also note: 12 rows have `is_wicket == False` but `dismissed_player_id.notna()`, and 1 row has `is_wicket == True` but `dismissed_player_id.isna()`.
- **Rule**:
  - For **Team Wickets Lost** (match state): `is_team_wicket = is_wicket.astype(int)`
  - For **Bowler Wickets Taken**: `is_bowler_wicket = is_wicket & dismissal_type.isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])`
  - For **Batter Dismissed**: `is_batter_out = is_wicket & ~dismissal_type.isin(['Retire Out'])` (attributed to `dismissed_player_id` when non-null, else `striker_id`).

### Trap 5: Competition Quality & Format Heterogeneity (`T20` vs `T20I`)
`competitions.csv` has 7 `T20` tournaments and 134 `T20I` series:
- The 7 `T20` competitions are: **5 IPL seasons** (`comp_id` in `[1358, 1715, 2193, 2725, 3298]` for IPL 2022–2026) PLUS **2 developmental Asian tournaments** (`2670`: *Mens T20 Emerging Teams Asia Cup 2024* and `3289`: *Asia Cup Rising Stars 2025*).
- **Rule**: Do NOT filter IPL using `match_format == 'T20'` alone! Filter IPL explicitly via `comp_id.isin([1358, 1715, 2193, 2725, 3298])`. Moreover, `T20I` includes both Full Member clashes (e.g., India vs Australia, World Cup knockouts) and lower-tier bilateral series. Your competition-difficulty weight $w_{\text{comp}}$ must distinguish **IPL**, **Tier-1 Full Member T20Is / World Cups**, and **Associate / Emerging T20s**.

### Trap 6: Super Overs (`innings` 3 and 4)
`ball_by_ball.csv` contains 25 rows with `innings == 3` and 13 rows with `innings == 4` (Super Overs).
- **Rule**: Keep `innings.isin([1, 2])` for standard 20-over match-state reconstruction, and treat `innings.isin([3, 4])` as maximum-leverage (`Pressure Index = 1.0`) tie-breaker deliveries!

### Trap 7: Rain-Shortened Matches & DLS (`revised_target` / `second_inn_revised_overs`)
In `matches.csv`, 25 matches have `first_inn_revised_overs` / `second_inn_revised_overs` and 23 have `revised_target`.
- **Rule**: In Innings 2, target score is `np.where(revised_target.notna(), revised_target, inn1_total_runs + 1)`, and total scheduled balls uses cricket over-to-ball conversion on `second_inn_revised_overs` when non-null.

### Trap 8: `playing_eleven.csv` Includes Unplayed Bench Squad (`is_played == False`)
Out of 28,381 rows in `playing_eleven.csv`, 8,678 rows have `is_played == False` (and `batting_order` is `NaN`).
- **Rule**: Always filter `playing_eleven[playing_eleven['is_played'] == True]` when computing appearances, role distributions, or Impact Player usage (`is_impact == 1`).

---

## 4. Multi-Agent Architecture & Execution Pipeline

When executing this project locally, coordinate work across the domain skill and three specialized agent workflows:

1. **Skill Reference (`.agents/skills/superr-selector-pressure-analytics/SKILL.md`)**:
   - Load first for mathematical formulas, pressure index equations, empirical Bayes shrinkage, baseline adjustment, and ready-to-run Python code blocks.
2. **Stage 1 — Data Engineering Subagent (`.agents/agents/data-engineering-agent.md` / `.agents/workflows/data-engineering-agent.md`)**:
   - Ingests raw CSVs, applies all 8 forensic fixes, reconstructs exact ball-by-ball state (`score`, `wickets_lost`, `balls_remaining`, `RRR`, `CRR`, `win_prob`, `leverage_index`), tags opposition quality, and saves `deliveries_enriched.parquet` + `player_registry.csv`.
3. **Stage 2 — Pressure & Rating Modeling Subagent (`.agents/agents/pressure-modeling-agent.md` / `.agents/workflows/pressure-modeling-agent.md`)**:
   - Computes continuous and thresholded **Pressure Index** ($P \in [0, 1]$) for every delivery, builds contextual and personal baselines ($\text{Expected}$ vs. $\text{Usual}$ vs. $\text{High-Pressure}$), applies Empirical Bayes shrinkage and competition quality weights, and outputs the final **Top 10 Batters** and **Top 10 Bowlers** with component breakdowns.
4. **Stage 3 — Validation & Report Generation Subagent (`.agents/agents/report-and-validation-agent.md` / `.agents/workflows/report-and-validation-agent.md`)**:
   - Runs bootstrap stability tests, sensitivity checks across pressure thresholds, generates high-resolution charts/tables, verifies Unstop dropdown compliance, and compiles the final **Methodology Report**.

---

## 5. Definition of Done (Verification Checklist)
Before finalizing any submission output, verify:
- [ ] `extras1_runs` was never summed as runs anywhere in the codebase.
- [ ] Canonical ID mapping merged the 4 split player IDs (`39444->8638`, `20229->3083`, `28978->27373`, `39479->29833`) while keeping the 3 homonyms (`Rashid Khan`, `Abdul Samad`, `Haider Ali`) separate by `player_id` and disambiguated by team/country in display labels.
- [ ] Both Top-10 lists contain exactly 10 unique batters and 10 unique bowlers with valid Unstop `player_name` strings from `competition_team_player_mapping.csv`.
- [ ] Every ranked player's pressure performance is explicitly compared against both **(a) their own baseline (usual non-pressure performance)** and **(b) phase/context expectation**.
- [ ] IPL performance and high-tier opposition carry explicit, documented weight so the Top 10 aligns with Rajasthan Royals' IPL 2027 Auction strategy.
