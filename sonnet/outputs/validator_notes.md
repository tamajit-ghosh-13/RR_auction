# Validator Stage Notes (`C03` Primary: `D1 = bye1_repaired`, `LI >= 75th pct`)

## Audits Completed (`scripts/stage4_validation.py`)
1. **Red-Team Independent Recomputation (`outputs/red_team_checks.json`)**:
   - Recomputed HP (`is_hp_75`) balls, bat/bowler runs, dismissals (`dismissed_player_id`), and bowler-credited wickets directly from `data/raw/ball_by_ball.csv`, `matches.csv`, and `ball_pressure.csv.gz` with **zero imports** from `scripts/common.py` or `scripts/stage3_ratings.py`.
   - Checked 6 Top-10 players (`Vaibhav Sooryavanshi`, `Heinrich Klaasen`, `Prabhsimran Singh`, `Mohammed Shami`, `Lockie Ferguson`, `Rashid Khan`): **6 / 6 EXACT MATCH** on every count.
2. **Leakage, Schema & ID Integrity Checks**:
   - Confirmed Gate `D1 = bye1_repaired` across all active combinations (`C01, C03..C12`), isolating the categorical ID trap in `extras1_runs` (`6` normal, `2` wide, `3` leg-bye, `4` bye, `1` no-ball).
   - Confirmed zero post-delivery leakage (`GroupKFold(5, match_id)` on WP and Ridge models), zero homonym collapses (`Rashid Khan 4722` vs `20172`, `Abdul Samad`, `Haider Ali`), and clean exclusion of DLS (`34` matches) and Super Overs (`6` matches).
3. **Unstop Dropdown & Registry Compliance**:
   - Verified **`10/10` Top-10 Batters** and **`10/10` Top-10 Bowlers** in `competition_team_player_mapping.csv` AND **`10/10` Batters + `10/10` Bowlers** mapped cleanly in IPL 2026 (`comp_id == 3298`).
4. **Match-by-Match Audit & Limitation Flags (`outputs/top10_match_audit.md`)**:
   - **Single-match dependence flags (`max_1match_share > 35%`)**: Flagged `#3 Priyansh Arya` (`47.9%` from `2025-04-08` IPL `103` runs in `42` HP balls, `match_id=40715`), `#5 Lockie Ferguson` (`42.1%` from `2022-07-18` `4/13`, `match_id=16258`), `#6 Krunal Pandya` (`47.1%` from `2024-04-07` `3/7`, `match_id=30076`), and `#10 Rashid Khan` (`38.4%` from `2026-04-08` `3/17`, `match_id=50138`).
   - **Format dependence flags (`hp_ipl_share > 85%`)**: Batters `Priyansh Arya` (`100%`), `Prabhsimran Singh` (`100%`), `Jitesh Sharma` (`97.7%`), `Yashasvi Jaiswal` (`92.0%`), `Heinrich Klaasen` (`90.6%`), `Vaibhav Sooryavanshi` (`88.9%`), `Rinku Singh` (`87.3%`); Bowlers `Mohammed Shami` (`100%`), `Sunil Narine` (`100%`), `Krunal Pandya` (`100%`), `Trent Boult` (`93.8%`).
   - **Missing Stars Check**: Verified `Jasprit Bumrah` (`455` HP balls, `#39`, `17` vs `26.75` expected HP wkts, `delta_own = -7.43`) and `Matheesha Pathirana` (`207` HP balls, `#49`, `13` vs `15.79` expected HP wkts, `delta_own = -4.75`) passed eligibility cleanly (`last_year=2026`) and missed Top 10 strictly on HP wicket deficits under `12 * WAE`.
