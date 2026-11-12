# Top 10 Batters Under Pressure — `sonnet` Autonomous Run

Primary spec: `LI >= 90th pct`, `min_hp_balls = 120`, `min_hp_matches = 10`, `last_year >= 2025` (`32` eligible), opposition-adjusted EB-shrunk (`k = 206.0`), weights `50% RAE100 / 15% Own-Delta / 25% Consistency / 10% WPA100`.

| Rank | `player_id` | Player | HP Matches | HP BF | Runs | HP SR | Raw RAE100 | EB RAE100 | Own Delta | Pos Match EB | EB WPA100 | Score (0-100) | IPL Share |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4708 | Rinku Singh | 15 | 123 | 232 | 188.6 | +48.3 | +22.8 | +22.7 | 0.727 | +1.29 | 81.3 | 87.8% |
| 2 | 6819 | Yashasvi Jaiswal | 27 | 194 | 339 | 174.7 | +35.6 | +21.1 | +11.7 | 0.651 | +0.06 | 71.3 | 89.7% |
| 3 | 6281 | Abhishek Sharma | 31 | 181 | 325 | 179.6 | +43.0 | +24.1 | -18.8 | 0.688 | +0.49 | 69.0 | 72.9% |
| 4 | 3647 | Shreyas Iyer | 21 | 194 | 317 | 163.4 | +18.4 | +12.8 | +3.3 | 0.664 | +1.67 | 64.3 | 85.1% |
| 5 | 2101 | Quinton de Kock | 18 | 165 | 286 | 173.3 | +28.2 | +16.7 | +9.6 | 0.540 | +0.31 | 63.6 | 53.9% |
| 6 | 1699 | Suryakumar Yadav | 25 | 181 | 310 | 171.3 | +28.5 | +17.3 | -8.3 | 0.531 | +0.75 | 60.7 | 53.0% |
| 7 | 2367 | Travis Head | 16 | 123 | 211 | 171.5 | +31.5 | +16.5 | -13.2 | 0.540 | +1.53 | 60.1 | 76.4% |
| 8 | 4823 | Washington Sundar | 10 | 160 | 228 | 142.5 | +5.5 | +6.6 | +16.7 | 0.545 | +1.80 | 57.9 | 63.8% |
| 9 | 7544 | Venkatesh Iyer | 11 | 148 | 215 | 145.3 | +15.3 | +10.8 | +1.6 | 0.604 | -0.01 | 56.3 | 95.3% |
| 10 | 23450 | Sai Sudharsan | 16 | 200 | 310 | 155.0 | +6.5 | +7.0 | +8.7 | 0.593 | +1.13 | 54.8 | 100.0% |

*Format-dependence flags (`IPL Share > 85%`)*: Rinku Singh (`87.8%`), Yashasvi Jaiswal (`89.7%`), Shreyas Iyer (`85.1%`), Venkatesh Iyer (`95.3%`), Sai Sudharsan (`100.0%`). Full ±10 weight sensitivity and 1,000-match bootstrap CIs are in `outputs/batting_ratings.csv` and `outputs/final_rankings.csv`.
