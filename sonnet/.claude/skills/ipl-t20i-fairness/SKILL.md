---
name: ipl-t20i-fairness
description: Make IPL and T20I performance comparable (competition effects, opposition quality, venue/country, batter–bowler joint model). Use when pooling IPL and T20I data or ranking players who play both.
---
# IPL vs T20I fairness

Facts: 134 T20I competitions (many bilateral series, minnow opponents) vs 5 IPL seasons (2022–26) with franchise squads; IPL has impact-player rule (flags in playing_eleven); scoring environments differ.

## Approach (recommended)
1. **Format-specific context baselines**: fit expected runs / wicket probability with `match_format` and `season` effects (or separate models per format), so a player is compared to what a typical player did in the *same format & state*.
2. **Joint batter–bowler model** (ridge / mixed effects): outcome(ball) ~ context + batter_id effect + bowler_id effect (+ venue_country, competition). Ridge penalty = built-in shrinkage; the effects are opposition-adjusted by construction. Use sparse one-hot + `sklearn.linear_model.Ridge`, or `statsmodels` mixed LM on match-aggregated data.
3. **Opposition strength**: team strength from the same model or Elo-style team ratings from match results (`win_team_id`). Optionally down-weight pressure balls against clearly weaker sides; always show the unweighted version.
4. **Venue/country**: `venue_id` only has IDs; use `venue_country` and venue-level scoring baselines (n per venue permitting).
5. **Pooling policy**: rank on pooled IPL+T20I with the adjustments above; show per-format ratings in the evidence table and flag players whose rating relies on one format. Test an "IPL-only" and "T20I-only" ranking as robustness.
6. **A-team / emerging events**: tag and (by default) exclude; mention in limitations.
7. **Home/away & toss**: include `toss_opted`, home team as covariates if they move baselines.

## Checks
- league-average runs/ball and wicket rate by format × phase × season (table) to show why pooling needs adjustment.
- Players present in both formats: compare ratings per format; large gaps → flag as context-dependent.
- Rank correlation between adjusted and unadjusted lists.

Outputs: `outputs/format_baselines.csv`, `outputs/opposition_adjustment_notes.md`.
