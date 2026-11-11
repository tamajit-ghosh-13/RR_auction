# Graph Report - RR_auction_strategy  (2026-11-11)

## Corpus Check
- 14 files · ~19,490 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .csv 15, .parquet 2, (none) 1)

## Summary
- 146 nodes · 192 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cc79fab0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pressure & Rating Modeling
- Round 1 Challenge: Identify Most Reliable Players Under Pressure
- SupeRR Selector Season 2 (Round 1) — Methodology Report
- SupeRR Selector Master Agent Blueprint
- stage3_validation_and_reporting.py
- SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics
- Competition Data Inventory & Schema Map
- 4. Mathematical Methodology
- Section 1: Defining Pressure in T20 Cricket
- Sensitivity & Verification Protocol

## God Nodes (most connected - your core abstractions)
1. `SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics` - 13 edges
2. `SupeRR Selector Season 2 (Round 1) — Methodology Report` - 9 edges
3. `Competition Data Inventory & Schema Map` - 9 edges
4. `4. Mathematical Methodology` - 8 edges
5. `Cricket Pressure Analytics Domain Skill` - 8 edges
6. `Round 1 Challenge: Identify Most Reliable Players Under Pressure` - 8 edges
7. `load_and_clean_superr_data Function` - 8 edges
8. `Pressure Reliability Rating (PRR)` - 7 edges
9. `Pressure & Rating Modeling Agent Specification` - 7 edges
10. `Five-Section Methodology Report Architecture` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 4: Evidence for Top 10`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 3: Fair Comparisons`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --implements--> `Methodology Report Deliverable`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 2: Performance Measurement`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 1: Pressure Definition`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Mandatory Forensic Schema Traps and Critical Guardrails** — agents_trap_1_extras1_runs, agents_trap_2_over_ball_num, agents_trap_3_player_id_canonicalization, agents_trap_4_wicket_attribution, agents_trap_5_competition_tiers, _agents_rules_superr_selector_critical_data_guardrails [EXTRACTED 1.00]
- **Official Five Evaluation Pillars of SupeRR Selector Season 2** — round_1_problem_statement___superr_selector_season_2_docx_pressure_definition_pillar, round_1_problem_statement___superr_selector_season_2_docx_performance_measurement_pillar, round_1_problem_statement___superr_selector_season_2_docx_fair_comparisons_pillar, round_1_problem_statement___superr_selector_season_2_docx_evidence_pillar, round_1_problem_statement___superr_selector_season_2_docx_reliability_limitations_pillar, _agents_agents_report_and_validation_agent_five_section_report [EXTRACTED 1.00]
- **Three-Stage SupeRR Selector Multi-Agent Analytics Architecture** — agents_stage_1_data_engineering, agents_stage_2_pressure_modeling, agents_stage_3_report_validation [EXTRACTED 1.00]

## Communities (10 total, 1 thin omitted)

### Community 0 - "Pressure & Rating Modeling"
Cohesion: 0.15
Nodes (13): Pressure Reliability Rating Composite Model, Role-Specific Pressure Construction, Pressure & Rating Modeling Agent Specification, Win Probability & Leverage Index Calibration, Batting Pressure Index (BPI), Bowling Pressure Index (BoPI), Contextual Expected Value (xRuns / xWicket), Cricket Pressure Analytics Domain Skill (+5 more)

### Community 1 - "Round 1 Challenge: Identify Most Reliable Players Under Pressure"
Cohesion: 0.19
Nodes (14): Stage 2 Modeling Artifacts Suite, Five-Section Methodology Report Architecture, Robustness & Sensitivity Verification Suite, Report & Validation Agent Specification, Publication-Grade Visualizations Suite, Report and Validation Workflow, Evaluation Pillar 4: Evidence for Top 10, Evaluation Pillar 3: Fair Comparisons (+6 more)

