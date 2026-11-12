# Validator Stage Notes (`sonnet`)

## Audits Completed (`scripts/stage4_validation.py`)
1. **Red-Team Independent Recomputation (`outputs/red_team_checks.json`)**:
   - Recomputed HP balls, bat/bowler runs, dismissals (`dismissed_player_id`), and bowler-credited wickets directly from `data/raw/ball_by_ball.csv`, `matches.csv`, and `ball_pressure.csv.gz` with **zero imports** from `scripts/common.py` or `scripts/stage3_ratings.py`.
   - Checked 6 Top-10 players (`Rinku Singh`, `Quinton de Kock`, `Sai Sudharsan`, `Josh Hazlewood`, `Yuzvendra Chahal`, `Rashid Khan`): **6 / 6 EXACT MATCH** on every count.
2. **Leakage & ID Integrity Checks**:
   - Confirmed zero post-delivery leakage in WP models (`GroupKFold(5, match_id)`) and Ridge baselines (`GroupKFold(5, match_id)`).
   - Confirmed 0 homonym collapses (`Rashid Khan 4722` cleanly isolated from `20172`; `Abdul Samad`, `Haider Ali` cleanly separated) and clean merge of the 4 verified split IDs.
   - Confirmed `dls_flag == 1` (`34` matches) and Super Overs (`6` matches) excluded cleanly from primary rankings.
3. **Unstop Dropdown & Registry Compliance**:
   - Verified all `10/10` Top-10 Batters and `10/10` Top-10 Bowlers exist unambiguously in `competition_team_player_mapping.csv` (`10/10` Batters and `8/10` Bowlers mapped in `comp_id == 3298` IPL 2026; `#4 Nawaz` & `#7 Saim Ayub` mapped in senior T20Is).
4. **Match-by-Match Audit (`outputs/top10_match_audit.md`)**:
   - Inspected best 3 and worst 3 HP matches for all 20 Top-10 players; confirmed real high-leverage cricket innings (e.g., Shreyas Iyer 75 in 37 HP balls on 2025-06-01, Krunal Pandya 2/14 in 20 HP balls in the 2025-06-03 final, Rashid Khan 3-ball hat-trick spell 2023-04-09, Chahal 4/21 in 17 HP balls 2023-05-07).
   - Flagged `#6 Suryakumar Yadav`'s heavy contribution (`+39.84 RAE`) from one 86-run blitz (`match_id=18531`) and the honest split-half noise limitation under strict 90th-pct LI (`~120-200` HP balls).
