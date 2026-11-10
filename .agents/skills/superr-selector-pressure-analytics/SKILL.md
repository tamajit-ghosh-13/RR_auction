---
name: superr-selector-pressure-analytics
description: Domain skill for Rajasthan Royals SupeRR Selector Season 2 (Round 1). Provides exact data cleaning rules, ball-by-ball state reconstruction, continuous & discrete Pressure Index models, contextual expected value (xRuns/xWickets), Empirical Bayes shrinkage, and Top-10 ranking recipes for IPL + T20I data (2022–2026).
---

# SupeRR Selector Season 2 — Cricket Pressure Analytics Skill (`SKILL.md`)

Use this skill whenever analyzing the SupeRR Selector Season 2 dataset, engineering ball-by-ball match states, defining batting/bowling pressure, computing player baselines, or ranking the Top 10 Batters and Top 10 Bowlers under pressure.

---

## 1. Canonical Data Loading & Forensic Cleaning Recipe

Always execute this exact preprocessing pipeline first so that `extras1_runs`, legal ball counters, bowler wickets, DLS targets, and split player IDs are handled cleanly:

```python
import numpy as np
import pandas as pd

SPLIT_ID_MAP = {
    39444: 8638,   # Basil Hameed (UAE)
    20229: 3083,   # Mohammad Ali (PAK)
    28978: 27373,  # Muhammad Farooq (UAE)
    39479: 29833,  # Bashir Ahmad (AFG)
}

IPL_COMP_IDS = {1358, 1715, 2193, 2725, 3298}  # IPL 2022, 2023, 2024, 2025, 2026
EMERGING_COMP_IDS = {2670, 3289}               # Emerging Teams Asia Cup 2024, Rising Stars 2025

FULL_MEMBER_TEAMS = {
    "India", "Australia", "England", "South Africa", "New Zealand",
    "Pakistan", "Sri Lanka", "West Indies", "Bangladesh", "Afghanistan",
    "Ireland", "Zimbabwe"
}

BOWLER_WICKET_TYPES = {"Caught", "Bowled", "LBW", "Stump", "Hit Wicket"}


def convert_cricket_overs_to_balls(overs_val: float) -> int:
    """Convert cricket notation (e.g. 14.3 overs -> 14*6 + 3 = 87 balls)."""
    if pd.isna(overs_val):
        return 120
    whole_overs = int(np.floor(overs_val + 1e-9))
    rem_balls = int(np.round((overs_val - whole_overs) * 10))
    if rem_balls >= 6:
        return int(np.round(overs_val * 6))
    return whole_overs * 6 + rem_balls


def load_and_clean_superr_data(data_dir: str = "."):
    comp = pd.read_csv(f"{data_dir}/competitions.csv")
    teams = pd.read_csv(f"{data_dir}/teams.csv")
    matches = pd.read_csv(f"{data_dir}/matches.csv")
    mapping = pd.read_csv(f"{data_dir}/competition_team_player_mapping.csv")
    xi = pd.read_csv(f"{data_dir}/playing_eleven.csv")
    bbb = pd.read_csv(f"{data_dir}/ball_by_ball.csv", low_memory=False)

    # 1. Canonicalize split player IDs across all tables
    for col in ["striker_id", "non_striker_id", "bowler_id", "dismissed_player_id"]:
        bbb[col] = bbb[col].replace(SPLIT_ID_MAP)
    mapping["player_id"] = mapping["player_id"].replace(SPLIT_ID_MAP)
    xi["player_id"] = xi["player_id"].replace(SPLIT_ID_MAP)

    # 2. Fix runs & extras (NEVER sum extras1_runs!)
    is_non_bat_extra = bbb["extras_type"].isin(["wide", "byes", "legbyes", "Penalty"])
    bbb["batter_runs"] = np.where(is_non_bat_extra, 0, bbb["runs"])

    bbb["extra_runs"] = np.where(
        bbb["extras_type"].notna() & (bbb["extras_type"] != "Penalty"),
        1 + bbb["extras_2_runs"],
        np.where(bbb["extras_type"] == "Penalty", 5, 0),
    )
    bbb["total_runs"] = bbb["batter_runs"] + bbb["extra_runs"]

    is_bowler_extra = bbb["extras_type"].isin(["wide", "Overstep", "other"])
    bbb["bowler_runs"] = bbb["batter_runs"] + np.where(
        is_bowler_extra, 1 + bbb["extras_2_runs"], 0
    )

    # 3. Legal delivery flags
    bbb["is_legal_ball"] = ~bbb["extras_type"].isin(["wide", "Overstep", "other", "Penalty"])
    bbb["is_batter_ball"] = ~bbb["extras_type"].isin(["wide", "Penalty"])
    bbb["is_bowler_ball"] = bbb["is_legal_ball"]

    # 4. Wicket attribution flags
    bbb["is_team_wicket"] = bbb["is_wicket"].astype(int)
    bbb["is_bowler_wicket"] = (
        bbb["is_wicket"] & bbb["dismissal_type"].isin(BOWLER_WICKET_TYPES)
    ).astype(int)
    bbb["is_batter_out"] = (
        bbb["is_wicket"] & ~bbb["dismissal_type"].isin(["Retire Out"])
    ).astype(int)
    bbb["is_dot_batter"] = ((bbb["batter_runs"] == 0) & bbb["is_batter_ball"]).astype(int)
    bbb["is_dot_bowler"] = ((bbb["bowler_runs"] == 0) & bbb["is_bowler_ball"]).astype(int)
    bbb["is_boundary"] = (bbb["is_four"] | bbb["is_six"]).astype(int)

    # 5. Clean bowl_speed (sentinel <= 0 and corrupt values > 165)
    bbb["clean_bowl_speed"] = np.where(
        (bbb["bowl_speed"] >= 65.0) & (bbb["bowl_speed"] <= 165.0),
        bbb["bowl_speed"],
        np.nan,
    )

    return comp, teams, matches, mapping, xi, bbb
```

