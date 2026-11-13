# Graph Report - RR_auction_strategy  (2026-11-13)

## Corpus Check
- 65 files · ~53,063 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 63 file(s) not represented in the graph (top: .csv 59, (none) 2, .parquet 2)
- WARNING: 63 of 142 files seen (44%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 426 nodes · 660 edges · 46 communities (27 shown, 19 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5b6a569f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pressure & Rating Modeling
- stage3_ratings.py
- SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics
- SupeRR Selector Always-On Rules
- numpy
- SupeRR Selector Season 2 (Round 1) — Methodology Report
- Top 10 Batters
- stage1_data_engineering.py
- 3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE)
- SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`)
- Sensitivity & Verification Protocol
- Baselines, shrinkage, eligibility
- Data profiling & validation
- Stage 2 — Pressure Definition (`sonnet`)
- SupeRR Selector Season 2 — Round 1 (Rajasthan Royals × Unstop)
- Batting under pressure
- match_cluster_bootstrap
- Defining pressure (the heart of Round 1 — the human decides)
- Final ranking & reliability checks
- Bowling under pressure
- Methodology report
- Stage 1 — Data Profile (`sonnet`)
- Decisions Log (`sonnet` Pipeline)
- IPL vs T20I fairness
- Ball-state feature table
- Shrinkage & Eligibility Specification (`C03` Primary: `D1 = bye1_repaired`, `LI >= 75th pct`)
- Format Baselines & Opposition Adjustment Notes (`sonnet`)
- Robustness & Stability Notes (`sonnet`)
- orchestrator.md
- Batting & Bowling Analysts Stage Notes (`sonnet`)
- Pressure Modeler Stage Notes (`sonnet`)
- Validator Stage Notes (`sonnet`)
- submission-checklist/SKILL.md
- Top 10 Batters Under Pressure — 5-Pillar Architecture (`C03` Primary, `D1 = bye1_repaired`)
- Top 10 Bowlers Under Pressure — 5-Pillar Architecture (`C03` Primary, `D1 = bye1_repaired`)
- submission_checklist.md
- sonnet/README.md
- Gate Combinations Comparison Guide (`C01–C12`, Fixed `D1 = bye1_repaired`)
- Data Engineer Stage Notes (`sonnet`)

## God Nodes (most connected - your core abstractions)
1. `assign_format_bucket()` - 16 edges
2. `bowler_runs()` - 14 edges
3. `fit_expected_and_opposition_models()` - 14 edges
4. `build_batting_ratings()` - 14 edges
5. `build_bowling_ratings()` - 14 edges
6. `build_or_load_exact_modeled()` - 13 edges
7. `SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics` - 13 edges
8. `balls_faced()` - 12 edges
9. `legal_balls()` - 12 edges
10. `main()` - 12 edges

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

## Communities (46 total, 19 thin omitted)

### Community 0 - "Pressure & Rating Modeling"
Cohesion: 0.08
Nodes (27): deliveries_enriched.parquet Target Table, Match-State Reconstruction Pipeline Steps, player_registry.csv Canonical Registry, Data Engineering Agent Specification, Pressure Reliability Rating Composite Model, Role-Specific Pressure Construction, Pressure & Rating Modeling Agent Specification, Stage 2 Modeling Artifacts Suite (+19 more)

### Community 1 - "stage3_ratings.py"
Cohesion: 0.09
Nodes (22): 1. Output Summary & Row Accounting, 2. Target Reconstruction & Repair Diagnostics (2nd Innings, Non-DLS), 3. RRR & Boundary Edge Cases, Stage 1 — Ball-State Checks (`sonnet`), What Was Executed, assign_format_bucket(), balls_faced(), batter_runs() (+14 more)

### Community 2 - "SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics"
Cohesion: 0.06
Nodes (32): 10. Quickstart & Reproduction Guide, 1. Executive Summary & Official Unstop Dropdown Rankings, 2. The 8 Forensic Dataset Traps & Data Hygiene, 3. Multi-Agent Architecture, 4.1 Win Probability & Leverage Calibration, 4.2 The Five Core Pressure Dimensions, 4.3 Role-Specific Pressure Indices (BPI & BoPI), 4.4 Dual-Baseline Architecture & Dynamic Wicket Valuation (+24 more)

### Community 4 - "numpy"
Cohesion: 0.08
Nodes (21): run_stage3_pipeline(), main(), main(), build_exact_ball_state(), build_or_load_exact_modeled(), main(), quick_bootstrap_p_top10(), split_half_rho() (+13 more)

### Community 5 - "SupeRR Selector Season 2 (Round 1) — Methodology Report"
Cohesion: 0.06
Nodes (30): 1.1 Why Standard Metrics Fail to Measure Pressure, 1.2 Mathematical Formulation of the 5 Pressure Dimensions, 1.3 Composite Role Indices: BPI & BoPI, 1.4 Empirical Proof of Pressure Separation, 2.1 Contextual Par Expectation ($\text{xRuns}$ and $\text{xWickets}$), 2.2 Ball-Level Net Value Added, 2.3 The Dual-Baseline Comparison, 2.4 Pressure Reliability Rating (PRR) Composite Formulation (+22 more)

### Community 6 - "Top 10 Batters"
Cohesion: 0.08
Nodes (23): #10 Mujeeb Ur Rahman (`player_id=6450`, CI=Outside / Volatile, P(Top10)=21.8%), #10 Rinku Singh (`player_id=4708`, CI=Borderline (8-14), P(Top10)=57.3%), #1 Vaibhav Sooryavanshi (`player_id=50284`, CI=Lock Top 10, P(Top10)=98.0%), #1 Wanindu Hasaranga (`player_id=4900`, CI=Borderline (8-14), P(Top10)=64.2%), #2 Sunil Narine (`player_id=781`, CI=Likely Top 10, P(Top10)=66.7%), #2 Suryakumar Yadav (`player_id=1699`, CI=Lock Top 10, P(Top10)=92.0%), #3 Josh Hazlewood (`player_id=830`, CI=Likely Top 10, P(Top10)=65.5%), #3 Travis Head (`player_id=2367`, CI=Likely Top 10, P(Top10)=71.1%) (+15 more)

### Community 7 - "stage1_data_engineering.py"
Cohesion: 0.10
Nodes (5): convert_cricket_overs_to_balls(), run_stage1_pipeline(), run_stage2_pipeline(), build(), main()

### Community 8 - "3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE)"
Cohesion: 0.12
Nodes (15): 1. Mission & Competition Context, 2. Workspace Data Inventory & Exact Schema, 3. Eight Mandatory Dataset Traps & Rules (READ BEFORE WRITING ANY CODE), 4. Multi-Agent Architecture & Execution Pipeline, 5. Definition of Done (Verification Checklist), AGENTS.md — SupeRR Selector Season 2 (Round 1) Master Agent Blueprint, Full Column Specification for `ball_by_ball.csv` (33 Columns), Trap 1: `extras1_runs` is a Categorical ID (`extras_type_id`), NOT Run Counts! (+7 more)

### Community 9 - "SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`)"
Cohesion: 0.18
Nodes (10): 0. Executive Summary, 1. Defining Pressure — Win Probability Leverage Index (`LI`) & `D1 = bye1_repaired`, 2. Data Discipline, Context Baselines & Opposition Adjustment, 3. The 5-Pillar Architecture, Empirical Bayes Shrinkage & Eligibility, 4. Final Top 10 Batters & Top 10 Bowlers Under Pressure, 5. Robustness, Limitations & Missing-Stars Audit, 6. Reproducibility Appendix, SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`) (+2 more)

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

### Community 17 - "Defining pressure (the heart of Round 1 — the human decides)"
Cohesion: 0.33
Nodes (5): Defining pressure (the heart of Round 1 — the human decides), One situation, two perspectives, Pitfalls, Prove it separates pressure from ordinary play (goes in the report), Recommended design: two lenses that must agree

### Community 18 - "Final ranking & reliability checks"
Cohesion: 0.33
Nodes (5): Build the ranking, Final ranking & reliability checks, Mandatory robustness suite (report each as a table/figure), Presenting uncertainty, Sanity audits (read, don't just trust the numbers)

### Community 19 - "Bowling under pressure"
Cohesion: 0.33
Nodes (5): Bowling under pressure, Metrics (pressure balls, per bowler), Per-delivery building blocks, Pitfalls, Suggested rating (human to confirm weights)

### Community 20 - "Methodology report"
Cohesion: 0.40
Nodes (4): Figures that earn their place, Methodology report, Outline (map 1:1 to the brief's five required sections), Writing rules

### Community 21 - "Stage 1 — Data Profile (`sonnet`)"
Cohesion: 0.40
Nodes (4): 1. Table Shapes & Coverage, 2. Competition & Format Breakdown (`ball_state`, 867 matches), 3. Data Integrity & Traps Checked, Stage 1 — Data Profile (`sonnet`)

### Community 22 - "Decisions Log (`sonnet` Pipeline)"
Cohesion: 0.33
Nodes (5): Decisions Log (`sonnet` Pipeline — Corrected `C03` Consolidation Run), Stage 1 — Data Engineering & Profiling (`data-engineer`), Stage 2 — Pressure Definition (`pressure-modeler`), Stage 3 — Analyst Metrics, Shrinkage & Eligibility (`batting-analyst`, `bowling-analyst`), Stage 4 — Strategic Enhancements (`strategic-analyst`)

### Community 23 - "IPL vs T20I fairness"
Cohesion: 0.50
Nodes (3): Approach (recommended), Checks, IPL vs T20I fairness

### Community 24 - "Ball-state feature table"
Cohesion: 0.40
Nodes (4): Ball-state feature table, Columns produced (state is **before** the delivery unless `_after`), Rules & traps, Validate after every rebuild

### Community 26 - "Shrinkage & Eligibility Specification (`C03` Primary: `D1 = bye1_repaired`, `LI >= 75th pct`)"
Cohesion: 0.50
Nodes (3): 1. Empirical Bayes Shrinkage Parameters (`outputs/shrinkage_params.json`), 2. Eligibility Thresholds & Pool Depth (`outputs/eligibility_scan.csv`), Shrinkage & Eligibility Specification (`C03` Primary: `D1 = bye1_repaired`, `LI >= 75th pct`)

### Community 27 - "Format Baselines & Opposition Adjustment Notes (`sonnet`)"
Cohesion: 0.50
Nodes (3): 1. IPL vs T20I vs Emerging Scoring Environments (`outputs/format_baselines.csv`), 2. Joint Context + Batter + Bowler Opposition Adjustment, Format Baselines & Opposition Adjustment Notes (`sonnet`)

### Community 28 - "Robustness & Stability Notes (`sonnet`)"
Cohesion: 0.50
Nodes (3): 1. 1,000-Match Cluster Bootstrap Tiers, 2. Structural Stress Tests (`outputs/robustness_summary.csv`), Robustness & Stability Notes (`C03` 5-Pillar Architecture: `D1 = bye1_repaired`, `LI >= 75th pct`)

### Community 43 - "Gate Combinations Comparison Guide (`C01–C12`, Fixed `D1 = bye1_repaired`)"
Cohesion: 0.50
Nodes (3): 1. Objective Diagnostics Across Combinations (`summary_metrics.csv`), 2. Why `C03` + 5-Combo Confirmation (`{C01, C03, C04, C11, C12}`) Survives, Gate Combinations Comparison Guide (`C01–C12`, Fixed `D1 = bye1_repaired`)

### Community 44 - "Data Engineer Stage Notes (`sonnet`)"
Cohesion: 0.50
Nodes (3): Data Engineer Stage Notes (`sonnet`), Key Pitfalls Caught & Handled, Next Stage Handoff

## Knowledge Gaps
- **9 isolated node(s):** `player_registry.csv Canonical Registry`, `Win Probability & Leverage Index Calibration`, `Five-Section Methodology Report Architecture`, `Robustness & Sensitivity Verification Suite`, `Publication-Grade Visualizations Suite` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 267 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `bowler_runs()` connect `stage3_ratings.py` to `Ball-state feature table`, `Bowling under pressure`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `bowler_runs()` (e.g. with `data-engineer.md` and `Columns produced (state is **before** the delivery unless `_after`)`) actually correct?**
  _`bowler_runs()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `player_registry.csv Canonical Registry`, `Win Probability & Leverage Index Calibration`, `Five-Section Methodology Report Architecture` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pressure & Rating Modeling` be split into smaller, more focused modules?**
  _Cohesion score 0.08143939393939394 - nodes in this community are weakly interconnected._
- **Why does `fit_expected_and_opposition_models()` connect `stage3_ratings.py` to `numpy`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Should `stage3_ratings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08708272859216255 - nodes in this community are weakly interconnected._
- **Why does `Per-delivery building blocks` connect `Bowling under pressure` to `stage3_ratings.py`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._