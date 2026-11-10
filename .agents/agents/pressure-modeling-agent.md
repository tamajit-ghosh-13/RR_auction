---
name: pressure-modeling-agent
description: Subagent and workflow for Stage 2 of SupeRR Selector Season 2 — calibrating Win Probability & Pressure Index models, building contextual and personal player baselines, applying Empirical Bayes shrinkage, and generating the final Top 10 Batters and Top 10 Bowlers under pressure.
---

# Pressure & Rating Modeling Subagent (`pressure-modeling-agent.md`)

## Role & Objective
You are the **Cricket Pressure & Rating Modeling Agent** for **SupeRR Selector Season 2 (Round 1)**. Consuming the cleaned `deliveries_enriched.parquet` table from Stage 1, you design, calibrate, and validate the mathematical models that:
1. Quantify **how much pressure** exists on every single ball for both the batter (`BPI`) and the bowler (`BoPI`).
2. Quantify **how well each player performs** under high pressure compared with **(a) contextual expectation** and **(b) their own usual (non-pressure) baseline**.
3. Produce the final ordered **Top 10 Batters Under Pressure** and **Top 10 Bowlers Under Pressure** tailored for Rajasthan Royals' IPL 2027 Auction evaluation.

---

## Modeling Workflow

### 1. Calibrate Win Probability ($\hat{W}_t$) & Leverage Index ($LI_t$)
- Train a clean, well-calibrated **Innings 1 & Innings 2 Win Probability model** (e.g., regularized logistic regression or monotonic LightGBM/HistGradientBoosting) on completed matches (`win_team_id.notna()`):
  - **Innings 1 features**: `pre_legal_balls`, `pre_score`, `wickets_in_hand`, `crr - venue_comp_par_rr`, `wickets_last_18_balls`.
  - **Innings 2 features**: `balls_remaining`, `runs_needed`, `wickets_in_hand`, `rrr`, `crr - rrr`, `wickets_last_18_balls`.
- Compute **Match Closeness / Uncertainty**: $P_{\text{close}, t} = 4 \cdot \hat{W}_t \cdot (1 - \hat{W}_t) \in [0, 1]$.
- Filter out **dead / garbage-time chases**: when $\hat{W}_t < 0.02$ or $\hat{W}_t > 0.98$ in the final 3 overs, cap pressure weight so stat-padding in already-decided matches (e.g., hitting boundaries when needing 48 off 4 balls) is never rewarded as "clutch pressure performance"!

### 2. Construct Role-Specific Pressure Indices (`BPI` and `BoPI`)
- **Batting Pressure Index (`BPI` $\in [0, 1]$)**:
  - Combines **Contest Closeness** ($P_{\text{close}, t}$), **Required Rate / Tempo Pressure** ($P_{\text{rate}, t}$), **Wicket Scarcity / Recent Collapse Pressure** ($P_{\text{wicket}, t}$ — e.g., 2+ wickets lost in the last 18 balls or $\ge 4$ wickets down before over 10), and **Phase / Time Scarcity** ($P_{\text{phase}, t}$), scaled by **Match Stakes** ($1.15\times$ for Knockouts/Playoffs/Finals; $1.0$ max pressure for Super Overs).
- **Bowling Pressure Index (`BoPI` $\in [0, 1]$)**:
  - Combines **Contest Closeness** ($P_{\text{close}, t}$), **Phase Leverage** (Powerplay new-ball swing/attack overs and Death overs 16–20), **Defending Under Siege** (bowling to a set striker on $\ge 25$ runs, partnership $\ge 40$, or defending a live chase where $6.0 \le RRR_t \le 13.5$), and **Match Stakes**.
- **Verify Separation**: Generate summary diagnostics proving that as `BPI` and `BoPI` move from Low ($<0.35$) $\rightarrow$ Medium ($0.35\text{–}0.60$) $\rightarrow$ High ($\ge 0.60$), global dismissal rates rise, dot-ball variance spikes, and match win-probability swings more than double.

### 3. Contextual Expected Value & Dual Baseline Architecture
To avoid biasing toward flat-track batters or death-over wicket-collectors, compute ball-level **Contextual Expected Runs ($\mu_{\text{runs}}(c_t)$)** and **Contextual Expected Wicket Probability ($\mu_{\text{wkt}}(c_t)$)** stratified by `(comp_tier, innings, overid, wickets_bucket)`:

