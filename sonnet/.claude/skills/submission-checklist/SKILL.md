---
name: submission-checklist
description: Final pre-submission checklist for the SupeRR Selector Round 1 (Unstop dropdowns, report, rules compliance, reproducibility). Use before submitting.
---
# Final checklist

**Deliverables**
- [ ] Top-10 batters, ranks 1–10, no duplicates within the list.
- [ ] Top-10 bowlers, ranks 1–10, no duplicates within the list.
- [ ] Each name found in the Unstop dropdown; confirm correct *player* for the 3 duplicate-name cases (Abdul Samad, Basil Hameed, Haider Ali).
- [ ] Dropdown order = report table order = `outputs/final_rankings.csv`.
- [ ] Report covers all five required areas (pressure definition, measurement, fair comparisons, evidence, reliability/limitations).

**Method quality**
- [ ] Pressure uses pre-delivery state only; same pressure set used for batting and bowling.
- [ ] Baselines = context-expected *and* own non-pressure baseline; shrinkage + eligibility documented.
- [ ] IPL/T20I pooling explained; opposition adjustment shown.
- [ ] Robustness suite run; borderline cases discussed; limitations include the missing bye/leg-bye runs and approximate chase targets.
- [ ] Rankings come from the supplied data, not reputation.

**Rules & integrity**
- [ ] The definition, weights, and final picks are the participant's own decisions; the report is in the participant's own words (AI used only as a tool).
- [ ] Data pack not shared/published; no raw rows in the report or any public repo.
- [ ] One submission only, individual entry.
- [ ] Participant can travel to Mumbai (and Goa if selected) with valid government photo ID (eligibility note from the organisers).

**Reproducibility**
- [ ] Fresh run from `data/raw` regenerates every table with fixed seeds.
- [ ] Versions and run order listed in the appendix.
