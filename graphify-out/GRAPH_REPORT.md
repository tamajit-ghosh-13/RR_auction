# Graph Report - RR_auction_strategy  (2026-11-11)

## Corpus Check
- 13 files · ~15,824 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .csv 15, .parquet 2, (none) 1)

## Summary
- 113 nodes · 160 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1276bddf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Pressure & Rating Modeling
- Round 1 Challenge: Identify Most Reliable Players Under Pressure
- SupeRR Selector Season 2 (Round 1) — Methodology Report
- Data Engineering & State Reconstruction
- stage3_validation_and_reporting.py
- Section 4: Evidence for the Top 10 Batters & Top 10 Bowlers
- Competition Data Inventory & Schema Map
- Sensitivity & Verification Protocol

## God Nodes (most connected - your core abstractions)
1. `SupeRR Selector Season 2 (Round 1) — Methodology Report` - 9 edges
2. `Competition Data Inventory & Schema Map` - 9 edges
3. `Round 1 Challenge: Identify Most Reliable Players Under Pressure` - 8 edges
4. `Cricket Pressure Analytics Domain Skill` - 8 edges
5. `load_and_clean_superr_data Function` - 8 edges
6. `Pressure & Rating Modeling Agent Specification` - 7 edges
7. `Five-Section Methodology Report Architecture` - 7 edges
8. `Pressure Reliability Rating (PRR)` - 7 edges
9. `Report & Validation Agent Specification` - 7 edges
10. `SupeRR Selector Master Agent Blueprint` - 7 edges

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

## Communities (8 total, 1 thin omitted)

### Community 0 - "Pressure & Rating Modeling"
Cohesion: 0.15
Nodes (14): Pressure Reliability Rating Composite Model, Role-Specific Pressure Construction, Pressure & Rating Modeling Agent Specification, Stage 2 Modeling Artifacts Suite, Win Probability & Leverage Index Calibration, Batting Pressure Index (BPI), Bowling Pressure Index (BoPI), Contextual Expected Value (xRuns / xWicket) (+6 more)

### Community 1 - "Round 1 Challenge: Identify Most Reliable Players Under Pressure"
Cohesion: 0.15
Nodes (18): Five-Section Methodology Report Architecture, Robustness & Sensitivity Verification Suite, Report & Validation Agent Specification, Publication-Grade Visualizations Suite, Report and Validation Workflow, SupeRR Selector Master Agent Blueprint, Stage 1: Data Engineering Pipeline, Stage 2: Pressure & Rating Modeling Pipeline (+10 more)

### Community 2 - "SupeRR Selector Season 2 (Round 1) — Methodology Report"
Cohesion: 0.08
Nodes (25): 1.1 Why Standard Metrics Fail to Measure Pressure, 1.2 Mathematical Formulation of the 5 Pressure Dimensions, 1.3 Composite Role Indices: BPI & BoPI, 1.4 Empirical Proof of Pressure Separation, 2.1 Contextual Par Expectation ($\text{xRuns}$ and $\text{xWickets}$), 2.2 Ball-Level Net Value Added, 2.3 The Dual-Baseline Comparison, 2.4 Pressure Reliability Rating (PRR) Composite Formulation (+17 more)

### Community 3 - "Data Engineering & State Reconstruction"
Cohesion: 0.40
Nodes (5): deliveries_enriched.parquet Target Table, Match-State Reconstruction Pipeline Steps, player_registry.csv Canonical Registry, Data Engineering Agent Specification, Data Engineering Workflow

### Community 4 - "stage3_validation_and_reporting.py"
Cohesion: 0.16
Nodes (4): convert_cricket_overs_to_balls(), run_stage1_pipeline(), run_stage2_pipeline(), run_stage3_pipeline()

### Community 5 - "Section 4: Evidence for the Top 10 Batters & Top 10 Bowlers"
Cohesion: 0.40
Nodes (5): 4.1 Detailed Breakdown of Top 10 Batters Under Pressure, 4.2 Detailed Breakdown of Top 10 Bowlers Under Pressure, 4.3 Concrete Signature Match Case Studies from the Data, 4.4 Strategic Takeaways for Rajasthan Royals' IPL 2027 Auction, Section 4: Evidence for the Top 10 Batters & Top 10 Bowlers

### Community 6 - "Competition Data Inventory & Schema Map"
Cohesion: 0.21
Nodes (5): SupeRR Selector Always-On Rules, build_match_state Function, load_and_clean_superr_data Function, convert_cricket_overs_to_balls Function, Competition Data Inventory & Schema Map

## Knowledge Gaps
- **7 isolated node(s):** `Win Probability & Leverage Index Calibration`, `Bowling Pressure Index (BoPI)`, `Verification and Sensitivity Protocol`, `Empirical Bayes Shrinkage Regularization`, `player_registry.csv Canonical Registry` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 44 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Cricket Pressure Analytics Domain Skill` connect `Pressure & Rating Modeling` to `Round 1 Challenge: Identify Most Reliable Players Under Pressure`, `Data Engineering & State Reconstruction`, `Competition Data Inventory & Schema Map`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `load_and_clean_superr_data Function` (e.g. with `Match-State Reconstruction Pipeline Steps` and `Trap 1: extras1_runs Categorical ID`) actually correct?**
  _`load_and_clean_superr_data Function` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Win Probability & Leverage Index Calibration`, `Bowling Pressure Index (BoPI)`, `Verification and Sensitivity Protocol` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Pressure & Rating Modeling` be split into smaller, more focused modules?**
  _Cohesion score 0.14705882352941177 - nodes in this community are weakly interconnected._
- **Why does `Report & Validation Agent Specification` connect `Round 1 Challenge: Identify Most Reliable Players Under Pressure` to `Pressure & Rating Modeling`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Should `Round 1 Challenge: Identify Most Reliable Players Under Pressure` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._
- **Why does `SupeRR Selector Master Agent Blueprint` connect `Round 1 Challenge: Identify Most Reliable Players Under Pressure` to `Competition Data Inventory & Schema Map`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._