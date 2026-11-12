# Pressure Modeler Stage Notes (`sonnet`)

## Summary
- Ran 5-fold match-grouped CV WP modeling (`LogisticRegression` vs `HistGradientBoostingClassifier`) on completed non-DLS `IPL + T20I` matches.
- **Diagnostic catch during Stage 2**: Initial WP features used unsmoothed instantaneous `crr`, which spiked on deliveries 1–6 (`legal_before <= 5`) and inflated early-over `LI`. Replaced with a 12-ball Bayesian prior-smoothed `crr_smooth` plus DLS resource projection/cushion, raising Innings 2 OOF AUC to `0.9003` (`LogLoss = 0.3946`) and shifting `LI >= 90th pct` concentration cleanly into true crunch overs (`79.2%` in 2nd-innings chases; `+0.59 pp` wicket rate and `+0.29 rpo` run-rate separation).
- Logistic Regression outperformed HGB on OOF LogLoss and Brier in both innings (`0.6363` vs `0.6464` Inn 1; `0.3946` vs `0.4249` Inn 2) and yields smooth monotonic counterfactuals, so Logistic Regression was selected as the primary WP engine.
- Saved `data/interim/ball_pressure.csv.gz` with continuous `li`, realized `delta_wp` (for WPA), discrete tiers (`is_hp_75`, `is_hp_90`, `is_hp_95`), `li_target_raw`, and Lens B (`rule_score`, `is_hp_rule`).
