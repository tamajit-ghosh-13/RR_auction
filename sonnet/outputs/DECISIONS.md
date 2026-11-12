# Decisions Log (`sonnet` Pipeline)

Status convention under **Option 2 (Autonomous Run First, Review After)**:
Every methodological choice uses `sonnet/`'s documented recommended default and is marked `DECISION NEEDED (autonomous default: ...)` for post-run human review and comparison against `argon/`. No decision is marked approved.

---

## Stage 1 — Data Engineering & Profiling (`data-engineer`)

- **D1. `team_runs` & chase target reconstruction (`build_ball_state.py` vs `extras1_runs`)**:
  **DECISION NEEDED (autonomous default: use `scripts/build_ball_state.py` with `--bye-runs 1.0` + target repair for primary run; compare `target_raw` and exact `extras1_runs` totals in Stage 2/4 sensitivity)**
  - *Trade-off*: `build_ball_state.py` is the canonical provided pipeline in `sonnet/scripts/`, yielding 13.37% repaired 2nd-innings rows (`MAE = 2.17 runs` vs `matches.result`). Profiling revealed that `runs + extras1_runs + extras_2_runs` in `sonnet/ball_by_ball.csv` reproduces 303/303 non-DLS run-win margins with `MAE = 0.00`. Keeping `build_ball_state.py` preserves strict parity with `sonnet/`'s code while testing exact totals in robustness checks.

- **D2. Treatment of Emerging/A-Team T20 tournaments (`comp_id` `2670` & `3289`)**:
  **DECISION NEEDED (autonomous default: exclude Emerging/A-Team tournaments `2670` and `3289` from IPL & senior T20I rankings/eligibility pool; test inclusion/sensitivity in validation)**
  - *Options*: (a) Exclude (`IPL` = `{1358, 1715, 2193, 2725, 3298}`, `T20I` = senior `match_format == 'T20I'`); (b) Include under a separate `"Other T20"` bucket; (c) Pool with T20I. Exclusion prevents U23/A-team games from inflating senior pressure volume, and keeps clean IPL vs T20I format parity.

- **D3. DLS / Rain-Reduced Matches (`dls_flag == 1`, 34 matches / 4,433 deliveries)**:
  **DECISION NEEDED (autonomous default: exclude `dls_flag == 1` from Win Probability training AND primary player pressure ratings; inspect impact in robustness)**
  - *Trade-off*: Revised-over par targets alter scoring incentives and chase dynamics (`balls_in_innings` 30–114); keeping them out of WP & primary metrics prevents target distortions, while testing inclusion in robustness.

- **D4. Super Overs (`innings` 3 & 4, 38 deliveries across 6 matches) & Tied/No-Result Matches**:
  **DECISION NEEDED (autonomous default: exclude Super Overs from `ball_state` & primary pressure ratings, matching `build_ball_state.py`; track Super Over performances separately as an audit check)**
  - *Trade-off*: Super Overs are the highest-stakes 6 balls in cricket, yet `build_ball_state.py` filters to `innings <= 2` because 1-over rules make standard 20-over WP/LI undefined. Also exclude `batting_won.isna()` (25 no-result/abandoned/tied matches) from WP training while keeping completed-result balls if match was abandoned mid-way? Wait: keep WP training strictly to completed non-DLS matches with known `batting_won`.

- **D5. Player ID Canonicalization (Split IDs vs Homonyms)**:
  **DECISION NEEDED (autonomous default: never group by `player_name`; keep 3 true homonym pairs separate (`Rashid Khan` 4722/20172, `Abdul Samad` 7446/6922, `Haider Ali` 7338/28756) AND merge the 4 confirmed duplicate split IDs `{39444: 8638, 20229: 3083, 28978: 27373, 39479: 29833}`)**
  - *Audit*: Checked all `player_id <-> player_name` pairs; all 4 merged IDs correspond to identical players across senior/A-team or series feeds. `4458` (`Aneurin Donald` / `AHT Donald`) already shares one ID.

- **D6. Classification of `extras_type == 'other'` (264 rows) & `bowl_speed`**:
  **DECISION NEEDED (autonomous default: follow `build_ball_state.py` `is_legal` definition; never use raw `bowl_speed` uncleaned — use `pace_or_spin` and `bowling_type` instead)**
  - *Note*: `bowl_speed` has values from `-1.0` to `1456.1` kph (`77,884` rows `< 50`).

---

## Stage 2 — Pressure Definition (`pressure-modeler`)

