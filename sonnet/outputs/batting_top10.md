# Top 10 Batters Under Pressure — 5-Pillar Architecture (`C03` Primary, `D1 = bye1_repaired`)

Primary specification: `D1 = bye1_repaired`, `LI >= 75th pct`, `min_hp_balls = 180`, `min_hp_matches = 12`, `last_year >= 2025` (`83` eligible batters), format-aware context + joint ridge (`alpha=150`) opposition adjustment, Empirical Bayes shrinkage (`k = 180.9` balls).
**5-Pillar Weights**: `40% Shrunk Value (with Tier & Rivalry Adjustment) + 20% Technical Execution (SRR / DBA / BPR) + 15% Away Turf Lift (Travel Warrior Delta) + 15% Own-Baseline Lift + 10% Match Consistency`.

| Rank | `player_id` | Player | 1000-Boot P(T10) | CI Tier | HP Matches | HP BF | HP Runs | HP SR | HP Avg | EB RAE100 | SRR | DBA | BPR | Away $\Delta$ | Own $\Delta$ | Score (0-100) | Flags (`1-Match` / `Format IPL%`) |
|---:|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 50284 | **Vaibhav Sooryavanshi** | 98.0% | Lock Top 10 | 22 | 198 | 476 | 240.4 | 79.3 | +59.8 | 20.2% | 62.6% | 42.4% | -18.4 | +16.9 | 80.7 | Format (`88.9%` IPL) |
| 2 | 1699 | **Suryakumar Yadav** | 92.0% | Lock Top 10 | 50 | 628 | 1096 | 174.5 | 52.2 | +31.5 | 43.2% | 69.1% | 26.0% | +6.2 | +6.3 | 69.3 | None (`58.0%` IPL) |
| 3 | 2367 | **Travis Head** | 71.1% | Likely Top 10 | 43 | 340 | 615 | 180.9 | 38.4 | +29.5 | 27.9% | 60.6% | 32.6% | +20.6 | +1.1 | 67.4 | None (`62.9%` IPL) |
| 4 | 6281 | **Abhishek Sharma** | 69.9% | Likely Top 10 | 81 | 607 | 1073 | 176.8 | 35.8 | +32.3 | 35.1% | 64.3% | 29.2% | +19.8 | -14.9 | 66.6 | None (`67.5%` IPL) |
| 5 | 4260 | **Heinrich Klaasen** | 60.1% | Borderline (8-14) | 22 | 224 | 399 | 178.1 | 44.3 | +25.2 | 50.0% | 74.6% | 24.6% | +2.5 | +5.9 | 65.7 | Format (`90.6%` IPL) |
| 6 | 3125 | **Nicholas Pooran** | 28.2% | Borderline (8-14) | 43 | 412 | 668 | 162.1 | 29.0 | +23.1 | 39.3% | 62.1% | 22.8% | +25.4 | +13.6 | 65.7 | None (`52.7%` IPL) |
| 7 | 3916 | **Jitesh Sharma** | 60.1% | Borderline (8-14) | 30 | 303 | 487 | 160.7 | 34.8 | +21.6 | 42.6% | 66.0% | 23.4% | +1.6 | +17.2 | 63.7 | Format (`97.7%` IPL) |
| 8 | 25669 | **Priyansh Arya** | 64.1% | Borderline (8-14) | 22 | 207 | 392 | 189.4 | 35.6 | +33.5 | 29.0% | 60.9% | 31.9% | -8.4 | +2.1 | 63.1 | Single-match (`47.9%`), Format (`100%` IPL) |
| 9 | 6819 | **Yashasvi Jaiswal** | 51.4% | Borderline (8-14) | 58 | 599 | 977 | 163.1 | 36.2 | +22.4 | 31.4% | 60.1% | 28.7% | +0.0 | +15.3 | 61.5 | Format (`92.0%` IPL) |
| 10 | 4708 | **Rinku Singh** | 57.3% | Borderline (8-14) | 20 | 260 | 430 | 165.4 | 61.4 | +16.4 | 46.2% | 70.0% | 23.8% | -7.0 | +17.6 | 61.4 | Format (`87.3%` IPL) |

### Strategic & Technical Highlights
1. **Vaibhav Sooryavanshi (#1)**: Generational boundary-punch outlier (`BPR = 42.4%`, `HP SR = 240.4`). Retains #1 rank across all 12 combinations despite sample caveat (`198` balls). High ceiling, but format dependent (`88.9%` IPL).
2. **Suryakumar Yadav (#2)**: Complete dual-threat master. Elite strike rotation (`SRR = 43.2%`), high dot avoidance (`DBA = 69.1%`), and positive away delta (`+6.18`). Unanimous lock (`92.0%` P(T10)).
3. **Nicholas Pooran (#6 — Premier Travel Warrior)**: Elevates massively under away conditions (`Away Delta = +25.40`), thriving against hostile home crowds with 668 runs, high boundary punch (`22.8%`), and solid own-baseline lift (`+13.64`).
4. **Heinrich Klaasen (#5) & Rinku Singh (#10)**: Highest dot avoidance in the entire cohort (`Klaasen 74.6%`, `Rinku 70.0%`) combined with elite strike rotation (`50.0%` and `46.2%`), keeping the scoreboard ticking during tense middle overs.
5. **Challengers (11–15)**: `#11 Sam Curran` (`61.03`), `#12 Rovman Powell` (`60.32`), `#13 Josh Inglis` (`58.73`), `#14 Cameron Green` (`58.50`), `#15 Jonny Bairstow` (`58.46`).