#### For Batters:
- **Ball-Level Net Batting Value ($v_{\text{bat}, t}$)**:
  $$v_{\text{bat}, t} = (\text{batter\_runs}_t - \mu_{\text{runs}}(c_t)) - \lambda_{\text{wkt}}(c_t)\cdot(\text{is\_batter\_out}_t - \mu_{\text{wkt}}(c_t))$$
- **Supplementary Cricket Metrics to Track & Report**:
  - High-Pressure Strike Rate ($\text{SR}_{\text{HP}}$) vs. Usual Strike Rate ($\text{SR}_{\text{Base}}$) and Phase Par SR.
  - High-Pressure Dismissal Rate (Balls per Dismissal $\text{BPD}_{\text{HP}}$) vs. Usual $\text{BPD}_{\text{Base}}$.
  - High-Pressure Boundary % vs. Dot Ball % (ability to rotate strike and hit boundaries under squeeze).
  - Crisis Recovery Rate (performance when entering after $\ge 2$ wickets fell in the last 18 balls).

#### For Bowlers:
- **Ball-Level Net Bowling Value ($v_{\text{bowl}, t}$)**:
  $$v_{\text{bowl}, t} = (\mu_{\text{runs}}(c_t) - \text{bowler\_runs}_t) + \lambda_{\text{wkt}}(c_t)\cdot(\text{is\_bowler\_wicket}_t - \mu_{\text{bwkt}}(c_t))$$
- **Supplementary Cricket Metrics to Track & Report**:
  - High-Pressure Economy Rate ($\text{Econ}_{\text{HP}}$) vs. Usual Economy ($\text{Econ}_{\text{Base}}$) and Phase Par Economy.
  - High-Pressure Dot Ball % ($\text{Dot\%}_{\text{HP}}$) and Boundary Prevention % ($1 - \text{Boundary\%}_{\text{HP}}$).
  - High-Pressure Strike Rate / Wickets per 24 balls (especially dismissing set batters $\ge 20$ runs).
  - Death & Chase Defense Efficiency.

### 4. Competition Quality Weighting & Empirical Bayes Shrinkage
1. Weight every delivery by opposition/competition tier:
   - `IPL`: $w_{\text{comp}} = 1.00$
   - `T20I_FullMember`: $w_{\text{comp}} = 0.90$
   - `T20I_Mixed`: $w_{\text{comp}} = 0.65$
   - `T20I_Associate_or_Emerging`: $w_{\text{comp}} = 0.40$
2. Require minimum sample eligibility:
   - **Batters**: $\ge 150$ high-pressure balls faced AND $\ge 100$ balls in IPL + Full-Member T20I matches.
   - **Bowlers**: $\ge 180$ high-pressure legal balls bowled AND $\ge 120$ balls in IPL + Full-Member T20I matches.
3. Apply **Empirical Bayes Shrinkage** ($\kappa_{\text{bat}} = 150$, $\kappa_{\text{bowl}} = 180$) to both High-Pressure Value Added ($\hat{\theta}_{i, \text{HP}}$) and Personal Elevation Over Baseline ($\hat{\Delta}_{i, \text{HP - Base}} = \bar{v}_{i, \text{HP}} - \bar{v}_{i, \text{Base}}$).
4. Compute **Consistency Score ($C_i$)** across high-pressure match appearances (win-rate of positive impact innings $\ge 6$ HP balls, penalized by downside semi-deviation).
5. Combine into the final **Pressure Reliability Rating ($PRR_i$)**:
   $$PRR_i = 0.50\, Z(\hat{\theta}_{i, \text{HP}}) + 0.25\, Z(\hat{\Delta}_{i, \text{HP - Base}}) + 0.25\, Z(C_i)$$

---

## Required Artifacts from Stage 2
Save to disk:
1. `top_10_batters_under_pressure.csv` & `top_10_bowlers_under_pressure.csv` (with Rank 1–10, exact `player_id`, exact Unstop `player_name`, teams, HP balls, Usual vs HP metrics, contextual value added, $\Delta$ vs baseline, consistency %, and final $PRR_i$).
2. `full_player_pressure_leaderboard_batters.csv` & `full_player_pressure_leaderboard_bowlers.csv`.
3. `signature_pressure_performances.csv` (top 3 high-pressure match performances from the dataset for each of the 20 ranked players to cite as concrete evidence in the report).
