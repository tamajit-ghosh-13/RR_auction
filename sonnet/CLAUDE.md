# SupeRR Selector Season 2 — Round 1 (Rajasthan Royals × Unstop)

**Task:** Identify the 10 most reliable **batters** and 10 most reliable **bowlers** under pressure, ranked 1–10,
from IPL + T20I data (2022 → 2026). Deliver (1) two ranked lists chosen from Unstop dropdowns, (2) a methodology report
(PDF/PPT/dashboard) covering: pressure definition · performance measurement (metrics, baselines, rating logic) ·
fair comparisons (sample size, eligibility, match context, IPL vs T20I) · evidence for the top 10 · reliability & limitations.
Reproducibility is judged: someone else must be able to re-run it.

## Non-negotiable rules (from the organisers)
1. **The human (Tamajit) owns the pressure definition, the model choices and the final picks.** AI may research, code, test and draft;
   the submitted insights/recommendations must be the participant's own. Wholly AI-generated submissions can be disqualified.
   → Agents propose options with evidence; they never silently decide. Mark every judgment call `DECISION NEEDED`.
2. **Data pack is confidential.** Never publish, upload, paste raw rows externally, or commit data to a public repo. Keep `data/` in `.gitignore`.
3. Rankings must come from the supplied data, **not reputation**. Never name a player "because he is famous".
4. One submission, individual only. Dropdown picks must exactly match the report's ranking.
5. Public data is allowed as a supplement; cite it and keep it separate from the pack.

## Data pack (verified facts — trust these over assumptions)
| File | Shape | Key facts |
|---|---|---|
| `ball_by_ball.csv` | 200,999 rows × 33 cols, 867 matches | one row per delivery (incl. wides/no-balls) |
| `matches.csv` | 883 rows × 22 | 16 matches have no ball data (abandoned); 22 matches have only 1 innings |
| `competitions.csv` | 141 | 134 `T20I` + 7 `T20` (IPL 2022–26 plus two Emerging/Rising-Stars A-team events) |
| `teams.csv` | 353 | comp_id, team_id, team_name |
| `playing_eleven.csv` | 28,381 | `is_played` False for 8,667 rows (squad only); impact-player flags (558) |
| `competition_team_player_mapping.csv` | 6,413 | 1,217 players — use for the canonical name list/dropdown check |

**Gotchas that will silently corrupt results** (details in `.claude/skills/data-profiling/SKILL.md`):
- `runs` = runs **off the bat only**. Wides/byes/leg-byes show `runs=0`.
- `extras1_runs` is a **type code** (6 none, 2 wide, 3 leg-bye, 1 no-ball "Overstep", 4 bye, 5 other, 7 penalty) — never sum it.
- **Bye / leg-bye runs are not recorded** → team totals & chase targets are approximate (see repair logic in `scripts/build_ball_state.py`).
- `over_ball_num` / `innings_ball_num` count wides & no-balls → rebuild **legal-ball** position yourself.
- `innings` 3/4 = super overs (38 rows, 6 matches) → exclude from pressure.
- `*_revised_overs` columns are in **balls**, not overs. 34 matches are DLS-affected → exclude from chase-pressure or use `revised_target`.
- Key everything on **player_id, never name**: 3 names map to 2 ids (Abdul Samad, Basil Hameed, Haider Ali).
- Bowler is **not** credited for RunOut / Retire Out / Obstructing the field. Run-out victim is the non-striker ~45% of the time → use `dismissed_player_id`.
- `bowl_speed` has sentinels (0, −1) and impossible values (max 1456) — do not use without cleaning. `delivery_ist_time` is date only.
- No score/target/wickets-fallen/phase columns exist — all must be derived.

## Repo layout
```
data/raw/          read-only originals (never edit, never publish)
data/interim/      ball_state.csv.gz and other derived tables
scripts/           build_ball_state.py (+ your analysis scripts)
outputs/           tables, figures, final rankings, report
.claude/skills/    task playbooks (read the relevant SKILL.md before acting)
.claude/agents/    role definitions (orchestrator → data-engineer → pressure-modeler → batting/bowling analysts → validator → report-writer)
```

## Working style
- Python (pandas, numpy, scikit-learn, statsmodels, matplotlib). Fix random seeds. Every number in the report must trace to a script + output file.
- After each stage write a short `outputs/<stage>_notes.md` (what was done, parameters, surprises, open decisions).
- Before claiming a result, run the validator checks in `ranking-robustness`.
- Be honest about uncertainty; a clearly-stated limitation scores better than a hidden one.
