# Graph Report - RR_auction_strategy  (2026-11-12)

## Corpus Check
- 61 files · ~46,267 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 25 file(s) not represented in the graph (top: .csv 21, (none) 2, .parquet 2)
- WARNING: 25 of 100 files seen (25%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 392 nodes · 560 edges · 43 communities (27 shown, 16 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a54e1387`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pressure & Rating Modeling
- stage3_ratings.py
- SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics
- SupeRR Selector Always-On Rules
- pandas
- SupeRR Selector Season 2 (Round 1) — Methodology Report
- Top 10 Batters
- stage2_pressure.py
- 3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE)
- SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`)
- Sensitivity & Verification Protocol
- Baselines, shrinkage, eligibility
- Data profiling & validation
- Stage 2 — Pressure Definition (`sonnet`)
- SupeRR Selector Season 2 — Round 1 (Rajasthan Royals × Unstop)
- Batting under pressure
- Bowling under pressure
- Defining pressure (the heart of Round 1 — the human decides)
- Final ranking & reliability checks
- Ball-state feature table
- Methodology report
- Stage 1 — Data Profile (`sonnet`)
- Decisions Log (`sonnet` Pipeline)
- IPL vs T20I fairness
- Stage 1 — Ball-State Checks (`sonnet`)
- Data Engineer Stage Notes (`sonnet`)
- Shrinkage & Eligibility Specification (`sonnet`)
- Format Baselines & Opposition Adjustment Notes (`sonnet`)
- Robustness & Stability Notes (`sonnet`)
- orchestrator.md
- Batting & Bowling Analysts Stage Notes (`sonnet`)
- Pressure Modeler Stage Notes (`sonnet`)
- Validator Stage Notes (`sonnet`)
- submission-checklist/SKILL.md
- batting_top10.md
- bowling_top10.md
- submission_checklist.md
- sonnet/README.md

## God Nodes (most connected - your core abstractions)
1. `bowler_runs()` - 14 edges
2. `assign_format_bucket()` - 13 edges
3. `SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics` - 13 edges
4. `balls_faced()` - 12 edges
5. `legal_balls()` - 12 edges
6. `main()` - 12 edges
7. `fit_expected_and_opposition_models()` - 12 edges
8. `Top 10 Batters` - 11 edges
9. `Top 10 Bowlers` - 11 edges
10. `batter_runs()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Columns produced (state is **before** the delivery unless `_after`)` --references--> `bowler_runs()`  [INFERRED]
  sonnet/.claude/skills/ball-state-features/SKILL.md → sonnet/scripts/common.py
- `Per-delivery building blocks` --references--> `bowler_runs()`  [INFERRED]
  sonnet/.claude/skills/bowling-pressure-metrics/SKILL.md → sonnet/scripts/common.py
- `1. Output Summary & Row Accounting` --references--> `balls_faced()`  [INFERRED]
  sonnet/outputs/ball_state_checks.md → sonnet/scripts/common.py
- `What Was Executed` --references--> `balls_faced()`  [INFERRED]
  sonnet/outputs/data_engineer_notes.md → sonnet/scripts/common.py
- `1. Output Summary & Row Accounting` --references--> `legal_balls()`  [INFERRED]
  sonnet/outputs/ball_state_checks.md → sonnet/scripts/common.py

## Import Cycles
- None detected.

## Communities (43 total, 16 thin omitted)

### Community 0 - "Pressure & Rating Modeling"
Cohesion: 0.08
Nodes (27): deliveries_enriched.parquet Target Table, Match-State Reconstruction Pipeline Steps, player_registry.csv Canonical Registry, Data Engineering Agent Specification, Pressure Reliability Rating Composite Model, Role-Specific Pressure Construction, Pressure & Rating Modeling Agent Specification, Stage 2 Modeling Artifacts Suite (+19 more)

### Community 1 - "stage3_ratings.py"
Cohesion: 0.12
Nodes (16): 1. Output Summary & Row Accounting, What Was Executed, assign_format_bucket(), balls_faced(), batter_runs(), bowler_runs(), canon_player_ids(), is_any_dismissal_of_batter() (+8 more)

### Community 2 - "SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics"
Cohesion: 0.06
Nodes (32): 10. Quickstart & Reproduction Guide, 1. Executive Summary & Official Unstop Dropdown Rankings, 2. The 8 Forensic Dataset Traps & Data Hygiene, 3. Multi-Agent Architecture, 4.1 Win Probability & Leverage Calibration, 4.2 The Five Core Pressure Dimensions, 4.3 Role-Specific Pressure Indices (BPI & BoPI), 4.4 Dual-Baseline Architecture & Dynamic Wicket Valuation (+24 more)

### Community 4 - "pandas"
Cohesion: 0.08
Nodes (16): convert_cricket_overs_to_balls(), run_stage1_pipeline(), run_stage2_pipeline(), run_stage3_pipeline(), build(), anova_shrinkage_k(), build_batting_ratings(), build_bowling_ratings() (+8 more)

### Community 5 - "SupeRR Selector Season 2 (Round 1) — Methodology Report"
Cohesion: 0.06
Nodes (30): 1.1 Why Standard Metrics Fail to Measure Pressure, 1.2 Mathematical Formulation of the 5 Pressure Dimensions, 1.3 Composite Role Indices: BPI & BoPI, 1.4 Empirical Proof of Pressure Separation, 2.1 Contextual Par Expectation ($\text{xRuns}$ and $\text{xWickets}$), 2.2 Ball-Level Net Value Added, 2.3 The Dual-Baseline Comparison, 2.4 Pressure Reliability Rating (PRR) Composite Formulation (+22 more)

### Community 6 - "Top 10 Batters"
Cohesion: 0.08
Nodes (23): #10 Rashid Khan (`player_id=4722`, CI=Borderline (8-14), P(Top10)=39.5%), #10 Sai Sudharsan (`player_id=23450`, CI=Borderline (8-14), P(Top10)=49.7%), #1 Josh Hazlewood (`player_id=830`, CI=Likely Top 10, P(Top10)=85.9%), #1 Rinku Singh (`player_id=4708`, CI=Lock Top 10, P(Top10)=97.9%), #2 Krunal Pandya (`player_id=4219`, CI=Likely Top 10, P(Top10)=80.6%), #2 Yashasvi Jaiswal (`player_id=6819`, CI=Likely Top 10, P(Top10)=89.4%), #3 Abhishek Sharma (`player_id=6281`, CI=Lock Top 10, P(Top10)=90.0%), #3 Harshit Rana (`player_id=29888`, CI=Borderline (8-14), P(Top10)=63.4%) (+15 more)

### Community 7 - "stage2_pressure.py"
Cohesion: 0.13
Nodes (5): compute_expected_li(), compute_lens_b(), fit_oof_wp(), main(), prepare_features()

### Community 8 - "3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE)"
Cohesion: 0.12
Nodes (15): 1. Mission & Competition Context, 2. Workspace Data Inventory & Exact Schema, 3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE), 4. Multi-Agent Architecture & Execution Pipeline, 5. Definition of Done (Verification Checklist), AGENTS.md — SupeRR Selector Season 2 (Round 1) Master Agent Blueprint, Full Column Specification for `ball_by_ball.csv` (33 Columns), Trap 1: `extras1_runs` is a Categorical ID (`extras_type_id`), NOT Run Counts! (+7 more)

