# Top 10 Bowlers Under Pressure — `sonnet` Autonomous Run

Primary spec: `LI >= 90th pct`, `min_hp_legal = 100`, `min_hp_matches = 10`, `last_year >= 2025` (`59` eligible), opposition-adjusted EB-shrunk (`k = 199.6`), `Total RSAE24 = Runs Saved + 12 * Wkts Above Expected per 24 legal balls`, weights `50% Total RSAE24 / 15% Own-Delta / 25% Consistency / 10% (Discipline + WPA)`.

| Rank | `player_id` | Player | Pace/Spin | HP Matches | HP Legal | Wkts | HP Econ | Raw Total RSAE24 | EB Total RSAE24 | Own Delta | Pos Match EB | EB WPA24 | Score (0-100) | IPL Share |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 830 | Josh Hazlewood | Pace | 21 | 175 | 18 | 8.43 | +15.10 | +6.76 | +5.93 | 0.655 | +0.06 | 81.1 | 87.4% |
| 2 | 4219 | Krunal Pandya | Spin | 16 | 121 | 9 | 6.00 | +16.44 | +5.87 | +6.49 | 0.576 | -0.06 | 77.1 | 100.0% |
| 3 | 29888 | Harshit Rana | Pace | 16 | 143 | 14 | 8.98 | +10.70 | +4.15 | +6.47 | 0.562 | -0.18 | 71.2 | 83.2% |
| 4 | 2490 | Mohammad Nawaz | Spin | 13 | 146 | 11 | 6.12 | +10.82 | +4.25 | +2.27 | 0.546 | +0.06 | 69.7 | 0.0% |
| 5 | 1612 | Yuzvendra Chahal | Spin | 25 | 233 | 18 | 8.42 | +8.85 | +4.52 | +4.74 | 0.390 | -0.28 | 66.9 | 98.3% |
| 6 | 6256 | Varun Chakravarthy | Spin | 18 | 154 | 12 | 7.48 | +10.56 | +4.29 | -0.03 | 0.518 | -0.11 | 66.3 | 96.8% |
| 7 | 7690 | Saim Ayub | Spin | 10 | 133 | 8 | 5.95 | +6.74 | +2.37 | +4.04 | 0.520 | +0.17 | 66.1 | 0.0% |
| 8 | 781 | Sunil Narine | Spin | 20 | 167 | 9 | 6.50 | +8.40 | +3.53 | -0.35 | 0.494 | -0.04 | 64.9 | 100.0% |
| 9 | 2320 | Trent Boult | Pace | 25 | 257 | 16 | 7.75 | +6.55 | +3.45 | +5.55 | 0.495 | -0.32 | 64.8 | 96.5% |
| 10 | 4722 | Rashid Khan | Spin | 24 | 297 | 20 | 6.97 | +6.31 | +3.56 | +1.52 | 0.479 | -0.16 | 63.6 | 55.6% |

*Opportunity-bias & format flags*: Krunal Pandya (`100% IPL`), Sunil Narine (`100% IPL`), Yuzvendra Chahal (`98.3% IPL`), Varun Chakravarthy (`96.8% IPL`), Trent Boult (`96.5% IPL`), and Josh Hazlewood (`87.4% IPL`) draw mostly IPL high-pressure overs; Mohammad Nawaz (`0% IPL`) and Saim Ayub (`0% IPL`) are pure T20I volume. Note Jasprit Bumrah (`181` HP legal balls) ranks `#55` strictly because he took `6` wickets vs `~10.8` expected (`econ 8.69`) inside the strict `LI >= 90th pct` tier despite dominating lower-leverage overs.
