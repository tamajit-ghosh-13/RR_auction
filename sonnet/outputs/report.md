# SupeRR Selector Season 2 (Round 1): Methodology & Pressure Rankings Report (`sonnet`)

## 0. Executive Summary
[HUMAN: rewrite in your words — keep verified numbers intact]

To identify the top 10 batters and top 10 bowlers under genuine match pressure across **2022–2026 IPL and senior T20I cricket** (`837` clean IPL+T20I matches; `189,555` non-DLS deliveries), we replace ad-hoc "death-overs-only" heuristics with a symmetric, strictly pre-delivery **Expected Leverage Index (`LI = E[|ΔWP|]`)** derived from 5-fold match-grouped Win Probability models (`AUC = 0.9003` Innings 2, `0.6888` Innings 1). Deliveries at or above the **90th percentile (`LI >= 1.677`, `mean LI = 2.508`, `n = 18,956`)** define High Pressure identically for batter and bowler, capturing moments with both higher run tempo (`8.98` vs `8.69 rpo`) and higher wicket hazard (`6.06%` vs `5.47%`).

Player performance under pressure is evaluated relative to **format-, state-, venue-, and opposition-adjusted Ridge expectations** (`RAE100` for batters, `Total RSAE24 = Runs Saved + 12 * WAE` for bowlers), combined with **own non-pressure baseline delta**, **winsorised per-match consistency**, and **Win Probability Added / extras discipline**, stabilized via **Empirical Bayes shrinkage (`k_bat = 206.0`, `k_bowl = 199.6` balls)** and restricted to active cricketers (`last_year >= 2025`, `>= 10` HP matches, `>= 120` HP balls batting / `>= 100` legal HP balls bowling).

**Headline Top 10 Batters**: Rinku Singh (`97.9%` bootstrap Top-10 certainty), Yashasvi Jaiswal (`89.4%`), Abhishek Sharma (`90.0%`), Shreyas Iyer (`76.1%`), Quinton de Kock (`66.9%`), Suryakumar Yadav, Travis Head, Washington Sundar, Venkatesh Iyer, and Sai Sudharsan.  
**Headline Top 10 Bowlers**: Josh Hazlewood (`85.9%` Top-10 certainty), Krunal Pandya (`80.6%`), Harshit Rana, Mohammad Nawaz, Yuzvendra Chahal, Varun Chakravarthy, Saim Ayub, Sunil Narine, Trent Boult, and Rashid Khan.

---

## 1. Defining Pressure — Win Probability Leverage Index (`LI`)
[HUMAN: rewrite in your words — summarize why WP Leverage beats raw over cutoffs]

- **Symmetric Pre-Delivery Formulation**: Using `scripts/build_ball_state.py`, we reconstruct leak-free state before every delivery (`runs_before`, `wkts_in_hand`, `balls_left`, 12-ball prior-smoothed `crr_smooth`, DLS resource-weighted projection/chase cushion, `rrr` clipped `[0, 36]`, `is_ipl`, `knock_out`). Smoothing `crr` over a 12-ball prior eliminates ball-1 denominator volatility spikes.
- **Model Calibration**: Logistic Regression outperformed HistGradientBoosting on 5-fold `GroupKFold(match_id)` out-of-fold LogLoss in both innings (Innings 1: `0.6363` vs `0.6464`; Innings 2 repaired target: `0.3946` vs `0.4249`, `AUC = 0.9003`). Repairing chaser targets (`13.37%` of non-DLS 2nd-innings rows) improves Innings 2 OOF AUC (`0.8954 -> 0.9003`), with `Spearman rho = 0.9554` between repaired and raw LI.
- **Ex-Ante Expected Swing (`LI`)**: Evaluating counterfactual transitions over `{0, 1, 2, 4, 6, W}` weighted by `(innings, phase, is_ipl)` empirical rates produces `LI = E[|WP_next - WP_now|]` normalized to `mean = 1.000` (`75th = 1.296`, `90th = 1.677`, `95th = 2.074`). Of `LI >= 90th pct` deliveries, `79.24%` arise in 2nd-innings chases and `20.76%` in high-leverage 1st-innings situations.

![Leverage Index Distribution and Separation](figures/li_distribution.png)
![2nd Innings Leverage Heatmap](figures/pressure_heatmap_chase.png)

---

