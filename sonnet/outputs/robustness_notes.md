# Robustness & Stability Notes (`C03` 5-Pillar Architecture: `D1 = bye1_repaired`, `LI >= 75th pct`)

Summary of all 36 mandatory stress tests in `outputs/robustness_summary.csv` and `outputs/figures/robustness_rank_ci.png`, plus 5-combination confirmation under `D1 = bye1_repaired`.

## 1. 1,000-Match Cluster Bootstrap Tiers
Resampling `match_id` with replacement (`B = 1,000`, recomputing shrunk 5-pillar composite per draw) across the `C03` eligible pool (`83` batters, `93` bowlers):
- **Batters**:
  - *Lock Top 10 (`>=90%`)*: `#1 Vaibhav Sooryavanshi` (`98.0%`, 95% rank CI `[1.0, 9.0]`), `#2 Suryakumar Yadav` (`92.0%`, `[1.0, 15.0]`).
  - *Likely Top 10 (`65–89%`)*: `#3 Travis Head` (`71.1%`, `[1.0, 38.0]`), `#4 Abhishek Sharma` (`69.9%`, `[2.0, 32.0]`).
  - *Borderline (`25–64%`)*: `#8 Priyansh Arya` (`64.1%`, `[1.0, 53.0]`), `#7 Jitesh Sharma` (`60.1%`, `[2.0, 37.0]`), `#5 Heinrich Klaasen` (`60.1%`, `[2.0, 36.0]`), `#10 Rinku Singh` (`57.3%`, `[3.0, 27.0]`), `#9 Yashasvi Jaiswal` (`51.4%`, `[2.0, 37.0]`), `#6 Nicholas Pooran` (`28.2%`, `[2.0, 66.0]`), closely followed by `#13 Josh Inglis` (`26.1%`).
- **Bowlers**:
  - *Likely Top 10 (`65–89%`)*: `#2 Sunil Narine` (`66.7%`, `[1.0, 37.0]`), `#3 Josh Hazlewood` (`65.5%`, `[1.0, 45.0]`), plus `#12 Mohammed Shami` (`76.7%`, `[1.0, 28.0]`).
  - *Borderline (`25–64%`)*: `#1 Wanindu Hasaranga` (`64.2%`, `[1.0, 40.0]`), `#4 Lockie Ferguson` (`55.0%`, `[1.0, 52.0]`), `#5 Krunal Pandya` (`43.8%`, `[1.0, 53.0]`), `#7 Varun Chakravarthy` (`33.4%`, `[2.0, 64.0]`), `#9 Harshit Rana` (`31.2%`, `[2.0, 57.0]`), `#6 Rashid Khan` (`30.7%`, `[2.0, 53.0]`), `#8 Trent Boult` (`28.0%`, `[2.0, 58.0]`), with `#15 Patrick Cummins` (`30.4%`) in the challenger band.
  - *Outside / Volatile (`<25%`)*: `#10 Mujeeb Ur Rahman` (`21.8%`, `[3.0, 61.0]`).

## 2. Structural Stress Tests (`outputs/robustness_summary.csv`)
| Check | Batters `rho` (Top-10 Overlap) | Bowlers `rho` (Top-10 Overlap) | Interpretation |
|---|---:|---:|---|
| **Odd/Even Match Split-Half** | **`0.2498`** (`n=66`) | **`0.2399`** (`n=84`) | **Both batting & bowling clearly positive** (`SE ~ 0.1` for `n ~ 85`); `LI >= 90th` collapses bowling to `0.0654` and `LI >= 95th` collapses batting to `-0.1147`. |
| **Weights +10% Consist (`C12`: `40/15/35/10`)** | **`0.9832` (`9/10`)** | **`0.9832` (`9/10`)** | Statistically tied between `C03` and `C12` consistency tilt |
| Other weight perturbations (`60/10/20/10`, `45/15/20/20`) | `0.9829–0.9961` (`10/10`) | `0.9903–0.9953` (`9–10/10`) | Essentially invariant to pillar weight tweaks |
| Unadjusted (Context) vs Opp-Adj Ridge | `0.9872` (`8/10`) | `0.9889` (`9/10`) | Minimal rank swaps from opposition Ridge |
| Cutoffs: relaxed (`140b/120b, 10m`) / strict (`200b/180b, 14m`) / all years | `0.9992–0.9999` (`9–10/10`) | `0.9997–0.9999` (`9–10/10`) | Pool stability is invariant across eligibility perturbations |
| Target/LI ±0.05 noise & `target_raw` | `0.9390–0.9556` (`6–9/10`) | `0.9199–0.9447` (`6–8/10`) | Stable against chase target noise |
| Leave-One-Season-Out (min across 2022–26) | `0.8646` (`5/10`) | `0.8641` (`5/10`) | No single season drives the leaderboard |
| Format split (`IPL-only` / `T20I-only`) | `0.8808` (`8/10`) / `0.8247` (`3/10`) | `0.9047` (`8/10`) / `0.8628` (`4/10`) | Strong IPL alignment (`83–93` pool); smaller T20I-only pool (`n=48, 52`) |
| Temporal split (`2022-24` / `2025-26`) | `0.8335` (`3/10`) / `0.7995` (`6/10`) | `0.8170` (`5/10`) / `0.5397` (`4/10`) | Natural squad turnover & emergence of 2025–26 stars |
| `LI >= 90th` (`C01`) / `LI >= 95th` (`C10`) | `0.6628` (`5/10`) / `0.2191` (`1/10`) | `0.6380` (`7/10`) / `0.5049` (`2/10`) | Strict tails leave smaller ball counts |
| **Lens B (Rule Index, `C11`) vs Lens A** | `0.2854` (`2/10`) | `0.4392` (`3/10`) | Rule B elevates 1st-innings middle/death containment overs rather than chase win-probability swings. |
