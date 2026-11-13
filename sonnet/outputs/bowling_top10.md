# Top 10 Bowlers Under Pressure — `C03` Primary (`D1 = bye1_repaired`) + 5-Combo Confirmation

Primary spec: `D1 = bye1_repaired`, `LI >= 75th pct`, `min_hp_legal = 150`, `min_hp_matches = 12`, `last_year >= 2025` (`93` eligible bowlers), opposition-adjusted EB-shrunk (`k = 242.0` legal balls), `Total RSAE24 = Runs Saved + 12 * WAE`, weights `50% Total RSAE24 / 15% Own-Delta / 25% Consistency / 10% (Discipline + WPA)`. Confirmed across the 5 `bye1_repaired` surviving combinations `{C01, C03, C04, C11, C12}`.

| Rank | `player_id` | Player | Pace/Spin | 5-Combo Top10 | 1000-Boot P(T10) | HP Matches | HP Legal | Wkts | HP Econ | Raw RSAE24 | EB RSAE24 | Own Delta | Pos Match EB | Score (0-100) | Flags (`1-Match` / `Format IPL%`) |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1566 | **Mohammed Shami** | Pace | 3/5 | 76.7% | 46 | 466 | 31 | 7.76 | +8.28 | +5.00 | +6.23 | 0.568 | 79.2 | Format (`100%` IPL) |
| 2 | 830 | **Josh Hazlewood** | Pace | 4/5 | 65.5% | 36 | 452 | 33 | 8.02 | +7.93 | +4.70 | +4.63 | 0.531 | 76.9 | None (`73.2%` IPL) |
| 3 | 781 | **Sunil Narine** | Spin | 5/5 | 66.7% | 33 | 390 | 19 | 6.37 | +8.33 | +4.63 | +1.68 | 0.556 | 76.3 | Format (`100%` IPL) |
| 4 | 4900 | **Wanindu Hasaranga** | Spin | 3/5 | 64.2% | 31 | 409 | 32 | 8.10 | +6.62 | +3.67 | +1.81 | 0.596 | 74.1 | None (`66.0%` IPL) |
| 5 | 4692 | **Lockie Ferguson** | Pace | 3/5 | 55.0% | 30 | 291 | 22 | 8.02 | +8.83 | +4.22 | +6.73 | 0.492 | 73.6 | Single-match (`42.1%`) |
| 6 | 4219 | **Krunal Pandya** | Spin | 4/5 | 43.8% | 32 | 370 | 18 | 7.04 | +5.05 | +2.53 | +3.29 | 0.533 | 69.3 | Single-match (`47.1%`), Format (`100%` IPL) |
| 7 | 29888 | **Harshit Rana** | Pace | 3/5 | 31.2% | 26 | 285 | 22 | 8.55 | +6.52 | +2.92 | +6.05 | 0.423 | 67.0 | None (`81.1%` IPL) |
| 8 | 6256 | **Varun Chakravarthy** | Spin | 5/5 | 33.4% | 42 | 451 | 29 | 7.70 | +6.27 | +3.61 | -0.58 | 0.483 | 66.9 | None (`77.6%` IPL) |
| 9 | 2320 | **Trent Boult** | Pace | 4/5 | 28.0% | 52 | 532 | 27 | 7.52 | +3.90 | +2.27 | +5.21 | 0.485 | 66.7 | Format (`93.8%` IPL) |
| 10 | 4722 | **Rashid Khan** | Spin | 3/5 | 30.7% | 48 | 640 | 33 | 6.80 | +4.04 | +2.57 | +0.63 | 0.505 | 66.0 | Single-match (`38.4%`) |

*Unanimous 5-Combo Alignment & Missing Stars Audit*: All 10 bowlers in `C03`'s Top 10 have `top10_cnt_of_5 >= 3/5` (`5/5`: `Sunil Narine`, `Varun Chakravarthy`; `4/5`: `Josh Hazlewood`, `Krunal Pandya`, `Trent Boult`; `3/5`: `Mohammed Shami`, `Wanindu Hasaranga`, `Lockie Ferguson`, `Harshit Rana`, `Rashid Khan`), and zero bowler outside `C03` Top 10 reaches `>= 2/5` (`#11 Patrick Cummins 1/5`, `#12 Mujeeb Ur Rahman 0/5`, `#14 Saim Ayub 1/5`). `Jasprit Bumrah` (`455` legal HP balls, `eligible=True`, `#39`) and `Matheesha Pathirana` (`207` legal HP balls, `eligible=True`, `#49`) cleared eligibility easily but took fewer HP wickets than expected (`17` vs `26.75` for Bumrah, `13` vs `15.79` for Pathirana), lowering `12 * WAE` below Top-10 contention. Single-match dependence flags `Lockie Ferguson` (`42.1%`), `Krunal Pandya` (`47.1%`), and `Rashid Khan` (`38.4%`) under `D1 = bye1_repaired`; `Wanindu Hasaranga` sits at `31.2%` (`False`).
