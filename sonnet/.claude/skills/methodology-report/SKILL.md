---
name: methodology-report
description: Structure and draft the Round 1 methodology report (PDF/PPT/dashboard) covering pressure definition, performance measurement, fair comparisons, evidence, reliability and limitations. Use after ratings and robustness checks exist.
---
# Methodology report

Judging is on a transparent, reproducible method supported by the supplied data. The participant must own the narrative: the agent drafts structure, tables and figures; the human rewrites in their own voice and confirms every claim.

## Outline (map 1:1 to the brief's five required sections)
0. **Executive summary** (½ page): the two top-10 lists, one-line method, 3 headline insights.
1. **Pressure definition** — formula, thresholds, why meaningful, evidence it separates pressure from ordinary play (tables/figures from pressure-definition).
2. **Performance measurement** — batting & bowling metrics, context baseline vs own baseline, wicket cost, rating formula and weights (from the metric skills).
3. **Fair comparisons** — sample sizes/shrinkage, eligibility thresholds, match-context adjustment, IPL vs T20I handling, opposition/venue effects (from baselines + fairness skills).
4. **Evidence for the top 10** — one table per list (rank, player, team(s), pressure balls/matches, key metrics vs expected, own-baseline delta, consistency, CI), 2–4 figures, a short "why #1 beats #2" and borderline discussion.
5. **Reliability & limitations** — robustness results, uncertainty tiers, data issues (missing bye runs, noisy targets, DLS, super overs, `other` extras, no ball-tracking, A-team events), where the model is least certain.
6. **Reproducibility appendix** — data prep decisions, parameter list, seeds, script names and run order, library versions.
7. *(Optional)* journey / insights note — not scored.

## Figures that earn their place
LI distribution with threshold · pressure-rate heat-map (balls_left × wickets) · pressure vs non-pressure outcome comparison · shrinkage before/after · rank-stability (bootstrap) plot · rating-component stacked bars for the top 10 · IPL vs T20I contribution.

## Writing rules
- Every number traces to an output file; include the script path in captions.
- Plain language first, formulas second; define each metric once.
- No reputation-based justification. Use phrases like "rated by the model" not "everyone knows".
- Be explicit about decisions the participant made and alternatives tested.
- Dropdown lists in Unstop must equal the report's tables, same order.
- Format: PDF (primary), ≤ ~12 pages + appendix; or an interactive dashboard with the same sections. Keep file names free of private data.
- Do not embed raw rows from the data pack; aggregated tables only.

Outputs: `outputs/report.md` (source) → exported PDF; `outputs/figures/*.png`.