## 2. Data Discipline, Context Baselines & Fairness Across IPL vs T20I
[HUMAN: rewrite in your words — explain format baselines, opposition Ridge, and data gotchas]

- **Schema Guardrails Verified**: Excluded Super Overs (`38` rows across 6 matches), `dls_flag == 1` matches (`34` matches / `4,433` rows), and two Emerging/A-Team tournaments (`comp_id` `2670`, `3289` — `30` matches caught via explicit IPL IDs `{1358, 1715, 2193, 2725, 3298}`). All player joins use canonical `player_id` (preserving 3 homonym pairs including `Rashid Khan 4722 vs 20172` and merging 4 verified split IDs). Batting dismissals use `dismissed_player_id` (capturing non-striker run-outs), while bowler wickets exclude `RunOut`, `Retire Out`, and obstructing the field.
- **Format Scoring Environments (`outputs/format_baselines.csv`)**: IPL scoring averages `+0.8–1.0 rpo` higher than T20I across all phases (e.g., Inn 2 Death `10.26` vs `9.22 rpo`) with lower wicket rates (`7.74%` vs `8.90%`).
- **Opposition-Adjusted Ridge Model**: Out-of-fold sparse Ridge (`outcome ~ context + striker_id + bowler_id`, `alpha = 150` runs / `250` wickets) adjusts each player's expected baseline for the opponent's bowling or batting quality (`opp_bwl std = 0.0954 runs/ball`, `opp_bat std = 0.1101 runs/ball`).

![WP Calibration](figures/wp_calibration.png)
![IPL vs T20I High-Pressure Volume](figures/ipl_vs_t20i_contrib.png)

---

## 3. Four-Pillar Performance Scoring, Empirical Bayes Shrinkage & Eligibility
[HUMAN: rewrite in your words]

Within the clean high-pressure (`LI >= 90th pct`) and non-pressure (`LI < 90th pct`) pools, each player is scored across four standardized pillars (`50% / 15% / 25% / 10%`):
1. **Primary Value (`50%`)**: Batters use EB-shrunk **`RAE100`** (`100 * sum(bat_runs - xRuns_adj) / HP_BF`); Bowlers use EB-shrunk **`Total RSAE24`** (`24 * sum((xBwlRuns_adj - bwl_runs) + 12 * (wkt - xWkt_adj)) / HP_Legal_Balls`).
2. **Own-Baseline Pressure Lift (`15%`)**: `EB_HP - EB_NonHP`, isolating whether a player elevates or degrades relative to their normal-overs baseline.
3. **Winsorised Match Consistency (`25%`)**: Equal blend of Beta-Binomial positive-match rate (`m0 = 8`) and winsorised (1st–99th pct) per-match Sharpe stability (`m_bf >= 4` / `m_leg >= 4`).
4. **Win Probability & Discipline (`10%`)**: `EB WPA100` for batters; `50% EB WPA_saved_24 + 50% EB Extras Discipline Saved` for bowlers.

**Empirical Bayes & Eligibility**: Match-ANOVA variance decomposition sets **`k_bat = 206.0` balls** and **`k_bowl = 199.6` legal balls**. Requiring `last_year >= 2025`, `>= 10` HP matches, and `>= 120` HP balls faced (`32` eligible batters) / `>= 100` HP legal balls (`59` eligible bowlers) removes retired 2022–24 profiles (Wade, Rizwan, Southee) while retaining meaningful sample floors. Near-miss watchlist players (`Prabhsimran Singh 119b`, `Rovman Powell 113b`, `Heinrich Klaasen 96b`, `Mohsin Khan 95b`) are documented in `outputs/eligibility.md`.

![Shrinkage Before vs After](figures/shrinkage_before_after.png)
![Eligibility Curve](figures/eligibility_elbow.png)

---

## 4. Final Top 10 Batters & Top 10 Bowlers Under Pressure
[HUMAN: rewrite in your words — match dropdown submission order 1-to-1 with these tables]

