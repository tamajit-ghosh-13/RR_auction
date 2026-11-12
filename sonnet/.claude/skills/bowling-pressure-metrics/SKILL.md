---
name: bowling-pressure-metrics
description: Compute bowler performance under pressure vs context-expected and vs own baseline (economy, wickets, dots, boundaries, extras discipline) and produce a bowling reliability score. Use after pressure-definition and baselines-shrinkage-eligibility.
---
# Bowling under pressure

Unit: bowler × pressure delivery (`bowler_id`). Legal balls bowled for rate denominators; wides/no-balls are charged to the bowler's runs and counted as discipline events.

## Per-delivery building blocks
- `bowler_runs` from `ball_state` (bat runs + wide + no-ball + extras_2; **not** byes/leg-byes).
- `wkt = is_wkt_bowler` (excludes RunOut, Retire Out, Obstructing). Keep run-out involvement separate/unused.
- Expected runs and expected wicket probability given context (balls_left/over, wkts_in_hand, phase, innings, batter order/hand, competition) fitted on **all** deliveries.
- Batter-quality adjustment: facing a top-order hitter at the death is harder than facing a tail-ender — include striker batter-effect from the joint model.

## Metrics (pressure balls, per bowler)
1. **Runs Saved Above Expected per 24 balls (RSAE24)** = 24 × Σ(E[runs] − bowler_runs)/balls + wicket value × (wkts − E[wkts]) per 24 balls. (24 balls ≈ 4 overs.)
2. **Pressure economy vs expected**, dot%, boundary% conceded, wicket rate, balls per wicket (all vs context-expected).
3. **Discipline**: wide + no-ball rate under pressure vs baseline (these hand free runs/free hits when it matters).
4. **WPA saved** per 24 balls (from the WP model; cross-check).
5. **Own-baseline delta** = pressure RSAE24 − non-pressure RSAE24, shrunk.
6. **Consistency**: per-match pressure RSAE (matches with ≥ k pressure balls), % matches ≥ 0, median, stability; winsorise.
7. Phase fairness: death specialists see more pressure balls — evaluate vs *phase-and-state-specific* expectation, not league average economy.

## Suggested rating (human to confirm weights)
```
BowlRating = z( shrunk RSAE24 )            # level under pressure, context-adjusted    (≈ 50%)
           + z( shrunk own-baseline delta )                                          (≈ 15%)
           + z( consistency )                                                        (≈ 25%)
           + z( discipline + WPA saved )                                             (≈ 10%)
```

## Pitfalls
- Wicket-taking is lumpy; use shrinkage and don't rank on wicket count alone.
- Pace vs spin and left/right match-ups differ by phase; the context model must include `pace_or_spin`, `bowling_type`, `batting_type`.
- Partnership/captaincy effects: the same bowler gets overs differently across teams → opportunity bias (report pressure balls per match).
- Never use `bowl_speed` unless cleaned (sentinels 0/−1, outliers to 1456).

Outputs: `outputs/bowling_ratings.csv`, `outputs/bowling_top10.md`.
