# Shrinkage & Eligibility Specification (`sonnet`)

## 1. Empirical Bayes Shrinkage Parameters (`outputs/shrinkage_params.json`)
Estimated via one-way random-effects variance decomposition (`k = sigma2_within / sigma2_between`) across players with `>= 8` high-pressure matches using winsorised (1st–99th pct) per-match rates (`m_bf >= 4` batters, `m_leg >= 4` bowlers):

- **Batting (`HP RAE100`)**:
  - `sigma2_within_match = 4064.25`, `sigma2_between_match = 223.59`, winsor bounds `[-128.59, 206.45]`.
  - Optimal EB ball-equivalent shrinkage constant: **`k = 206.0` balls** (prior mean `mu = +7.51 RAE100` across `hp_bf >= 60` pool; non-pressure `k = 206.0`, `mu = +7.76`).
  - Beta-Binomial positive-match consistency prior: `m0 = 8` matches around `mu_pos = 0.5334`.
- **Bowling (`HP Total RSAE24` = runs saved + `12 * WAE`)**:
  - `sigma2_within_match = 881.46`, `sigma2_between_match = 14.50`, winsor bounds `[-66.61, 100.99]`.
  - Optimal EB ball-equivalent shrinkage constant: **`k = 199.6` legal balls** (prior mean `mu = -0.55 Total RSAE24` across `hp_legal >= 60` pool; non-pressure `mu = -1.03`).
  - Beta-Binomial positive-match consistency prior: `m0 = 8` matches around `mu_pos = 0.4210`.

## 2. Eligibility Thresholds & Recent Activity Curve (`outputs/eligibility_scan.csv`)
Pool size (`n_eligible`) across `min_hp_balls` (with `min_hp_matches >= 10` and `last_year >= 2025`):
- **Batters**: `60b -> 72`, `80b -> 60`, `100b -> 45`, **`120b -> 32` (Default)**, `150b -> 24`, `180b -> 15`.
- **Bowlers**: `60b -> 79`, `80b -> 71`, **`100b -> 59` (Default)**, `120b -> 45`, `150b -> 26`, `180b -> 15`.
- **Recent-activity filter (`last_year >= 2025`)**: Removes retired/inactive players before IPL 2026–27 auction decisions (e.g., excludes Mohammad Rizwan 245 HP balls last_year=2024, Matthew Wade 127 HP balls last_year=2024, Tim Southee 107 HP balls last_year=2024).
- **Near-miss watch-list (active 2025–26, just below `120` / `100` balls)**:
  - *Batters*: Prabhsimran Singh (`119` balls, EB `+16.73`), Rovman Powell (`113` balls, EB `+18.27`), Heinrich Klaasen (`96` balls, EB `+14.89`).
  - *Bowlers*: Abrar Ahmed (`99` balls, `9` matches), Mohsin Khan (`95` balls, EB `+8.02`), Patrick Cummins (`93` balls, EB `+0.48`).
- Cutoff sensitivity (`80b/8m`, `150b/12m`, and `all 2022–26`) is quantified in Stage 4 (`outputs/robustness_summary.csv`). See `outputs/figures/eligibility_elbow.png`.
