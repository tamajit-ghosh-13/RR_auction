# Batting & Bowling Analysts Stage Notes (`sonnet`)

## Execution Summary
- Built format baselines (`outputs/format_baselines.csv`) and fitted 5-fold match-grouped OOF Context + Joint Batter-Bowler Ridge models across `189,555` clean IPL + T20I deliveries (`alpha = 150` runs, `alpha = 250` wickets).
- Attributed batting dismissals strictly via `dismissed_player_id` (capturing non-striker run-outs accurately) and bowler wickets strictly to `{Caught, Bowled, LBW, Stump, Hit Wicket}`.
- Estimated ANOVA match-variance EB shrinkage constants (`k_bat = 206.0`, `k_bowl = 199.6`) and Beta-Binomial positive-match consistency (`m0 = 8`), plus winsorised (1st–99th pct) per-match Sharpe ratios.
- Scanned eligibility curves (`outputs/eligibility_scan.csv`) and flagged near-miss stars (`Prabhsimran Singh` `119` balls, `Rovman Powell` `113` balls, `Heinrich Klaasen` `96` balls, `Mohsin Khan` `95` balls).
- Saved `outputs/batting_ratings.csv`, `outputs/bowling_ratings.csv`, `outputs/shrinkage_params.json`, and `outputs/figures/eligibility_elbow.png`.
