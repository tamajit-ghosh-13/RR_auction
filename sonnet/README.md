# SupeRR Round 1 agent kit
Drop this folder into your project root (next to `data/raw/` containing the 6 CSVs). Works natively with Claude Code (`CLAUDE.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md`);
for other local agents point the system prompt at `CLAUDE.md` and the skill/agent files.

1. `mkdir -p data/raw outputs data/interim` and copy the CSVs into `data/raw` (keep `data/` out of git).
2. `python scripts/build_ball_state.py --data data/raw --out data/interim/ball_state.csv.gz`
3. Ask the agent: "Run the orchestrator workflow; stop at each gate for my decision."

Contains only schema facts and method guidance — no data. Rankings and definitions are yours to decide.
