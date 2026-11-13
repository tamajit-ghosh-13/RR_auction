# Top 10 Bowlers Under Pressure — 5-Pillar Architecture (`C03` Primary, `D1 = bye1_repaired`)

Primary specification: `D1 = bye1_repaired`, `LI >= 75th pct`, `min_hp_legal = 150`, `min_hp_matches = 12`, `last_year >= 2025` (`93` eligible bowlers), format-aware context + joint ridge (`alpha=150` runs, `250` wkts), Empirical Bayes shrinkage (`k = 242.0` legal balls), `Total RSAE24 = Runs Saved + 12.0 * WAE`.
**5-Pillar Weights**: `40% Shrunk Value (with Tier & Rivalry Adjustment) + 20% Post-Boundary Composure & Micro-Execution + 15% Away Turf Lift (Travel Warrior Delta) + 15% Own-Baseline Lift + 10% Match Consistency`.

| Rank | `player_id` | Player | Style | 1000-Boot P(T10) | CI Tier | HP Matches | HP Legal | HP Wkts | HP Econ | EB RSAE24 | PBC EB | Boundary Supp. | Wkt SR/24 | Away $\Delta$ | Own $\Delta$ | Score (0-100) | Flags (`1-Match` / `Format IPL%`) |
|---:|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 4900 | **Wanindu Hasaranga** | Spin | 64.2% | Borderline (8-14) | 31 | 409 | 32 | 8.10 | +4.46 | +0.370 | 84.1% | 1.88 | +1.86 | +3.49 | 72.9 | None (`66.0%` IPL) |
| 2 | 781 | **Sunil Narine** | Spin | 66.7% | Likely Top 10 | 33 | 390 | 19 | 6.37 | +5.04 | +0.378 | 90.3% | 1.17 | +0.50 | +2.64 | 72.6 | Format (`100%` IPL) |
| 3 | 830 | **Josh Hazlewood** | Pace | 65.5% | Likely Top 10 | 36 | 452 | 33 | 8.02 | +4.62 | +0.284 | 80.1% | 1.75 | +1.06 | +5.61 | 70.6 | None (`73.2%` IPL) |
| 4 | 4692 | **Lockie Ferguson** | Pace | 55.0% | Borderline (8-14) | 30 | 291 | 22 | 8.02 | +3.37 | +0.223 | 81.4% | 1.81 | +1.36 | +6.52 | 67.5 | Single-match (`42.1%`) |
| 5 | 4219 | **Krunal Pandya** | Spin | 43.8% | Borderline (8-14) | 32 | 370 | 18 | 7.04 | +3.03 | +0.216 | 88.9% | 1.17 | +1.47 | +4.49 | 66.6 | Single-match (`47.1%`), Format (`100%` IPL) |
| 6 | 4722 | **Rashid Khan** | Spin | 30.7% | Borderline (8-14) | 48 | 640 | 33 | 6.80 | +2.34 | +0.312 | 89.1% | 1.24 | +3.27 | +1.29 | 65.3 | Single-match (`38.4%`) |
| 7 | 6256 | **Varun Chakravarthy** | Spin | 33.4% | Borderline (8-14) | 42 | 451 | 29 | 7.70 | +3.97 | +0.314 | 84.0% | 1.54 | -0.55 | -0.05 | 64.9 | None (`77.6%` IPL) |
| 8 | 2320 | **Trent Boult** | Pace | 28.0% | Borderline (8-14) | 52 | 532 | 27 | 7.52 | +2.06 | +0.282 | 81.8% | 1.22 | +1.96 | +6.20 | 64.5 | Format (`93.8%` IPL) |
| 9 | 29888 | **Harshit Rana** | Pace | 31.2% | Borderline (8-14) | 26 | 285 | 22 | 8.55 | +3.25 | +0.281 | 79.3% | 1.85 | -4.48 | +7.75 | 63.9 | Single-match (`39.8%`) |
| 10 | 6450 | **Mujeeb Ur Rahman** | Spin | 21.8% | Outside / Volatile | 22 | 259 | 15 | 6.58 | +1.26 | +0.398 | 88.0% | 1.39 | -1.32 | +2.17 | 63.0 | Single-match (`48.2%`), Format (`100%` IPL) |

### Strategic & Technical Highlights
1. **Wanindu Hasaranga (#1)**: Ultimate dual-threat pressure bowler. Highest wicket strike rate among spinners (`1.88` wkts/24), elite post-boundary composure (`PBC = +0.370`), and positive away lift (`+1.86`). No single-match or format flags.
2. **Sunil Narine (#2)**: Extraordinary boundary suppression (`90.3%`) and economy under pressure (`6.37 rpo`). Post-boundary composure (`+0.378`) ensures boundary hits never spiral into big overs.
3. **Josh Hazlewood (#3 — Premier Pace Enforcer)**: 33 HP wickets, exceptional own-baseline lift (`+5.61 Total RSAE24`), strong away delta (`+1.06`), and elite consistency (`65.5%` bootstrap P(Top 10)).
4. **Mujeeb Ur Rahman (#10 — Peak Composure)**: Highest EB rebound composure score in the Top 10 (`+0.398`), shutting down opponent momentum immediately after boundaries are struck.
5. **Challengers & The Bumrah Finding**:
   - `#11 Ravindra Jadeja` (`Score = 62.48`, `PBC = +0.371`, `Away Delta = +1.20`, `Own Delta = +3.65`).
   - `#12 Mohammed Shami` (`Score = 61.86`, `31` HP wickets, `EB RSAE = +4.65`, `Own Delta = +7.15`, `Boot P(Top 10) = 76.7%`!). Shami remains the premier pace challenger if single-match risk is penalized.
   - **Jasprit Bumrah (#39)**: Possesses the #1 Post-Boundary Composure across world cricket (`+0.500` across 213 rebound deliveries). However, in High Pressure situations, opposing batters defensively shut down and refuse to take risks against Bumrah (0 wickets conceded, singles taken), lowering his HP wicket rate and causing an own-baseline drop ($\Delta_{\text{Pressure}} = -8.36$). This "Bumrah Suppression Paradox" is documented in the auction intelligence brief.
