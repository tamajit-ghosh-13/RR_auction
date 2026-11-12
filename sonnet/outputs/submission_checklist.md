# Final Submission Checklist Audit (`sonnet`)

- [x] **No leakage**: Pre-delivery features only (`runs_before`, `wkts_in_hand`, `legal_before`, smoothed `crr`); `GroupKFold(5, match_id)` on WP models & Ridge baselines.
- [x] **No reputation inputs**: Zero external rankings, auction prices, or hardcoded tournament/tier overrides.
- [x] **Player ID canonicalization**: Strictly keyed on `player_id`; 3 homonyms preserved (`Rashid Khan 4722` vs `20172`, `Abdul Samad`, `Haider Ali`); 4 verified split IDs merged.
- [x] **Cricket arithmetic traps verified**: `balls_faced = ~is_wide`; batting dismissals via `dismissed_player_id`; bowler wickets exclude `RunOut`, `Retire Out`, obstructing the field; Emerging T20 (`2670`, `3289`) excluded; DLS & Super Overs isolated.
- [x] **Symmetry & fair comparisons**: Identical `LI >= 90th pct` definition for batter & bowler; format- & opposition-adjusted baselines (`IPL` vs `T20I`); empirical Bayes shrinkage + `1,000`-match cluster bootstrap CIs + 10-check robustness table.
- [x] **Dropdown compliance**: `10/10` batters and `10/10` bowlers verified in `competition_team_player_mapping.csv`; exact ordering match between `outputs/final_rankings.csv`, `outputs/batting_top10.md`, `outputs/bowling_top10.md`, and `outputs/report.md`.
- [x] **Human ownership preserved**: Zero decisions marked approved in `outputs/DECISIONS.md`; all 15 judgment calls (`D1–D15`) flagged `DECISION NEEDED (autonomous default: ...)` and narrative blocks in `outputs/report.md` tagged `[HUMAN: rewrite in your words]`.
- [x] **Privacy / `.gitignore` safe**: `data/` and large `.csv`/`.csv.gz` outputs remain excluded via `sonnet/.gitignore`.
