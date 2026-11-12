---
name: baselines-shrinkage-eligibility
description: Player baselines, expected-performance models, empirical-Bayes shrinkage and eligibility thresholds for fair comparisons across very different sample sizes. Use before final ratings.
---
# Baselines, shrinkage, eligibility

## 1. Two baselines (use both, name them clearly)
- **Context baseline (league expectation):** E[outcome | state, phase, innings, opponent type, competition]. Fit on all balls. Answers "how much better than a typical player in the same situation?"
- **Own baseline (personal normal):** the player's own non-pressure performance (same competition mix). Answers the brief's *"compared with their usual performance levels"*. Use *non-pressure* balls only so the baseline isn't contaminated by the very thing being tested.

## 2. Shrinkage (mandatory)
- Rates (dot%, boundary%, dismissal rate, wkt rate): Beta-Binomial empirical Bayes. Estimate prior (α,β) by method of moments / MLE across players with ≥ a minimal number of balls; posterior mean = (x+α)/(n+α+β).
- Continuous per-ball residuals (RAE/ball, RSAE/ball): normal–normal. `shrunk = μ + (n/(n + k)) × (raw − μ)` with `k = σ²_within / σ²_between` estimated by random-effects/ANOVA over matches (cluster by match, not ball).
- Report raw vs shrunk side by side; show 2–3 players whose rank moves most and why.
- Prefer **cluster bootstrap by match** for CIs (resample matches, recompute rating).

## 3. Eligibility (decide from the data, then fix and document)
- Compute the distribution of pressure balls per player (batters faced / bowlers bowled) and pressure matches. Choose thresholds near the elbow of that distribution and test several. Typical starting points to *try*:
  batters ≥ ~150 pressure balls-faced or ≥ 15 pressure innings; bowlers ≥ ~100 pressure balls or ≥ 15 pressure spells; plus ≥ 2 seasons or ≥ 2 competitions? (human decides).
- Always require activity in the recent period (e.g. at least one match in the last 12–18 months of the data) if the goal is to inform IPL 2027 auction targets — the data runs to Nov 2026.
- Report how many players pass, and a sensitivity table of top-10 membership across thresholds.

## 4. Recency & role
- Optional exponential decay weights by match_date (half-life 1–2 years) as a robustness variant; keep primary = equal-weight if you can't justify decay.
- Tag each player's modal role (opener/middle/finisher; powerplay/middle/death bowler; pace/spin) from usage, not reputation.

## 5. Exposure sanity
- Report pressure-ball counts and matches next to every rating. A player with huge numbers on weak opposition should not outrank someone with fewer but tougher balls without the adjustment shown.

Outputs: `outputs/eligibility.md`, `outputs/shrinkage_params.json`.
