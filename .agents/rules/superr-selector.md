---
trigger: always_on
description: Mandatory dataset schema, forensic traps, and multi-agent rules for Rajasthan Royals SupeRR Selector Season 2 (Round 1).
---

# SupeRR Selector Season 2 — Always-On Project Rules

Consult `AGENTS.md` and `.agents/skills/superr-selector-pressure-analytics/SKILL.md` before writing any data processing, modeling, or visualization code in this repository.

## Critical Data Guardrails
1. **Never sum `extras1_runs` in `ball_by_ball.csv`**: `extras1_runs` is the categorical ID for `extras_type` (`6` on all 189,167 normal legal deliveries). Summing it adds `+6` runs to every legal ball. Use `batter_runs = np.where(extras_type.isin(['wide', 'byes', 'legbyes', 'Penalty']), 0, runs)` and `extra_runs = np.where(extras_type.notna() & (extras_type != 'Penalty'), 1 + extras_2_runs, np.where(extras_type == 'Penalty', 5, 0))`.
2. **Legal Balls vs Delivery Number**: `over_ball_num` increments on wides and no-balls (up to 13). Count legal deliveries via `is_legal_ball = ~extras_type.isin(['wide', 'Overstep', 'other', 'Penalty'])`.
3. **Player ID Canonicalization**: Group players by `player_id`, never by `player_name` alone (3 homonyms exist: `Rashid Khan` `4722` AFG/GT vs `20172` NEP; `Abdul Samad` `7446` IND vs `6922` PAK; `Haider Ali` `7338` PAK vs `28756` UAE). Merge the 4 duplicate split IDs first: `{39444: 8638, 20229: 3083, 28978: 27373, 39479: 29833}`.
4. **Bowler Wicket Attribution**: Filter bowler-credited wickets strictly to `is_wicket & dismissal_type.isin(['Caught', 'Bowled', 'LBW', 'Stump', 'Hit Wicket'])` (excludes `RunOut`, `Retire Out`, and `Obstracting the field` / `Obstructing the field`).
5. **IPL Filtering**: Do not use `match_format == 'T20'` alone to identify IPL (it includes two Emerging/Rising Stars Asian tournaments `2670` and `3289`). Filter IPL explicitly via `comp_id.isin([1358, 1715, 2193, 2725, 3298])`.