---

## 2. Reconstructing Ball-by-Ball Match State

To measure pressure on delivery $t$, you must know the exact match state **immediately prior to delivery $t$** (`pre_score`, `pre_wickets`, `pre_legal_balls`, `balls_remaining`, `runs_needed`, `RRR`):

```python
def build_match_state(bbb: pd.DataFrame, matches: pd.DataFrame, comp: pd.DataFrame) -> pd.DataFrame:
    df = bbb.sort_values(["match_id", "innings", "innings_ball_num"]).copy()
    m_meta = matches[[
        "match_id", "comp_id", "match_date", "stage", "venue_id", "venue_country",
        "home_team_id", "home_team", "away_team_id", "away_team",
        "first_inn_revised_overs", "second_inn_revised_overs", "revised_target",
        "knock_out", "win_team_id", "result"
    ]].merge(comp[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")

    df = df.merge(m_meta, on="match_id", how="left")

    # Cumulative post-ball state within (match_id, innings)
    grp = df.groupby(["match_id", "innings"], sort=False)
    df["post_score"] = grp["total_runs"].cumsum()
    df["post_wickets"] = grp["is_team_wicket"].cumsum()
    df["post_legal_balls"] = grp["is_legal_ball"].cumsum()

    # Pre-ball state (state entering the delivery)
    df["pre_score"] = df["post_score"] - df["total_runs"]
    df["pre_wickets"] = df["post_wickets"] - df["is_team_wicket"]
    df["pre_legal_balls"] = df["post_legal_balls"] - df["is_legal_ball"].astype(int)
    df["wickets_in_hand"] = np.clip(10 - df["pre_wickets"], 1, 10)

    # First innings total runs per match
    inn1_totals = (
        df[df["innings"] == 1]
        .groupby("match_id")["total_runs"]
        .sum()
        .rename("inn1_total")
    )
    df = df.merge(inn1_totals, on="match_id", how="left")

    # Scheduled balls per innings (accounting for DLS revised overs)
    inn1_max_balls = df["first_inn_revised_overs"].apply(convert_cricket_overs_to_balls)
    inn2_max_balls = df["second_inn_revised_overs"].apply(convert_cricket_overs_to_balls)
    df["max_balls"] = np.where(
        df["innings"] == 1, inn1_max_balls,
        np.where(df["innings"] == 2, inn2_max_balls, 6)
    )
    df["balls_remaining"] = np.clip(df["max_balls"] - df["pre_legal_balls"], 1, 120)

    # Target & Required Run Rate (Innings 2)
    df["target_runs"] = np.where(
        df["innings"] == 2,
        np.where(df["revised_target"].notna(), df["revised_target"], df["inn1_total"] + 1),
        np.nan,
    )
    df["runs_needed"] = np.where(
        df["innings"] == 2,
        np.clip(df["target_runs"] - df["pre_score"], 0, None),
        np.nan,
    )
    df["crr"] = np.where(df["pre_legal_balls"] > 0, df["pre_score"] * 6.0 / df["pre_legal_balls"], 8.0)
    df["rrr"] = np.where(df["innings"] == 2, df["runs_needed"] * 6.0 / df["balls_remaining"], np.nan)

    # Phase tagging
    df["phase"] = np.select(
        [df["overid"] <= 6, df["overid"] <= 15, df["overid"] >= 16],
        ["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"],
        default="Death (16-20)"
    )
    return df
```

