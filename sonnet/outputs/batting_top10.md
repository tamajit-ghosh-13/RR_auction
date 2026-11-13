# Top 10 Batters Under Pressure — `C03` Primary (`D1 = bye1_repaired`) + 5-Combo Confirmation

Primary spec: `D1 = bye1_repaired`, `LI >= 75th pct`, `min_hp_balls = 180`, `min_hp_matches = 12`, `last_year >= 2025` (`83` eligible batters), opposition-adjusted EB-shrunk (`k = 180.9` balls), weights `50% RAE100 / 15% Own-Delta / 25% Consistency / 10% WPA100`. Confirmed across the 5 `bye1_repaired` surviving combinations `{C01, C03, C04, C11, C12}`.

| Rank | `player_id` | Player | 5-Combo Top10 | 1000-Boot P(T10) | HP Matches | HP BF | HP SR | Raw RAE100 | EB RAE100 | Own Delta | Pos Match EB | EB WPA100 | Score (0-100) | Flags (`1-Match` / `Format IPL%`) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 50284 | **Vaibhav Sooryavanshi** | 3/5 | 98.0% | 22 | 198 | 240.4 | +94.0 | +52.1 | +10.6 | 0.752 | +0.54 | 92.7 | Format (`88.9%` IPL) |
| 2 | 1699 | **Suryakumar Yadav** | 4/5 | 92.0% | 50 | 628 | 174.5 | +34.4 | +28.1 | +4.6 | 0.746 | +1.22 | 75.1 | None (`58.0%` IPL) |
| 3 | 25669 | **Priyansh Arya** | 3/5 | 64.0% | 22 | 207 | 189.4 | +53.6 | +31.5 | +0.3 | 0.681 | +0.93 | 73.1 | Single-match (`47.9%`), Format (`100%` IPL) |
| 4 | 2367 | **Travis Head** | 4/5 | 71.1% | 43 | 340 | 180.9 | +41.9 | +29.5 | +3.6 | 0.616 | +1.21 | 73.0 | None (`62.9%` IPL) |
| 5 | 4260 | **Heinrich Klaasen** | 4/5 | 59.9% | 22 | 224 | 178.1 | +37.7 | +23.6 | +5.2 | 0.668 | +1.62 | 71.0 | Format (`90.6%` IPL) |
| 6 | 6281 | **Abhishek Sharma** | 4/5 | 70.0% | 81 | 607 | 176.8 | +39.3 | +31.7 | -12.8 | 0.678 | +0.48 | 70.0 | None (`67.5%` IPL) |
| 7 | 4708 | **Rinku Singh** | 4/5 | 57.2% | 20 | 260 | 165.4 | +21.6 | +15.3 | +15.2 | 0.761 | +0.91 | 68.5 | Format (`87.3%` IPL) |
| 8 | 3916 | **Jitesh Sharma** | 3/5 | 60.5% | 30 | 303 | 160.7 | +28.3 | +20.0 | +16.0 | 0.679 | +0.61 | 68.1 | Format (`97.7%` IPL) |
| 9 | 6819 | **Yashasvi Jaiswal** | 4/5 | 51.7% | 58 | 599 | 163.1 | +24.7 | +20.4 | +14.0 | 0.653 | +0.22 | 65.7 | Format (`92.0%` IPL) |
| 10 | 7216 | **Prabhsimran Singh** | 2/5 | 38.4% | 39 | 408 | 162.5 | +22.8 | +17.7 | -0.4 | 0.630 | +1.06 | 62.3 | Format (`100%` IPL) |

*Note on Challengers & Flags*: Every `4/5` consensus batter across `{C01, C03, C04, C11, C12}` (`Suryakumar Yadav`, `Travis Head`, `Heinrich Klaasen`, `Abhishek Sharma`, `Rinku Singh`, `Yashasvi Jaiswal`) AND every `3/5` consensus batter (`Vaibhav Sooryavanshi`, `Priyansh Arya`, `Jitesh Sharma`) appears directly in `C03`'s Top 9. Slot `#10` goes to `Prabhsimran Singh` (`2/5` in `{C03, C12}` `#10`, `#11` in `C04`, `38.4%` P(T10), zero single-match dependency), just ahead of `#11 Nicholas Pooran` (`1/5`, `28.2%`, `0` flags), `#16 Shreyas Iyer` (`2/5`, `18.8%`, `single_match=True`), and `#17 Tim David` (`1/5`, `18.7%`, `0` flags). Single-match flag applies strictly to `#3 Priyansh Arya` (`47.9%` of HP RAE from `match_id=40715`, `2025-04-08`). Format dependence (`>85%` IPL) applies to `Priyansh Arya`, `Prabhsimran Singh`, `Jitesh Sharma`, `Yashasvi Jaiswal`, `Heinrich Klaasen`, `Vaibhav Sooryavanshi`, and `Rinku Singh`.
