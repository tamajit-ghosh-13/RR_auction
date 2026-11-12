---
name: batting-pressure-metrics
description: Compute batter performance under pressure vs context-expected and vs own baseline, including wicket cost, consistency and a final batting reliability score. Use after pressure-definition and baselines-shrinkage-eligibility.
---
# Batting under pressure

Unit of analysis: batter × pressure delivery (`striker_id`, balls faced = legal + no-balls; exclude wides). Aggregate to batter × match first, then to batter.

## Per-delivery building blocks
- `bat_runs = runs`. `dot = runs==0 & legal`. `boundary = is_four | is_six`. `dismissed = (dismissed_player_id == striker_id)` — **use dismissed_player_id** (run-outs can be the non-striker).
- **Expected runs** `E[runs | context]`: regress/average bat runs on (balls_left or over, wkts_in_hand, phase, innings, bowler pace/spin, batting order bucket, competition) using **all** deliveries, not just pressure ones.
- **Expected wicket probability** `E[dismissed | context]` the same way (GBM or logistic; GroupKFold by match).
- **Wicket cost** in runs = value of a wicket in that state (≈ runs lost from WP-model or from mean remaining-runs difference with one more wicket down). Convert dismissals to runs so one number captures "runs minus risk".

## Metrics (per batter, pressure balls only unless stated)
1. **Runs Above Expected per 100 balls (RAE100)** = 100 × Σ(bat_runs − E[runs]) / balls − wicket-cost term (Σ(dismissed − E[dismissed]) × wicket value).
2. **Pressure SR** and **SR vs expected SR**; boundary%, dot%, and balls per dismissal (all vs context-expected).
3. **Win-probability added (WPA)** per 100 pressure balls, if the WP model is available (cleanest single measure; use as cross-check or primary).
4. **Own-baseline delta** = RAE100 under pressure − RAE100 in non-pressure play (the brief: *"compared with their usual performance levels"*). Shrink it (see baselines skill); don't let it dominate — a player who is excellent everywhere has delta ≈ 0 yet is still reliable.
5. **Consistency**: per-match pressure RAE (matches with ≥ k pressure balls) → share of matches with RAE ≥ 0, median, and a stability measure (e.g. MAD, or split-half correlation). Reliability ≠ one huge innings: use median/trimmed mean, cap single-match influence (winsorise at 1–99th percentile).
6. **Opportunity-quality adjustment**: opposition bowling quality (bowler-effect from the joint model in ipl-t20i-fairness) and batting position.

## Suggested rating (human to confirm weights)
```
BatRating = z( shrunk RAE100 )            # level under pressure, context-adjusted   (≈ 50%)
          + z( shrunk own-baseline delta )# rises vs usual                           (≈ 15%)
          + z( consistency )              # hit-rate / stability across matches       (≈ 25%)
          + z( WPA100 or knockout bonus ) # impact on results                          (≈ 10%)
```
State weights + a sensitivity table (±10 points each). Put all four z-components in the evidence table.

## Pitfalls
- Don't reward strike-rate alone: dismissals under pressure must hurt.
- Batting order confounds opportunity: openers face pressure differently from finishers — compare within context via expected runs, not raw SR.
- Small samples: a 12-ball cameo is noise → apply eligibility + shrinkage before ranking.
- `batting_order` in ball data is per-delivery; use the modal order per player for labelling.
- Report the batter's pressure balls, matches, innings, and share IPL vs T20I next to every rating.

Outputs: `outputs/batting_ratings.csv` (player_id, name, balls, matches, components, rating, rank, CI), `outputs/batting_top10.md`.