### Community 9 - "SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`)"
Cohesion: 0.18
Nodes (10): 0. Executive Summary, 1. Defining Pressure — Win Probability Leverage Index (`LI`), 2. Data Discipline, Context Baselines & Fairness Across IPL vs T20I, 3. Four-Pillar Performance Scoring, Empirical Bayes Shrinkage & Eligibility, 4. Final Top 10 Batters & Top 10 Bowlers Under Pressure, 5. Robustness, Limitations & Open Decision Gates, 6. Reproducibility Appendix, SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`) (+2 more)

### Community 11 - "Baselines, shrinkage, eligibility"
Cohesion: 0.29
Nodes (6): 1. Two baselines (use both, name them clearly), 2. Shrinkage (mandatory), 3. Eligibility (decide from the data, then fix and document), 4. Recency & role, 5. Exposure sanity, Baselines, shrinkage, eligibility

### Community 12 - "Data profiling & validation"
Cohesion: 0.29
Nodes (6): Data profiling & validation, Decisions to surface (do not decide silently), Integrity checks to run (copy into a script), Schema cheatsheet (ball_by_ball), Steps, Verified semantics

### Community 13 - "Stage 2 — Pressure Definition (`sonnet`)"
Cohesion: 0.29
Nodes (6): 1. Lens A: Win Probability & Ex-Ante Expected Leverage Index (`LI = E[|ΔWP|]`), 2. Lens B: Transparent Cricket-Logic Index & Agreement Test, 3. Behavioral Separation & Format Distribution, Expected Leverage Index (`LI`) & Discrete Tiers, Stage 2 — Pressure Definition (`sonnet`), Win Probability Calibration (5-Fold `GroupKFold(match_id)` OOF)

### Community 14 - "SupeRR Selector Season 2 — Round 1 (Rajasthan Royals × Unstop)"
Cohesion: 0.33
Nodes (5): Data pack (verified facts — trust these over assumptions), Non-negotiable rules (from the organisers), Repo layout, SupeRR Selector Season 2 — Round 1 (Rajasthan Royals × Unstop), Working style

### Community 15 - "Batting under pressure"
Cohesion: 0.33
Nodes (5): Batting under pressure, Metrics (per batter, pressure balls only unless stated), Per-delivery building blocks, Pitfalls, Suggested rating (human to confirm weights)

### Community 16 - "Bowling under pressure"
Cohesion: 0.33
Nodes (5): Bowling under pressure, Metrics (pressure balls, per bowler), Per-delivery building blocks, Pitfalls, Suggested rating (human to confirm weights)

### Community 17 - "Defining pressure (the heart of Round 1 — the human decides)"
Cohesion: 0.33
Nodes (5): Defining pressure (the heart of Round 1 — the human decides), One situation, two perspectives, Pitfalls, Prove it separates pressure from ordinary play (goes in the report), Recommended design: two lenses that must agree

### Community 18 - "Final ranking & reliability checks"
Cohesion: 0.33
Nodes (5): Build the ranking, Final ranking & reliability checks, Mandatory robustness suite (report each as a table/figure), Presenting uncertainty, Sanity audits (read, don't just trust the numbers)

### Community 19 - "Ball-state feature table"
Cohesion: 0.40
Nodes (4): Ball-state feature table, Columns produced (state is **before** the delivery unless `_after`), Rules & traps, Validate after every rebuild

### Community 20 - "Methodology report"
Cohesion: 0.40
Nodes (4): Figures that earn their place, Methodology report, Outline (map 1:1 to the brief's five required sections), Writing rules

### Community 21 - "Stage 1 — Data Profile (`sonnet`)"
Cohesion: 0.40
Nodes (4): 1. Table Shapes & Coverage, 2. Competition & Format Breakdown (`ball_state`, 867 matches), 3. Data Integrity & Traps Checked, Stage 1 — Data Profile (`sonnet`)

### Community 22 - "Decisions Log (`sonnet` Pipeline)"
Cohesion: 0.40
Nodes (4): Decisions Log (`sonnet` Pipeline), Stage 1 — Data Engineering & Profiling (`data-engineer`), Stage 2 — Pressure Definition (`pressure-modeler`), Stage 3 — Analyst Metrics, Shrinkage & Eligibility (`batting-analyst`, `bowling-analyst`)

### Community 23 - "IPL vs T20I fairness"
Cohesion: 0.50
Nodes (3): Approach (recommended), Checks, IPL vs T20I fairness

### Community 24 - "Stage 1 — Ball-State Checks (`sonnet`)"
Cohesion: 0.50
Nodes (3): 2. Target Reconstruction & Repair Diagnostics (2nd Innings, Non-DLS), 3. RRR & Boundary Edge Cases, Stage 1 — Ball-State Checks (`sonnet`)

### Community 25 - "Data Engineer Stage Notes (`sonnet`)"
Cohesion: 0.50
Nodes (3): Data Engineer Stage Notes (`sonnet`), Key Pitfalls Caught & Handled, Next Stage Handoff

### Community 26 - "Shrinkage & Eligibility Specification (`sonnet`)"
Cohesion: 0.50
Nodes (3): 1. Empirical Bayes Shrinkage Parameters (`outputs/shrinkage_params.json`), 2. Eligibility Thresholds & Recent Activity Curve (`outputs/eligibility_scan.csv`), Shrinkage & Eligibility Specification (`sonnet`)

### Community 27 - "Format Baselines & Opposition Adjustment Notes (`sonnet`)"
Cohesion: 0.50
Nodes (3): 1. IPL vs T20I vs Emerging Scoring Environments (`outputs/format_baselines.csv`), 2. Joint Context + Batter + Bowler Opposition Adjustment, Format Baselines & Opposition Adjustment Notes (`sonnet`)

### Community 28 - "Robustness & Stability Notes (`sonnet`)"
Cohesion: 0.50
Nodes (3): 1. 1,000-Match Cluster Bootstrap Tiers, 2. Structural Stress Tests (`outputs/robustness_summary.csv`), Robustness & Stability Notes (`sonnet`)

## Knowledge Gaps
- **9 isolated node(s):** `Win Probability & Leverage Index Calibration`, `Bowling Pressure Index (BoPI)`, `Empirical Bayes Shrinkage Regularization`, `Five-Section Methodology Report Architecture`, `Robustness & Sensitivity Verification Suite` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 250 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `bowler_runs()` connect `stage3_ratings.py` to `Bowling under pressure`, `Ball-state feature table`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `bowler_runs()` (e.g. with `data-engineer.md` and `Columns produced (state is **before** the delivery unless `_after`)`) actually correct?**
  _`bowler_runs()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Win Probability & Leverage Index Calibration`, `Bowling Pressure Index (BoPI)`, `Empirical Bayes Shrinkage Regularization` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pressure & Rating Modeling` be split into smaller, more focused modules?**
  _Cohesion score 0.08143939393939394 - nodes in this community are weakly interconnected._
- **Why does `Per-delivery building blocks` connect `Bowling under pressure` to `stage3_ratings.py`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Should `stage3_ratings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1173054587688734 - nodes in this community are weakly interconnected._
- **Why does `fit_expected_and_opposition_models()` connect `stage3_ratings.py` to `pandas`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._