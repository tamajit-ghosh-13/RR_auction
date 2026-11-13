# Shrinkage & Eligibility Specification (`C03` Primary: `D1 = bye1_repaired`, `LI >= 75th pct`)

## 1. Empirical Bayes Shrinkage Parameters (`outputs/shrinkage_params.json`)
Estimated via one-way random-effects variance decomposition (`k = sigma2_within / sigma2_between`) across players with `>= 8` high-pressure matches using winsorised (1st–99th pct) per-match rates (`m_bf >= 4` batters, `m_leg >= 4` bowlers):

- **Batting (`HP RAE100`, `LI >= 75th pct`)**:
  - `sigma2_within_match = 3489.03`, `sigma2_between_match = 247.67`, winsor bounds `[-124.06, 189.47]`.
  - Optimal EB ball-equivalent shrinkage constant: **`k = 180.9` balls** (prior mean `mu = +6.17 RAE100` across `hp_bf >= 60` pool; non-pressure prior `mu = +6.77`).
  - Beta-Binomial positive-match consistency prior: `m0 = 8` matches around `mu_pos = 0.5046`.
- **Bowling (`HP Total RSAE24` = runs saved + `12 * WAE`, `LI >= 75th pct`)**:
  - `sigma2_within_match = 692.46`, `sigma2_between_match = 21.54`, winsor bounds `[-61.67, 81.99]`.
  - Optimal EB ball-equivalent shrinkage constant: **`k = 242.0` legal balls** (prior mean `mu = -1.33 Total RSAE24` across `hp_legal >= 60` pool; non-pressure prior `mu = -1.41`).
  - Beta-Binomial positive-match consistency prior: `m0 = 8` matches around `mu_pos = 0.4073`.

## 2. Eligibility Thresholds & Pool Depth (`outputs/eligibility_scan.csv`)
Pool size (`n_eligible`) across `min_hp_balls` with `min_hp_matches >= 12` and `last_year >= 2025` under `is_hp_75`:
- **Batters**: `100b -> 118`, `140b -> 97`, `160b -> 86`, **`180b -> 83` (`C03` Primary)**, `200b -> 69`, `240b -> 49`.
- **Bowlers**: `100b -> 117`, `120b -> 108`, `140b -> 101`, **`150b -> 93` (`C03` Primary)**, `180b -> 82`, `200b -> 73`.
- **Recent-activity filter (`last_year >= 2025`)**: Preserves active IPL 2026–27 auction and T20I selection relevance (with `2022–26` full-history alternative showing `rho = 0.9998` batters, `1.0000` bowlers on common players).
- **Eligibility Check for Missing Stars**: Neither `Jasprit Bumrah` (`43` HP matches, `455` legal HP balls, `last_year = 2026`) nor `Matheesha Pathirana` (`20` HP matches, `207` legal HP balls, `last_year = 2026`) failed eligibility in `C03`. Both cleared the `150`-ball / `12`-match threshold easily (`eligible = True`), finishing **`#39` (`Bumrah`)** and **`#49` (`Pathirana`)** due to negative Wickets Above Expected in the `LI >= 75th pct` tier (`-0.514 WAE/24` and `-0.324 WAE/24`, i.e., `17` vs `26.75` and `13` vs `15.79` expected HP wickets respectively).
- See `outputs/figures/eligibility_elbow.png`.