---

## 3. Mathematical Formulation of Pressure ($P_t \in [0, 1]$)

A winning submission needs a **principled, cricket-grounded Pressure Index** that works seamlessly across **1st Innings**, **2nd Innings (Chases)**, **Super Overs**, and **both Batting and Bowling**.

### 3.1 Five Core Pressure Dimensions
For every delivery $t$, compute five normalized pressure components in $[0, 1]$:

1. **Required Rate / Tempo Pressure ($P_{\text{rate}, t}$)**:
   - *Innings 2 (Chase)*: Driven by Required Run Rate ($RRR_t$) relative to venue/competition par run rate ($RR_{\text{par}} \approx 8.5$ in IPL, $8.0$ in T20I):
     $$P_{\text{rate}, t}^{(2)} = \sigma\!\left(\frac{RRR_t - RR_{\text{par}}}{2.2}\right) \cdot \mathbb{I}(\text{Match Still Alive})$$
     *(Note: Downweight garbage-time deliveries where $RRR_t > 24$ with $<12$ balls left and win probability $< 1\%$, or walkover chases where $RRR_t < 4.0$ with $\ge 7$ wickets in hand).*
   - *Innings 1 (Setting)*: Driven by scoring behind par trajectory or accelerating in death overs:
     $$P_{\text{rate}, t}^{(1)} = \sigma\!\left(\frac{\text{ParScore}(b_t) - \text{pre\_score}_t}{15.0}\right) \cdot 0.6 + 0.4 \cdot \left(\frac{\text{overid}_t}{20}\right)^2$$

2. **Resource / Wicket Scarcity & Collapse Pressure ($P_{\text{wicket}, t}$)**:
   - Captures both cumulative wickets lost relative to overs elapsed AND recent wickets falling in the last 18 balls (collapse arrest):
     $$P_{\text{wicket}, t} = \text{clip}\!\left(\frac{\text{pre\_wickets}_t}{\text{ExpectedWickets}(b_t) + 1.5} \times 0.5 + 0.25 \times \text{WicketsLast18Balls}_t,\; 0,\; 1\right)$$

3. **Phase & Time-Scarcity Leverage ($P_{\text{phase}, t}$)**:
   - Mistakes become irreversible as `balls_remaining` shrinks. Additionally, new-ball swing in overs 1–3 against top order and death overs 16–20 carry elevated phase leverage:
     $$P_{\text{phase}, t} = 1 - \left(\frac{\text{balls\_remaining}_t}{120}\right)^{0.75}$$

4. **Contest Closeness / Win-Probability Leverage ($P_{\text{close}, t}$)**:
   - Let $\hat{W}_t \in [0, 1]$ be the estimated batting-team win probability entering ball $t$ (fit via logistic regression or gradient boosted trees on `innings`, `runs_needed`, `balls_remaining`, `wickets_in_hand`, `crr - par_rr`).
   - Uncertainty / knife-edge closeness peaks at $\hat{W}_t = 0.5$:
     $$P_{\text{close}, t} = 4 \cdot \hat{W}_t \cdot (1 - \hat{W}_t) \in [0, 1]$$
   - Even better: compute **Empirical Leverage Index ($LI_t$)** as the expected absolute swing in win probability $|\Delta \hat{W}_t|$ across possible outcomes (Wicket, 0, 1, 2, 4, 6) on ball $t$, normalized by the dataset mean $\overline{|\Delta W|}$.