- **D7. Win Probability Engine (Logistic Regression vs HistGradientBoosting)**:
  **DECISION NEEDED (autonomous default: Logistic Regression OOF ensemble with smoothed CRR + resource proxy, selected strictly on lower 5-fold GroupKFold LogLoss in both innings)**
  - *Evidence*: Inn 1 LogLoss `0.6363` vs `0.6464` (AUC `0.6888` vs `0.6799`); Inn 2 LogLoss `0.3946` vs `0.4249` (AUC `0.9003` vs `0.8864`).

- **D8. Primary Pressure Lens (Lens A WP Leverage Index vs Lens B Rule Index)**:
  **DECISION NEEDED (autonomous default: Lens A ex-ante `LI = E[|ΔWP|]` normalized to mean=1.0; Lens B rule index tested in Stage 4 robustness)**
  - *Trade-off*: Lens A naturally weighs innings, wickets, RRR, and balls left on a common win-probability scale; Lens B is simpler for human intuition (`rho = 0.209`, Jaccard `0.137`).

- **D9. High-Pressure Threshold Tier (`75th` vs `90th` vs `95th` percentile)**:
  **DECISION NEEDED (autonomous default: `LI >= 90th pct` (`LI >= 1.677`, `n = 18,956` clean deliveries) as primary discrete High-Pressure flag; `75th` (`1.296`) and `95th` (`2.074`) evaluated in Stage 4 robustness)**
  - *Trade-off*: `90th pct` balances sample size (`>=100–120` HP balls per top player) with sharp crunch-time focus (`mean LI = 2.508`, `6.06%` wicket rate, `8.98 rpo`).

- **D10. Repaired Target vs `target_raw` for Innings 2 WP & LI**:
  **DECISION NEEDED (autonomous default: use `build_ball_state.py` repaired `target`; `target_raw` sensitivity tested)**
  - *Evidence*: Repaired target improves Inn 2 OOF AUC (`0.8954 -> 0.9003`) and LogLoss (`0.4034 -> 0.3946`); `rho(LI_rep, LI_raw) = 0.9554`.

---

## Stage 3 — Analyst Metrics, Shrinkage & Eligibility (`batting-analyst`, `bowling-analyst`)

- **D11. Format Parity & Opposition Adjustment**:
  **DECISION NEEDED (autonomous default: train format-aware Context + Joint Batter-Bowler Ridge (`alpha=150` runs, `250` wkts) across `IPL + T20I` to remove `+0.8–1.0 rpo` IPL environment inflation and adjust for opponent bowler/batter strength)**
  - *Alternative*: Context-only baseline without opponent Ridge effects (checked in Stage 4).

- **D12. Bowling Value Unification (Runs Saved + Wickets Above Expected)**:
  **DECISION NEEDED (autonomous default: `Total RSAE24 = Runs Saved + 12.0 * Wickets Above Expected` per 24 legal balls; prevents pure defensive bowlers from outranking strike wicket-takers)**
  - *Alternative*: Pure `RSAE24` runs-saved only (`wkt_run_value = 0`), or `15` runs/wicket.

- **D13. Empirical Bayes Shrinkage Constant (`k`)**:
  **DECISION NEEDED (autonomous default: match-ANOVA empirical Bayes `k_bat = 206.0` balls, `k_bowl = 199.6` balls; Beta-Binomial `m0 = 8` HP matches)**
  - *Note*: Strong shrinkage prevents 120–140 ball hot streaks from sweeping `#1–#10` unchallenged while keeping high-volume stars competitive.

- **D14. Eligibility Cutoffs & Active Recency Window**:
  **DECISION NEEDED (autonomous default: Batters `>= 120 HP balls`, Bowlers `>= 100 HP legal balls`, both `>= 10 HP matches` and `last_year >= 2025`; yields 32 batters and 59 bowlers)**
  - *Trade-off*: Filtering `last_year >= 2025` prevents retired 2022–24 players (`Wade`, `Rizwan`, `Southee`) from occupying auction slots; tightening to `150` drops batters to 24 (removing `Rinku Singh` at 123, `Travis Head` at 123), whereas relaxing to `100` admits `Klaasen` (96 -> still 4 short) and `Powell` (`113`).

- **D15. Composite Pillar Weights**:
  **DECISION NEEDED (autonomous default: `50% EB Performance (RAE100 / Total RSAE24) + 15% Own-Baseline Delta + 25% Winsorised Consistency + 10% WPA / Extras Discipline`)**
  - *Sensitivity*: Evaluated `±10` percentage point corners and 1,000-match cluster bootstrap CIs.