### Top 10 Batters Under Pressure (Exact Dropdown Order)
| Rank | Player | ID | HP Matches | HP BF | HP SR | Raw RAE100 | EB RAE100 | Own Delta | Pos Match EB | EB WPA100 | Score | 1,000-Boot P(Top10) [95% Rank CI] |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | **Rinku Singh** | 4708 | 15 | 123 | 188.6 | +48.3 | +22.8 | +22.7 | 0.727 | +1.29 | 81.3 | **97.9%** `[1.0, 10.0]` Lock |
| 2 | **Yashasvi Jaiswal** | 6819 | 27 | 194 | 174.7 | +35.6 | +21.1 | +11.7 | 0.651 | +0.06 | 71.3 | **89.4%** `[1.0, 18.0]` Likely |
| 3 | **Abhishek Sharma** | 6281 | 31 | 181 | 179.6 | +43.0 | +24.1 | -18.8 | 0.688 | +0.49 | 69.0 | **90.0%** `[1.0, 16.0]` Lock |
| 4 | **Shreyas Iyer** | 3647 | 21 | 194 | 163.4 | +18.4 | +12.8 | +3.3 | 0.664 | +1.67 | 64.3 | **76.1%** `[1.0, 21.0]` Likely |
| 5 | **Quinton de Kock** | 2101 | 18 | 165 | 173.3 | +28.2 | +16.7 | +9.6 | 0.540 | +0.31 | 63.6 | **66.9%** `[1.0, 25.0]` Likely |
| 6 | **Suryakumar Yadav** | 1699 | 25 | 181 | 171.3 | +28.5 | +17.3 | -8.3 | 0.531 | +0.75 | 60.7 | **52.5%** `[1.0, 31.0]` Borderline |
| 7 | **Travis Head** | 2367 | 16 | 123 | 171.5 | +31.5 | +16.5 | -13.2 | 0.540 | +1.53 | 60.1 | **54.8%** `[2.0, 27.0]` Borderline |
| 8 | **Washington Sundar** | 4823 | 10 | 160 | 142.5 | +5.5 | +6.6 | +16.7 | 0.545 | +1.80 | 57.9 | **51.7%** `[3.0, 24.0]` Borderline |
| 9 | **Venkatesh Iyer** | 7544 | 11 | 148 | 145.3 | +15.3 | +10.8 | +1.6 | 0.604 | -0.01 | 56.3 | **46.6%** `[3.0, 26.0]` Borderline |
| 10 | **Sai Sudharsan** | 23450 | 16 | 200 | 155.0 | +6.5 | +7.0 | +8.7 | 0.593 | +1.13 | 54.8 | **49.7%** `[3.0, 26.0]` Borderline |

### Top 10 Bowlers Under Pressure (Exact Dropdown Order)
| Rank | Player | ID | Style | HP Matches | HP Legal | Wkts | HP Econ | Raw RSAE24 | EB RSAE24 | Own Delta | Pos Match EB | Score | 1,000-Boot P(Top10) [95% Rank CI] |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | **Josh Hazlewood** | 830 | Pace | 21 | 175 | 18 | 8.43 | +15.10 | +6.76 | +5.93 | 0.655 | 81.1 | **85.9%** `[1.0, 23.0]` Likely |
| 2 | **Krunal Pandya** | 4219 | Spin | 16 | 121 | 9 | 6.00 | +16.44 | +5.87 | +6.49 | 0.576 | 77.1 | **80.6%** `[1.0, 25.0]` Likely |
| 3 | **Harshit Rana** | 29888 | Pace | 16 | 143 | 14 | 8.98 | +10.70 | +4.15 | +6.47 | 0.562 | 71.2 | **63.4%** `[1.0, 32.0]` Borderline |
| 4 | **Mohammad Nawaz** | 2490 | Spin | 13 | 146 | 11 | 6.12 | +10.82 | +4.25 | +2.27 | 0.546 | 69.7 | **57.9%** `[1.0, 35.0]` Borderline |
| 5 | **Yuzvendra Chahal** | 1612 | Spin | 25 | 233 | 18 | 8.42 | +8.85 | +4.52 | +4.74 | 0.390 | 66.9 | **37.8%** `[1.0, 49.0]` Borderline |
| 6 | **Varun Chakravarthy** | 6256 | Spin | 18 | 154 | 12 | 7.48 | +10.56 | +4.29 | -0.03 | 0.518 | 66.3 | **46.5%** `[1.0, 45.0]` Borderline |
| 7 | **Saim Ayub** | 7690 | Spin | 10 | 133 | 8 | 5.95 | +6.74 | +2.37 | +4.04 | 0.520 | 66.1 | **39.1%** `[3.0, 30.0]` Borderline |
| 8 | **Sunil Narine** | 781 | Spin | 20 | 167 | 9 | 6.50 | +8.40 | +3.53 | -0.35 | 0.494 | 64.9 | **39.9%** `[1.0, 43.0]` Borderline |
| 9 | **Trent Boult** | 2320 | Pace | 25 | 257 | 16 | 7.75 | +6.55 | +3.45 | +5.55 | 0.495 | 64.8 | **42.5%** `[1.0, 41.0]` Borderline |
| 10 | **Rashid Khan** | 4722 | Spin | 24 | 297 | 20 | 6.97 | +6.31 | +3.56 | +1.52 | 0.479 | 63.6 | **39.5%** `[2.0, 40.0]` Borderline |

