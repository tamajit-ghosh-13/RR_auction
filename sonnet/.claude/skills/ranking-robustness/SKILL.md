---
name: ranking-robustness
description: Combine component scores into final top-10 lists and stress-test them (bootstrap, split-half, threshold/weight/lens sensitivity, leave-one-season-out). Use before locking picks and whenever the report claims reliability.
---
# Final ranking & reliability checks

## Build the ranking
1. Standardise each component (z-score among eligible players, separately for batters and bowlers).
2. Combine with the human-approved weights; sort; keep top 25 as a shortlist.
3. Attach to every shortlisted player: pressure balls, pressure matches, IPL/T20I split, raw vs shrunk metric, component z-scores, 90% CI of rating.

## Mandatory robustness suite (report each as a table/figure)
| Check | How | Pass signal |
|---|---|---|
| Cluster bootstrap by match | 1,000 resamples of matches → rating & rank distribution | top-10 players stay top-15 in ≥ ~80% of draws |
| Split-half reliability | split each player's pressure matches odd/even (or by season) → Spearman of ratings | clearly positive; report the number honestly |
| Pressure threshold | LI 75th / 90th / 95th pct | ≥ ~7 of top 10 shared |
| Pressure lens | Lens A (WP leverage) vs Lens B (rules) | high overlap or an explained difference |
| Weight perturbation | ±10 points on each weight, random Dirichlet weights | stable membership |
| Eligibility threshold | 3–4 minimum-ball settings | stable membership |
| Format | IPL-only, T20I-only, pooled | flag format-dependent players |
| Season holdout | leave one season out; also fit on 2022–24 and check 2025–26 | rating persists (year-to-year correlation) |
| Target noise | ±5 runs on chase targets; bye-run estimate 0.8–1.5 | ranks barely move |
| Unadjusted vs adjusted | Spearman between lists | explain differences |

## Presenting uncertainty
- Use "tiers": players whose CIs overlap are a tier; order inside a tier by the stated tie-break (higher consistency, then more pressure balls).
- Report borderline cases (ranks 8–14) explicitly. Honest limitation text > hidden fragility.

## Sanity audits (read, don't just trust the numbers)
- Look at each top-10 player's top 5 and bottom 5 pressure matches: is the rating driven by one innings?
- Check no player is in both batter and bowler lists by accident of ID collisions (`Abdul Samad`, `Basil Hameed`, `Haider Ali`).
- Confirm player names exist in `competition_team_player_mapping.csv` (they will populate the Unstop dropdown).
- Reputation check is allowed only as a *post-hoc* sanity read; never as a ranking input.

Outputs: `outputs/final_rankings.csv`, `outputs/robustness_*.csv|png`, `outputs/robustness_notes.md`.
