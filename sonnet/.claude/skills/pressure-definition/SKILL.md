---
name: pressure-definition
description: Design, calibrate and justify the definition of "pressure" per delivery for both batting and bowling, and show it separates pressure from ordinary situations. Use after ball-state-features.
---
# Defining pressure (the heart of Round 1 — the human decides)

The brief says pressure is *"for you to define"* (required rate, wickets in hand, balls remaining, innings stage, closeness, or a combination),
must **work for both batting and bowling**, and you must **show how it distinguishes pressure from ordinary situations**.

## Recommended design: two lenses that must agree
**Lens A — Leverage (primary, model-based).**
1. Fit a win-probability model `WP(state)` on non-DLS, non-super-over deliveries (innings 1 and 2, with an innings interaction).
   Features: balls_left, wkts_in_hand, runs_needed (chase) or runs_before + projected score (innings 1), rrr−crr (chase), phase.
   Models: logistic with splines → `HistGradientBoostingClassifier`. Target `batting_won`; drop ties/no-results.
   **GroupKFold by match_id** (never split one match across folds). Report log-loss, Brier, calibration plot.
2. Leverage `LI = E[|ΔWP|]` over next-ball outcomes (or |WP_after − WP_before| averaged in state bins), scaled so mean = 1.0.
3. **Pressure = top tail**, e.g. LI ≥ 90th percentile (also report 75th and 95th). Pick thresholds from the plotted LI distribution.

**Lens B — transparent rule-based index** (for the report + sanity check). Candidate components, each scored 0–1:
- Chase: `rrr − crr` gap (clipped), wickets in hand ≤ 4, balls_left ≤ 36, required rate high **while the chase is still alive** (WP roughly 0.25–0.75).
- Innings 1: death overs with ≥5 wickets down; collapse (≥2 wickets in last 12 balls); scoring far below par after over 10.
- Match-context multiplier: `knock_out`, `stage` in Final/Qualifier/Eliminator/Semi Final/Super 4.
- Closeness: small |WP − 0.5|.
Combine via weights (or regress |ΔWP| on them); list and justify the weights.

**Agreement test:** report Spearman and Jaccard overlap between Lens A and Lens B pressure sets. If low, explain which drives the ranking (recommend A, B as robustness).

## One situation, two perspectives
Pressure is symmetric: the same delivery is high-pressure for batter and bowler. Use the identical `pressure_flag`/`LI` for both, and interpret
direction per role (batter needs runs without losing wickets; bowler needs dots/wickets). Don't build incompatible pressure sets for the two roles without justification.

## Prove it separates pressure from ordinary play (goes in the report)
- Table: pressure vs non-pressure → runs/ball, dot%, boundary%, wicket rate, phase mix, innings mix, knockout share.
- Charts: LI distribution with thresholds; heat-map of pressure rate by (balls_left × wkts_in_hand).
- Effect sizes with CIs showing outcomes genuinely differ under pressure.

## Pitfalls
- Pressure must be defined from the state **before** the ball, never from the outcome.
- Exclude DLS and super overs from WP training and say so.
- Approximate targets (bye gap): fit WP with `target_raw` vs repaired and report the difference.
- "Pressure = death overs" confounds pressure with power-hitting and mechanically rewards finishers.
- Finish with a one-paragraph definition + one formula block the report-writer can paste.

Outputs: `outputs/pressure_definition.md`, `data/interim/ball_pressure.csv.gz` (adds `wp_before, li, pressure_flag, pressure_tier, rule_index`).
