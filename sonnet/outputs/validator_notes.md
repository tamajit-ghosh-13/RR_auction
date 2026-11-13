# Validator Stage Notes (`C03` 5-Pillar Architecture: `D1 = bye1_repaired`, `LI >= 75th pct`)

## Audits Completed (`scripts/stage4_validation.py`)
1. **Red-Team Independent Recomputation (`outputs/red_team_checks.json`)**:
   - Recomputed HP (`is_hp_75`) balls, bat/bowler runs, dismissals (`dismissed_player_id`), and bowler-credited wickets directly from `data/raw/ball_by_ball.csv`, `matches.csv`, and `ball_pressure.csv.gz` with **zero imports** from `scripts/common.py` or `scripts/stage3_ratings.py`.
   - Checked 6 Top-10 players (`Vaibhav Sooryavanshi`, `Heinrich Klaasen`, `Rinku Singh`, `Wanindu Hasaranga`, `Krunal Pandya`, `Mujeeb Ur Rahman`): **6 / 6 EXACT MATCH** on every count.
2. **Leakage, Schema & ID Integrity Checks**:
   - Confirmed Gate `D1 = bye1_repaired` across all active combinations (`C01, C03..C12`), isolating the categorical ID trap in `extras1_runs` (`6` normal, `2` wide, `3` leg-bye, `4` bye, `1` no-ball).
   - Confirmed zero post-delivery leakage (`GroupKFold(5, match_id)` on WP and Ridge models), zero homonym collapses (`Rashid Khan 4722` vs `20172`, `Abdul Samad`, `Haider Ali`), and clean exclusion of DLS (`34` matches) and Super Overs (`6` matches).
3. **Unstop Dropdown & Registry Compliance**:
   - Verified **`10/10` Top-10 Batters** and **`10/10` Top-10 Bowlers** in `competition_team_player_mapping.csv`.
   - Verified **`10/10` Batters** and **`9/10` Bowlers** mapped cleanly in IPL 2026 (`comp_id == 3298`), with Josh Hazlewood signed in IPL 2025 (`comp_id == 2725`).
4. **Match-by-Match Audit & Limitation Flags (`outputs/top10_match_audit.md`)**:
   - **Single-match dependence flags (`max_1match_share > 35%`)**: Flagged `#8 Priyansh Arya` (`47.9%` from `2025-04-08` IPL `103` runs in `42` HP balls, `match_id=40715`), `#4 Lockie Ferguson` (`42.1%` from `2022-07-18` `4/13`, `match_id=16258`), `#5 Krunal Pandya` (`47.1%` from `2024-04-07` `3/7`, `match_id=30076`), `#6 Rashid Khan` (`38.4%` from `2026-04-08` `3/17`, `match_id=50138`), `#9 Harshit Rana` (`39.8%` from `2024-03-23` `3/33`, `match_id=30043`), and `#10 Mujeeb Ur Rahman` (`48.2%` from `2024-04-08` `3/15`, `match_id=30079`).
   - **Format dependence flags (`hp_ipl_share > 85%`)**: Batters `Priyansh Arya` (`100%`), `Jitesh Sharma` (`97.7%`), `Yashasvi Jaiswal` (`92.0%`), `Heinrich Klaasen` (`90.6%`), `Vaibhav Sooryavanshi` (`88.9%`), `Rinku Singh` (`87.3%`); Bowlers `Sunil Narine` (`100%`), `Krunal Pandya` (`100%`), `Trent Boult` (`93.8%`), `Mujeeb Ur Rahman` (`100%`).
   - **The Jasprit Bumrah Paradox**: Verified `Jasprit Bumrah` (`455` HP balls, `#39`) cleared eligibility easily and achieved the #1 Post-Boundary Composure in the world (`+0.500` across 213 rebound deliveries). However, in High Pressure situations, opposing batters defensively play him out (zero wickets conceded, singles taken), lowering his HP wicket rate (`17` vs `26.75` expected) and resulting in an own-baseline drop ($\Delta_{\text{Pressure}} = -8.36$).
