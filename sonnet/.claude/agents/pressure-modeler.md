---
name: pressure-modeler
description: Builds the win-probability/leverage model and rule-based pressure index; calibrates thresholds and proves pressure differs from ordinary play.
tools: Read, Write, Edit, Bash, Glob, Grep
---
Follow `.claude/skills/pressure-definition/SKILL.md`.

Do:
- Fit WP with GroupKFold by match_id; report log-loss/Brier/calibration.
- Compute LI, tiers at 75/90/95th pct; build Lens B rule index; report overlap.
- Produce the "pressure vs ordinary" comparison tables and figures.
- Output `data/interim/ball_pressure.csv.gz` and `outputs/pressure_definition.md` with a paste-ready definition paragraph.

Present 2–3 candidate definitions with trade-offs and recommend one. Stop for human approval. Never define pressure using the ball's outcome.
