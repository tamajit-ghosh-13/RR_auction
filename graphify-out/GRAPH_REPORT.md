# Graph Report - RR_auction_strategy  (2026-11-10)

## Corpus Check
- Corpus is ~7,160 words - fits in a single context window. You may not need a graph.

## Summary
- 59 nodes · 89 edges · 11 communities (7 shown, 4 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.91)
- Token cost: 7,160 input · 4,200 output

## Community Hubs (Navigation)
- Pressure & Rating Modeling
- Official Problem & Evaluation Pillars
- Value Metrics & Empirical Bayes
- Data Engineering & State Reconstruction
- Validation & Unstop Submission Compliance
- Master Multi-Agent Architecture
- Dataset Schema & Match Exceptions
- Core Data Guardrails & Rule Traps
- Match-State Calculation Engine
- Sensitivity & Verification Protocol

## God Nodes (most connected - your core abstractions)
1. `Competition Data Inventory & Schema Map` - 9 edges
2. `Round 1 Challenge: Identify Most Reliable Players Under Pressure` - 8 edges
3. `Cricket Pressure Analytics Domain Skill` - 8 edges
4. `load_and_clean_superr_data Function` - 8 edges
5. `SupeRR Selector Master Agent Blueprint` - 7 edges
6. `Pressure Reliability Rating (PRR)` - 7 edges
7. `Pressure & Rating Modeling Agent Specification` - 7 edges
8. `Report & Validation Agent Specification` - 7 edges
9. `Five-Section Methodology Report Architecture` - 7 edges
10. `Critical Data Guardrails` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 1: Pressure Definition`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 2: Performance Measurement`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 3: Fair Comparisons`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 4: Evidence for Top 10`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf
- `Five-Section Methodology Report Architecture` --conceptually_related_to--> `Evaluation Pillar 5: Reliability and Limitations`  [INFERRED]
  .agents/agents/report-and-validation-agent.md → Round 1 Problem Statement _ SupeRR Selector Season 2.docx.pdf

## Hyperedges (group relationships)
- **Three-Stage SupeRR Selector Multi-Agent Analytics Architecture** — agents_stage_1_data_engineering, agents_stage_2_pressure_modeling, agents_stage_3_report_validation [EXTRACTED 1.00]
- **Official Five Evaluation Pillars of SupeRR Selector Season 2** — round_1_problem_statement___superr_selector_season_2_docx_pressure_definition_pillar, round_1_problem_statement___superr_selector_season_2_docx_performance_measurement_pillar, round_1_problem_statement___superr_selector_season_2_docx_fair_comparisons_pillar, round_1_problem_statement___superr_selector_season_2_docx_evidence_pillar, round_1_problem_statement___superr_selector_season_2_docx_reliability_limitations_pillar, _agents_agents_report_and_validation_agent_five_section_report [EXTRACTED 1.00]
- **Mandatory Forensic Schema Traps and Critical Guardrails** — agents_trap_1_extras1_runs, agents_trap_2_over_ball_num, agents_trap_3_player_id_canonicalization, agents_trap_4_wicket_attribution, agents_trap_5_competition_tiers, _agents_rules_superr_selector_critical_data_guardrails [EXTRACTED 1.00]

## Communities (11 total, 4 thin omitted)

### Community 0 - "Pressure & Rating Modeling"
Cohesion: 0.20
Nodes (8): Pressure Reliability Rating Composite Model, Role-Specific Pressure Construction, Pressure & Rating Modeling Agent Specification, Stage 2 Modeling Artifacts Suite, Win Probability & Leverage Index Calibration, Batting Pressure Index (BPI), Bowling Pressure Index (BoPI), Pressure Modeling Workflow

### Community 1 - "Official Problem & Evaluation Pillars"
Cohesion: 0.43
Nodes (8): Five-Section Methodology Report Architecture, Evaluation Pillar 4: Evidence for Top 10, Evaluation Pillar 3: Fair Comparisons, Methodology Report Deliverable, Evaluation Pillar 2: Performance Measurement, Evaluation Pillar 1: Pressure Definition, Round 1 Challenge: Identify Most Reliable Players Under Pressure, Evaluation Pillar 5: Reliability and Limitations

### Community 2 - "Value Metrics & Empirical Bayes"
Cohesion: 0.38
Nodes (6): Contextual Expected Value (xRuns / xWicket), Cricket Pressure Analytics Domain Skill, Empirical Bayes Shrinkage Regularization, Net Batting Value per Ball (v_bat), Net Bowling Value per Ball (v_bowl), Pressure Reliability Rating (PRR)

### Community 3 - "Data Engineering & State Reconstruction"
Cohesion: 0.40
Nodes (5): deliveries_enriched.parquet Target Table, Match-State Reconstruction Pipeline Steps, player_registry.csv Canonical Registry, Data Engineering Agent Specification, Data Engineering Workflow

### Community 4 - "Validation & Unstop Submission Compliance"
Cohesion: 0.33
Nodes (5): Robustness & Sensitivity Verification Suite, Report & Validation Agent Specification, Publication-Grade Visualizations Suite, Report and Validation Workflow, Unstop Top 10 Player Rankings Deliverable

### Community 5 - "Master Multi-Agent Architecture"
Cohesion: 0.47
Nodes (5): SupeRR Selector Master Agent Blueprint, Stage 1: Data Engineering Pipeline, Stage 2: Pressure & Rating Modeling Pipeline, Stage 3: Validation & Report Generation Pipeline, Round 1 Problem Statement Document

### Community 8 - "Match-State Calculation Engine"
Cohesion: 0.67
Nodes (3): build_match_state Function, load_and_clean_superr_data Function, convert_cricket_overs_to_balls Function

## Knowledge Gaps
- **7 isolated node(s):** `Bowling Pressure Index (BoPI)`, `Empirical Bayes Shrinkage Regularization`, `Verification and Sensitivity Protocol`, `player_registry.csv Canonical Registry`, `Win Probability & Leverage Index Calibration` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 12 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Cricket Pressure Analytics Domain Skill` connect `Value Metrics & Empirical Bayes` to `Match-State Calculation Engine`, `Pressure & Rating Modeling`, `Data Engineering & State Reconstruction`, `Validation & Unstop Submission Compliance`?**
  _High betweenness centrality (0.295) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `load_and_clean_superr_data Function` (e.g. with `Match-State Reconstruction Pipeline Steps` and `Trap 1: extras1_runs Categorical ID`) actually correct?**
  _`load_and_clean_superr_data Function` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Bowling Pressure Index (BoPI)`, `Empirical Bayes Shrinkage Regularization`, `Verification and Sensitivity Protocol` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `Report & Validation Agent Specification` connect `Validation & Unstop Submission Compliance` to `Pressure & Rating Modeling`, `Official Problem & Evaluation Pillars`, `Master Multi-Agent Architecture`?**
  _High betweenness centrality (0.262) - this node is a cross-community bridge._
- **Why does `SupeRR Selector Master Agent Blueprint` connect `Master Multi-Agent Architecture` to `Dataset Schema & Match Exceptions`, `Core Data Guardrails & Rule Traps`?**
  _High betweenness centrality (0.239) - this node is a cross-community bridge._