5. **Match Stakes Multiplier ($M_{\text{stakes}}$)**:
   - Playoff/Knockout matches (`knock_out == 1` or `stage` in `['Final', 'Qualifier', 'Eliminator', 'Semi Final', 'Super 4']`) receive a stakes boost ($M_{\text{stakes}} = 1.15$), and Super Overs (`innings` in `[3, 4]`) receive $P_t = 1.0$.

### 3.2 Composite Batting & Bowling Pressure Indices
Combine the components into role-tuned indices:
- **Batting Pressure Index ($BPI_t \in [0, 1]$)**:
  $$BPI_t = \text{clip}\!\Big(M_{\text{stakes}} \cdot \big(0.30\, P_{\text{close}, t} + 0.30\, P_{\text{rate}, t} + 0.25\, P_{\text{wicket}, t} + 0.15\, P_{\text{phase}, t}\big),\; 0,\; 1\Big)$$
- **Bowling Pressure Index ($BoPI_t \in [0, 1]$)**:
  $$BoPI_t = \text{clip}\!\Big(M_{\text{stakes}} \cdot \big(0.35\, P_{\text{close}, t} + 0.30\, P_{\text{phase}, t} + 0.25\, P_{\text{defend}, t} + 0.10\, (1 - P_{\text{wicket}, t})\big),\; 0,\; 1\Big)$$
  where $P_{\text{defend}, t}$ is high when bowling at the death (overs 16–20), bowling to a set batter (striker $\ge 25$ runs or current partnership $\ge 40$), or defending a tight equation in Innings 2 ($6.0 \le RRR_t \le 13.5$).

Define **High-Pressure Zone** as deliveries in the top tertile/quartile ($P_t \ge 0.60$, or top 30% of deliveries) and **Normal/Baseline Zone** as $P_t < 0.60$, while also using continuous $P_t$ weights so no boundary threshold artifact distorts rankings.

---

## 4. Measuring Performance Relative to Usual Baseline & Context

The Problem Statement explicitly requires:
> *"Build a data-driven system that measures how batters and bowlers perform in high-pressure match situations **compared with their usual performance levels**. Use your system to identify and rank the players who deliver most consistently when it matters."*

Therefore, a player's rating MUST combine **three pillars**:
1. **Absolute High-Pressure Excellence (Contextual Value Added under Pressure)**: How much better do they perform under high pressure than an average player in that exact match phase, competition, and wicket state?
2. **Personal Pressure Elevation / Resilience ($\Delta_{\text{self}}$ — Pressure vs. Usual Baseline)**: How well do they maintain or elevate their output under high pressure compared to their *own* non-pressure baseline?
3. **Match-to-Match Consistency ($C_i$)**: How reliably do they deliver positive impact across high-pressure matches (high hit-rate of good outings, low catastrophic failure rate)?

### 4.1 Ball-Level Expected Value ($\text{xRuns}_t$ and $\text{xWicket}_t$)
First, compute contextual expectation $\mu_{\text{runs}}(c_t)$ and $\mu_{\text{wkt}}(c_t)$ stratified by `c_t = (comp_tier, innings, overid, wickets_bucket)`:
- **Net Batting Value per Ball ($v_{\text{bat}, t}$)**:
  $$v_{\text{bat}, t} = \left(\text{batter\_runs}_t - \mu_{\text{runs}}(c_t)\right) - \lambda_{\text{wkt}}(c_t) \cdot \left(\text{is\_batter\_out}_t - \mu_{\text{wkt}}(c_t)\right)$$
  where $\lambda_{\text{wkt}}(c_t)$ is the run value of a wicket in state $c_t$ (typically $\approx 18\text{–}22$ runs in Powerplay/Middle, scaling down to $\approx 6\text{–}12$ runs in overs 17–20).
- **Net Bowling Value per Ball ($v_{\text{bowl}, t}$)**:
  $$v_{\text{bowl}, t} = \left(\mu_{\text{runs}}(c_t) - \text{bowler\_runs}_t\right) + \lambda_{\text{wkt}}(c_t) \cdot \left(\text{is\_bowler\_wicket}_t - \mu_{\text{bwkt}}(c_t)\right)$$

