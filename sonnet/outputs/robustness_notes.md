# Robustness & Stability Notes (`C03` Primary: `D1 = bye1_repaired`, `LI >= 75th pct`)

Summary of all 10 mandatory stress tests in `outputs/robustness_summary.csv` and `outputs/figures/robustness_rank_ci.png`, plus 5-combination confirmation under `D1 = bye1_repaired`.

## 1. 1,000-Match Cluster Bootstrap Tiers
Resampling `match_id` with replacement (`B = 1,000`, recomputing shrunk RAE100/RSAE24, own-baseline delta, Beta-Binomial consistency, and WPA/discipline per draw) across the `C03` eligible pool (`83` batters, `93` bowlers):
- **Batters**:
  - *Lock Top 10 (`>=90%`)*: `#1 Vaibhav Sooryavanshi` (`98.0%`, 95% rank CI `[1.0, 9.0]`), `#2 Suryakumar Yadav` (`92.0%`, `[1.0, 15.0]`).
  - *Likely Top 10 (`65–89%`)*: `#4 Travis Head` (`71.1%`, `[1.0, 38.0]`), `#6 Abhishek Sharma` (`70.0%`, `[2.0, 32.0]`).
  - *Borderline (`25–64%`)*: `#3 Priyansh Arya` (`64.0%`, `[1.0, 53.0]`), `#8 Jitesh Sharma` (`60.5%`, `[2.0, 37.0]`), `#5 Heinrich Klaasen` (`59.9%`, `[2.0, 36.0]`), `#7 Rinku Singh` (`57.2%`, `[3.0, 27.0]`), `#9 Yashasvi Jaiswal` (`51.7%`, `[2.0, 37.0]`), `#10 Prabhsimran Singh` (`38.4%`, `[3.0, 52.0]`), closely trailed by `#11 Nicholas Pooran` (`28.2%`) and `#12 Josh Inglis` (`25.9%`).
- **Bowlers**:
  - *Likely Top 10 (`65–89%`)*: `#1 Mohammed Shami` (`76.7%`, `[1.0, 28.0]`), `#3 Sunil Narine` (`66.7%`, `[1.0, 37.0]`), `#2 Josh Hazlewood` (`65.5%`, `[1.0, 45.0]`).
  - *Borderline (`25–64%`)*: `#4 Wanindu Hasaranga` (`64.2%`, `[1.0, 40.0]`), `#5 Lockie Ferguson` (`55.0%`, `[1.0, 52.0]`), `#6 Krunal Pandya` (`43.8%`, `[1.0, 53.0]`), `#8 Varun Chakravarthy` (`33.4%`, `[2.0, 64.0]`), `#7 Harshit Rana` (`31.2%`, `[2.0, 57.0]`), `#10 Rashid Khan` (`30.7%`, `[2.0, 53.0]`), `#9 Trent Boult` (`28.0%`, `[2.0, 58.0]`), with `#11 Patrick Cummins` (`30.4%`) and `#13 Rahul Chahar` (`26.2%`) in the challenger band.

## 2. Structural Stress Tests (`outputs/robustness_summary.csv`)
| Check | Batters `rho` (Top-10 Overlap) | Bowlers `rho` (Top-10 Overlap) | Interpretation |
|---|---:|---:|---|
| **Weights +10% Consist (`C12`: `40/15/35/10`)** | **`0.9980` (`10/10`)** | **`0.9957` (`9/10`)** | Statistically tied between `C03` and `C12` consistency tilt |
| Other weight perturbations (`60/10/20/10`, `45/15/20/20`) | `0.9868–0.9972` (`9/10`) | `0.9927–0.9949` (`9–10/10`) | Essentially invariant to pillar weight tweaks |
| Unadjusted (Context) vs Opp-Adj Ridge | `0.9802` (`9/10`) | `0.9865` (`10/10`) | Minimal rank swaps from opposition Ridge |
| Cutoffs: relaxed (`140b/120b, 10m`) / strict (`200b/180b, 14m`) / all years | `0.9996–0.9998` (`9/10`) | `0.9997–1.0000` (`9–10/10`) | Pool stability is invariant across eligibility perturbations |
| Target/LI ±0.05 noise & `target_raw` | `0.9665–0.9691` (`9/10`) | `0.9075–0.9492` (`7–9/10`) | Stable against chase target noise |
| Leave-One-Season-Out (min across 2022–26) | `0.8860` (`6/10`) | `0.8744` (`6/10`) | No single season drives the leaderboard |
| Format split (`IPL-only` / `T20I-only`) | `0.9375` (`7/10`) / `0.7975` (`2/10`) | `0.9218` (`9/10`) / `0.8548` (`3/10`) | Strong IPL alignment (`83–93` pool); smaller T20I-only pool (`n=48, 52`) |
| Temporal split (`2022-24` / `2025-26`) | `0.8536` (`4/10`) / `0.8404` (`6/10`) | `0.8388` (`5/10`) / `0.5821` (`4/10`) | Natural squad turnover & emergence of 2025–26 stars |
| `LI >= 90th` (`C01`) / `LI >= 95th` (`C10`) | `0.7133` (`5/10`) / `0.4857` (`1/10`) | `0.5908` (`7/10`) / `0.4663` (`4/10`) | Strict tails leave smaller ball counts |
| **Odd/Even Match Split-Half** | **`0.2603`** (`n=66`) | **`0.2011`** (`n=84`) | **Both batting & bowling clearly positive** (`SE ~ 0.1` for `n ~ 85`); `LI >= 90th` collapses bowling to `0.0186` and `LI >= 95th` collapses batting to `-0.1353`. |
| **Lens B (Rule Index, `C11`) vs Lens A** | `0.3983` (`1/10`) | `0.3910` (`2/10`) | Rule B elevates 1st-innings middle/death containment overs rather than chase win-probability swings. |
