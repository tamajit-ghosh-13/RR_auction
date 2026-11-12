# Stage 2 — Pressure Definition (`sonnet`)

Produced by `scripts/stage2_pressure.py` -> `data/interim/ball_pressure.csv.gz` and `outputs/stage2_stats.json`.

## 1. Lens A: Win Probability & Ex-Ante Expected Leverage Index (`LI = E[|ΔWP|]`)

### Win Probability Calibration (5-Fold `GroupKFold(match_id)` OOF)
Trained on non-DLS, completed `IPL + T20I` matches using strictly pre-delivery state features (`balls_left`, `wkts_in_hand`, `runs_before`, 12-ball Bayesian-smoothed `crr_smooth`, DLS resource-weighted projected score / chase cushion, `rrr` clipped `[0, 36]`, `rrr - crr_smooth`, `is_ipl`, `knock_out`). Using smoothed CRR eliminates the classic ball-1 denominator volatility artifact.

| Innings | Model Family | OOF Brier | OOF LogLoss | OOF ROC-AUC | Selected |
|---|---|---:|---:|---:|---|
| Innings 1 (Setting) | Logistic Regression | **0.2229** | **0.6363** | **0.6888** | Yes |
| Innings 1 (Setting) | HistGradientBoosting | 0.2260 | 0.6464 | 0.6799 | — |
| Innings 2 (Repaired Target) | Logistic Regression | **0.1283** | **0.3946** | **0.9003** | Yes |
| Innings 2 (Repaired Target) | HistGradientBoosting | 0.1374 | 0.4249 | 0.8864 | — |
| Innings 2 (`target_raw`) | Logistic Regression | 0.1316 | 0.4034 | 0.8954 | Sensitivity |

Repaired target improves Innings 2 OOF LogLoss (`0.4034 -> 0.3946`) and AUC (`0.8954 -> 0.9003`), with `Spearman rho = 0.9554` between Innings 2 `LI(repaired)` and `LI(target_raw)`.

### Expected Leverage Index (`LI`) & Discrete Tiers
For every delivery state $s$, counterfactual next states $s'_k$ are evaluated across the 6 canonical legal outcomes $\{0, 1, 2, 4, 6, \text{W}\}$ weighted by `(innings, phase, is_ipl)` empirical outcome probabilities, giving `LI_raw = sum_k p_k * |WP(s'_k) - WP(s)|`. Across clean `IPL + T20I` deliveries, `LI` is normalized to `mean = 1.0000`:
- **50th percentile**: `0.888`
- **75th percentile (`is_hp_75`)**: `1.296` (Elevated)
- **90th percentile (`is_hp_90`)**: `1.677` (**Primary High-Pressure Cutoff**)
- **95th percentile (`is_hp_95`)**: `2.074` (Extreme)
- **Max**: `32.53`

Symmetry rule enforced: `li` and `is_hp_*` depend strictly on pre-delivery match state and are identical for batter and bowler.

## 2. Lens B: Transparent Cricket-Logic Index & Agreement Test
- **Binary Rule (`is_hp_rule`)**:
  - *Innings 2*: `(balls_left <= 30 & 8 <= rrr <= 20 & runs_needed > 0)` OR `(30 < balls_left <= 60 & wkts_before >= 3 & 8 <= rrr <= 16)` OR `(wkts_before >= 4 & 7.5 <= rrr <= 15)`.
  - *Innings 1*: `(phase == 'death' & 5 <= wkts_before <= 8)` OR `(phase in ['powerplay','middle'] & wkts_before >= 4 & balls_left >= 42)`.
- **Agreement (`IPL + T20I` clean pool)**:
  - Continuous Spearman `rho(LI, rule_score) = 0.2093`.
  - Binary Jaccard overlap with `is_hp_rule` (`~19-26%` prevalence): `0.1617` (`75th`), `0.1371` (`90th`), `0.1011` (`95th`).
  - *Why they diverge*: Rule B treats many 1st-innings middle/death collapse overs uniformly (~20–24% of Inn 1 balls), whereas calibrated WP-based `LI` assigns only `3.7–4.2%` of 1st-innings balls vs `15.2–18.4%` of 2nd-innings chase balls above the 90th percentile, concentrating directly on pivotal chase swings (`79.2%` of `LI >= 90th` deliveries occur in chases). Stage 4 tests whether player rankings remain robust under Lens B.

## 3. Behavioral Separation & Format Distribution
| LI Bucket | Clean Balls | % Inn 2 | Run Rate (rpo) | Boundary % | Dot % | Wicket % | Mean LI |
|---|---:|---:|---:|---:|---:|---:|---:|
| Low (`<50th`) | 94,777 | 44.75% | 8.69 | 17.51% | 33.64% | 5.47% | 0.523 |
| Medium (`50-75th`) | 47,389 | 31.57% | 8.86 | 18.65% | 33.91% | 5.16% | 1.078 |
| Elevated (`75-90th`) | 28,433 | 62.48% | 8.77 | 18.66% | 34.91% | 4.91% | 1.456 |
| High+Extreme (`>=90th`) | 18,956 | **79.24%** | **8.98** | 18.17% | **32.79%** | **6.06%** | **2.508** |

High+Extreme pressure deliveries show both **higher scoring tempo (`8.98 rpo` vs `8.69`)** and **higher dismissal risk (`6.06%` vs `5.47%`)**, confirming genuine two-sided competitive pressure for both batters and bowlers.

Figures generated:
- `outputs/figures/li_distribution.png`
- `outputs/figures/pressure_heatmap_chase.png`
- `outputs/figures/wp_calibration.png`
