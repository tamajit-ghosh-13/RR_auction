# Final Submission Checklist Audit (`C03` Primary + 5-Combo Confirmation)

- [x] **Gate `D1` repaired (`bye1_repaired`)**: `extras1_runs` category codes replaced cleanly across all active combinations `{C01, C03..C12}` (`C02` retained only as diagnostic contrast).
- [x] **No leakage**: Pre-delivery features only (`runs_before`, `wkts_in_hand`, `legal_before`, smoothed `crr`); `GroupKFold(5, match_id)` on WP models & Ridge baselines.
- [x] **No reputation inputs**: Zero external rankings, auction prices, or hardcoded tournament/tier overrides; Bumrah (`#39`) and Pathirana (`#49`) gaps audited objectively.
- [x] **Player ID canonicalization**: Strictly keyed on `player_id`; 3 homonyms preserved (`Rashid Khan 4722` vs `20172`, `Abdul Samad`, `Haider Ali`); 4 verified split IDs merged.
- [x] **Symmetry & fair comparisons**: Identical `LI >= 75th pct` definition for batter & bowler (`180b/150b, 12m, >=2025`, `83` batters / `93` bowlers); format- & opposition-adjusted baselines (`IPL` vs `T20I`); empirical Bayes shrinkage + `1,000`-match cluster bootstrap CIs + 10-check robustness table + 5-combo stability confirmation.
- [x] **Dropdown compliance**: `10/10` batters and `10/10` bowlers verified in `competition_team_player_mapping.csv` AND IPL 2026 (`comp_id == 3298`); exact ordering match between `outputs/final_rankings.csv`, `outputs/batting_top10.md`, `outputs/bowling_top10.md`, and `outputs/report.md`.
- [x] **Limitation flags disclosed**: Single-match (`max_1match_share > 35%`) and format-dependence (`> 85%` IPL) flags disclosed in `batting_top10.md`, `bowling_top10.md`, `validator_notes.md`, and `report.md`.
- [x] **Privacy / `.gitignore` safe**: `data/` and large `.csv`/`.csv.gz` outputs remain excluded via `sonnet/.gitignore`.