### 4.2 Fair Comparisons: Competition Quality Weights ($w_{\text{comp}}$)
Because this is an **IPL 2027 Auction Strategy** competition for Rajasthan Royals, facing or bowling in the IPL or against Full Member international teams is far harder than bilateral series between lower-ranked Associate teams:
- **IPL (`comp_id` in `[1358, 1715, 2193, 2725, 3298]`)**: $w_{\text{comp}} = 1.00$
- **T20I — Both Teams in `FULL_MEMBER_TEAMS` (or World Cup / Asia Cup Main Draw)**: $w_{\text{comp}} = 0.90$
- **T20I — One Team in `FULL_MEMBER_TEAMS` vs Associate**: $w_{\text{comp}} = 0.65$
- **T20I — Both Teams Associate / Emerging Teams Tournaments (`2670`, `3289`)**: $w_{\text{comp}} = 0.40$

### 4.3 Empirical Bayes Shrinkage (Solving Small Sample Bias)
If a batter hits two sixes in 4 pressure balls, raw averages will falsely rank them #1. Apply **Empirical Bayes (James-Stein / Beta-Binomial / Normal-Normal) shrinkage** toward a conservative replacement prior $\mu_0$:
$$\hat{\theta}_{i, \text{HP}} = \frac{N_{i, \text{HP}}}{N_{i, \text{HP}} + \kappa} \cdot \bar{v}_{i, \text{HP}} + \frac{\kappa}{N_{i, \text{HP}} + \kappa} \cdot \mu_0$$
- Recommended shrinkage constant $\kappa$: $\kappa_{\text{bat}} = 150$ weighted high-pressure balls faced; $\kappa_{\text{bowl}} = 180$ weighted high-pressure legal balls bowled.
- Minimum Eligibility Floor:
  - **Batters**: At least $150$ total high-pressure balls faced (or $\ge 15$ high-pressure innings) AND proven sample in IPL or Full-Member T20Is.
  - **Bowlers**: At least $180$ total high-pressure legal balls bowled (or $\ge 20$ high-pressure innings) AND proven sample in IPL or Full-Member T20Is.

### 4.4 Final Composite Pressure Reliability Rating ($PRR_i$)
For each eligible player $i$:
1. **Shrunk High-Pressure Value Added ($Z(\hat{\theta}_{i, \text{HP}})$)** — 50% weight: Measures elite performance under high pressure against contextual par.
2. **Shrunk Pressure Delta Over Own Usual Baseline ($Z(\hat{\Delta}_{i, \text{HP - Base}})$)** — 25% weight:
   $$\hat{\Delta}_{i, \text{HP - Base}} = \frac{N_{i, \text{eff}}}{N_{i, \text{eff}} + \kappa_\Delta}\left(\bar{v}_{i, \text{HP}} - \bar{v}_{i, \text{Base}}\right)$$
   Rewards players who step up (or refuse to drop off) when pressure spikes compared to their own non-pressure baseline.
3. **Match-Level Consistency & Clutch Win Impact ($Z(C_i)$)** — 25% weight:
   - Fraction of high-pressure match appearances ($\ge 6$ HP balls) where the player posted positive Net Value Added ($v_{i, m, \text{HP}} > 0$), plus lower downside semi-variance.

$$\text{Pressure Reliability Rating } (PRR_i) = 0.50\, Z\!\left(\hat{\theta}_{i, \text{HP}}\right) + 0.25\, Z\!\left(\hat{\Delta}_{i, \text{HP - Base}}\right) + 0.25\, Z(C_i)$$

---

## 5. Mandatory Verification & Sensitivity Protocol
Before locking the Top 10 Batters and Top 10 Bowlers:
1. **Bootstrap Rank Stability**: Resample matches with replacement $B = 500$ times and record each Top-10 player's median rank and 90% confidence interval.
2. **Threshold Sensitivity Check**: Verify Spearman rank correlation ($\rho > 0.90$) when varying the High-Pressure threshold across $P_t \ge 0.55$, $0.60$, $0.65$, and continuous $P_t$-weighted aggregation.
3. **Unstop Dropdown Exact String Match**: Verify every `player_name` in the final Top 10 Batters and Top 10 Bowlers matches `competition_team_player_mapping.csv` character-for-character.