![Top 10 Component Breakdown](figures/component_bars_top10.png)

---

## 5. Robustness, Limitations & Open Decision Gates
[HUMAN: rewrite in your words — be candid about split-half variance and Lens B divergence]

- **Stability Strengths**: Rankings are invariant to `±10%` pillar weight changes (`rho = 0.987–0.998`, `9–10/10` overlap), opposition Ridge toggling (`rho = 0.986–0.990`), LI/target boundary noise (`rho = 0.956–0.967`), and Leave-One-Season-Out (`min rho = 0.834–0.849`). Red-team independent recomputation matched `6/6` sampled Top-10 players identically from `ball_by_ball.csv`, and `10/10` batters + `10/10` bowlers are verified dropdown-valid in `competition_team_player_mapping.csv`.
- **Transparent Limitations**:
  1. *Sample-size noise at strict `LI >= 90th`*: Odd/even match split-half yields `rho = 0.294` (batters) / `0.010` (bowlers) because halving the top-10% pool leaves `~60–90` balls per player; widening to `LI >= 75th pct` improves split coverage while modestly shifting rankings (`rho = 0.713` bat, `0.591` bowl).
  2. *Lens A vs Lens B*: Transparent cricket rules (`rho = 0.126–0.235`) weigh 1st-innings middle/death collapse overs more heavily than WP Leverage Index.
  3. *Format dependence*: `Sai Sudharsan`, `Krunal Pandya`, `Sunil Narine` (`100%` IPL) and `Mohammad Nawaz`, `Saim Ayub` (`0%` IPL) rely primarily on one format.
  4. *Reconstructed `team_runs` note*: `scripts/build_ball_state.py` omits `extras1_runs` (`MAE = 2.17 runs` vs `matches.result` before target repair), whereas Stage 1 profiling confirmed `runs + extras1_runs + extras_2_runs` matches `303/303` non-DLS run margins (`MAE = 0.00`); target-noise sensitivity (`rho = 0.808–0.967`) shows minor sensitivity around chaser targets.
- **Decision Gates**: All 15 methodological decisions (`D1–D15`) remain logged as `DECISION NEEDED (autonomous default: ...)` in `outputs/DECISIONS.md` for final human review prior to portal upload.

![Bootstrap Rank Confidence Intervals](figures/robustness_rank_ci.png)

---

## 6. Reproducibility Appendix
- **Random Seed**: `SEED = 42` across all `GroupKFold`, Ridge, and 1,000-match bootstrap procedures.
- **Exact Pipeline Commands (`sonnet/`)**:
  1. `../.venv/bin/python scripts/build_ball_state.py --data data/raw --out data/interim/ball_state.csv.gz --bye-runs 1.0`
  2. `../.venv/bin/python scripts/stage1_profile.py`
  3. `../.venv/bin/python scripts/stage2_pressure.py`
  4. `../.venv/bin/python scripts/stage3_ratings.py`
  5. `../.venv/bin/python scripts/stage4_validation.py`
  6. `../.venv/bin/python scripts/stage5_report_charts.py`
  7. `../.venv/bin/python scripts/stage5_audit_checklist.py`
- **Artifacts Generated**: `outputs/data_profile.md`, `outputs/ball_state_checks.md`, `outputs/pressure_definition.md`, `outputs/format_baselines.csv`, `outputs/opposition_adjustment_notes.md`, `outputs/eligibility.md`, `outputs/shrinkage_params.json`, `outputs/batting_ratings.csv`, `outputs/bowling_ratings.csv`, `outputs/final_rankings.csv`, `outputs/robustness_summary.csv`, `outputs/top10_match_audit.md`, `outputs/red_team_checks.json`, `outputs/DECISIONS.md`, `outputs/report.md`, and `outputs/figures/*.png`.
