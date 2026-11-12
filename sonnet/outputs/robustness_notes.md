# Robustness & Stability Notes (`sonnet`)

Summary of all 10 mandatory stress tests in `outputs/robustness_summary.csv` and `outputs/figures/robustness_rank_ci.png`.

## 1. 1,000-Match Cluster Bootstrap Tiers
Resampling `match_id` with replacement (`B = 1,000`, recomputing shrunk RAE100/RSAE24, own-baseline delta, Beta-Binomial consistency, and WPA/discipline per draw):
- **Batters**:
  - *Lock Top 10 (`>=90%`)*: `#1 Rinku Singh` (`97.9%`, 95% rank CI `[1, 10]`), `#3 Abhishek Sharma` (`90.0%`, `[1, 16]`).
  - *Likely Top 10 (`65-89%`)*: `#2 Yashasvi Jaiswal` (`89.4%`, `[1, 18]`), `#4 Shreyas Iyer` (`76.1%`, `[1, 21]`), `#5 Quinton de Kock` (`66.9%`, `[1, 25]`).
  - *Borderline (`25-64%`)*: `#6 Suryakumar Yadav` (`52.5%`), `#7 Travis Head` (`54.8%`), `#8 Washington Sundar` (`51.7%`), `#9 Venkatesh Iyer` (`46.6%`), `#10 Sai Sudharsan` (`49.7%`), tightly contested by `#11 David Miller` (`43.2%`), `#12 Tim David` (`44.6%`), `#13 Jos Buttler` (`34.8%`).
- **Bowlers**:
  - *Likely Top 10 (`65-89%`)*: `#1 Josh Hazlewood` (`85.9%`, `[1, 23]`), `#2 Krunal Pandya` (`80.6%`, `[1, 25]`).
  - *Borderline (`25-64%`)*: `#3 Harshit Rana` (`63.4%`), `#4 Mohammad Nawaz` (`57.9%`), `#6 Varun Chakravarthy` (`46.5%`), `#9 Trent Boult` (`42.5%`), `#8 Sunil Narine` (`39.9%`), `#10 Rashid Khan` (`39.5%`), `#7 Saim Ayub` (`39.1%`), `#5 Yuzvendra Chahal` (`37.8%`), challenged closely by `#11 Mohammed Shami` (`31.4%`), `#12 Kagiso Rabada` (`31.1%`), `#14 Taskin Ahmed` (`36.6%`).

## 2. Structural Stress Tests (`outputs/robustness_summary.csv`)
| Check | Batters `rho` (Top-10 Overlap) | Bowlers `rho` (Top-10 Overlap) | Interpretation |
|---|---:|---:|---|
| Weight perturbations (`±10%` corners) | `0.987–0.996` (`9–10/10`) | `0.994–0.998` (`10/10`) | Essentially invariant to pillar weights |
| Unadjusted (Context) vs Opp-Adj Ridge | `0.986` (`9/10`) | `0.990` (`9/10`) | Small rank swaps only |
| Target/LI ±0.05 noise | `0.956` (`8/10`) | `0.967` (`9/10`) | Stable against boundary target uncertainty |
| `target_raw` vs repaired target | `0.808` (`5/10`) | `0.867` (`7/10`) | Moderate shift; supports repairing chaser targets |
| Cutoffs: all years (`2022-26`) vs `2025+` | `0.9996` (`10/10`) | `1.000` (`10/10`) | Within common pool ordering is identical |
| Cutoffs: relaxed (`80b, 8m`) / strict (`150b`) | `0.999` (`4/10`) / `0.998` (`6/10`) | `0.9998` (`9/10`) / `0.999` (`6/10`) | Admitting 80–115b specialists adds Klaasen/Powell |
| Leave-One-Season-Out (min across 2022–26) | `0.849` (`5/10`) | `0.834` (`5/10`) | Consistent across seasons |
| Temporal split (`2022-24` / `2025-26`) | `0.877` (`4/10`) / `0.621` (`5/10`) | `0.787` (`3/10`) / `0.701` (`6/10`) | Natural player aging & role turnover |
| Format split (`IPL-only` / `T20I-only`) | `0.789` (`3/10`) / `0.800` (`2/10`) | `0.879` (`7/10`) / `0.849` (`2/10`) | Small T20I-only qualifying counts (`n=11, 27`) |
| `LI >= 75th` / `LI >= 95th` | `0.713` (`5/10`) / `0.333` (`2/10`) | `0.591` (`7/10`) / `0.674` (`5/10`) | `95th pct` leaves <65 balls per player (noisy) |
| **Odd/Even Match Split-Half** | **`0.294` (`3/10`)** | **`0.010` (`1/10`)** | **Key Variance Warning**: halving the top-10% LI pool drops each player to ~60–90 balls (7–15 overs), where ball-by-ball variance dominates (`k ~ 200` balls). |
| **Lens B (Rule Index) vs Lens A** | **`0.126` (`1/10`)** | **`0.235` (`2/10`)** | Rule B draws heavily from 1st-innings middle/death overs (`~25%` of dataset), rewarding volume accumulators/defensive death bowlers over 2nd-innings chase specialists. |

**Bottom line on uncertainty**: Point ranks `#1–#5` Batters and `#1–#2` Bowlers are robust; ranks `#6–#15` sit within overlapping bootstrap confidence intervals and should be presented as **Top-10 Tier + Borderline Challengers** rather than deterministic point claims.