### Community 2 - "SupeRR Selector Season 2 (Round 1) — Methodology Report"
Cohesion: 0.08
Nodes (25): 2.1 Contextual Par Expectation ($\text{xRuns}$ and $\text{xWickets}$), 2.2 Ball-Level Net Value Added, 2.3 The Dual-Baseline Comparison, 2.4 Pressure Reliability Rating (PRR) Composite Formulation, 3.1 Resolving the 8 Forensic Dataset Traps, 3.2 Competition Quality Weights ($w_{\text{comp}}$), 3.3 Sample Size Floors & Empirical Bayes Shrinkage, 4.1 Detailed Breakdown of Top 10 Batters Under Pressure (+17 more)

### Community 3 - "SupeRR Selector Master Agent Blueprint"
Cohesion: 0.19
Nodes (11): deliveries_enriched.parquet Target Table, Match-State Reconstruction Pipeline Steps, player_registry.csv Canonical Registry, Data Engineering Agent Specification, SupeRR Selector Always-On Rules, Data Engineering Workflow, SupeRR Selector Master Agent Blueprint, Stage 1: Data Engineering Pipeline (+3 more)

### Community 4 - "stage3_validation_and_reporting.py"
Cohesion: 0.16
Nodes (4): convert_cricket_overs_to_balls(), run_stage1_pipeline(), run_stage2_pipeline(), run_stage3_pipeline()

### Community 5 - "SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics"
Cohesion: 0.08
Nodes (24): 10. Quickstart & Reproduction Guide, 1. Executive Summary & Official Unstop Dropdown Rankings, 2. The 8 Forensic Dataset Traps & Data Hygiene, 3. Multi-Agent Architecture, 5. Visualizations & Publication Charts, 6.1 Bootstrap Stability ($B = 500$ Resamples), 6.2 Threshold Sensitivity Invariance, 6.3 IPL vs. T20I Performance Splits (+16 more)

### Community 6 - "Competition Data Inventory & Schema Map"
Cohesion: 0.26
Nodes (4): build_match_state Function, load_and_clean_superr_data Function, convert_cricket_overs_to_balls Function, Competition Data Inventory & Schema Map

### Community 7 - "4. Mathematical Methodology"
Cohesion: 0.25
Nodes (8): 4.1 Win Probability & Leverage Calibration, 4.2 The Five Core Pressure Dimensions, 4.3 Role-Specific Pressure Indices (BPI & BoPI), 4.4 Dual-Baseline Architecture & Dynamic Wicket Valuation, 4.5 Competition Quality Weighting, 4.6 Empirical Bayes Shrinkage Regularization, 4.7 Match-to-Match Consistency & PRR Rating Formulation, 4. Mathematical Methodology

### Community 8 - "Section 1: Defining Pressure in T20 Cricket"
Cohesion: 0.40
Nodes (5): 1.1 Why Standard Metrics Fail to Measure Pressure, 1.2 Mathematical Formulation of the 5 Pressure Dimensions, 1.3 Composite Role Indices: BPI & BoPI, 1.4 Empirical Proof of Pressure Separation, Section 1: Defining Pressure in T20 Cricket

## Knowledge Gaps
- **7 isolated node(s):** `Win Probability & Leverage Index Calibration`, `Bowling Pressure Index (BoPI)`, `Empirical Bayes Shrinkage Regularization`, `Robustness & Sensitivity Verification Suite`, `Publication-Grade Visualizations Suite` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 71 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Cricket Pressure Analytics Domain Skill` connect `Pressure & Rating Modeling` to `Round 1 Challenge: Identify Most Reliable Players Under Pressure`, `SupeRR Selector Master Agent Blueprint`, `Competition Data Inventory & Schema Map`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **What connects `Win Probability & Leverage Index Calibration`, `Bowling Pressure Index (BoPI)`, `Empirical Bayes Shrinkage Regularization` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pressure & Rating Modeling` be split into smaller, more focused modules?**
  _Cohesion score 0.14705882352941177 - nodes in this community are weakly interconnected._
- **Why does `SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics` connect `SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics` to `4. Mathematical Methodology`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `SupeRR Selector Season 2 (Round 1) — Methodology Report` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Why does `Report & Validation Agent Specification` connect `Round 1 Challenge: Identify Most Reliable Players Under Pressure` to `SupeRR Selector Master Agent Blueprint`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `SupeRR Selector Season 2 (Round 1) — Rajasthan Royals Talent Analytics` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._