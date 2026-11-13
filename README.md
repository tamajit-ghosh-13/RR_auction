# Rajasthan Royals SupeRR Selector Season 2 — Round 1
## Auction Strategy & High-Pressure Performance Analytics Framework

This repository houses the end-to-end data pipeline, modeling infrastructure, and auction intelligence report for **Rajasthan Royals SupeRR Selector Season 2 (Round 1)**.

The framework identifies the most reliable batters and bowlers under genuine match pressure across **IPL and senior T20I cricket (2022–2026)** (837 non-DLS matches, 189,555 deliveries).

---

## 1. Official Unstop Dropdown Rankings (5-Pillar Architecture)

### Top 10 Batters Under Pressure
| Rank | Player Name | `player_id` | Primary Teams | HP Balls | HP Runs | HP SR | EB RAE100 | Away $\Delta$ | Own $\Delta$ | Score (0-100) | 1,000-Boot Certainty | Flags |
|:---:|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **Vaibhav Sooryavanshi** | `50284` | RR | 198 | 476 | 240.4 | +59.8 | -18.4 | +16.9 | **80.69** | **98.0%** (Lock) | Format (`88.9%` IPL) |
| **2** | **Suryakumar Yadav** | `1699` | MI, IND | 628 | 1096 | 174.5 | +31.5 | +6.2 | +6.3 | **69.35** | **92.0%** (Lock) | None (`58.0%` IPL) |
| **3** | **Travis Head** | `2367` | SRH, AUS | 340 | 615 | 180.9 | +29.5 | +20.6 | +1.1 | **67.42** | **71.1%** (Likely) | None (`62.9%` IPL) |
| **4** | **Abhishek Sharma** | `6281` | SRH, IND | 607 | 1073 | 176.8 | +32.3 | +19.8 | -14.9 | **66.61** | **69.9%** (Likely) | None (`67.5%` IPL) |
| **5** | **Heinrich Klaasen** | `4260` | SRH, SA | 224 | 399 | 178.1 | +25.2 | +2.5 | +5.9 | **65.74** | **60.1%** (Borderline) | Format (`90.6%` IPL) |
| **6** | **Nicholas Pooran** | `3125` | LSG, WI | 412 | 668 | 162.1 | +23.1 | +25.4 | +13.6 | **65.74** | **28.2%** (Borderline) | None (`52.7%` IPL) |
| **7** | **Jitesh Sharma** | `3916` | PBKS, RCB, IND | 303 | 487 | 160.7 | +21.6 | +1.6 | +17.2 | **63.67** | **60.1%** (Borderline) | Format (`97.7%` IPL) |
| **8** | **Priyansh Arya** | `25669` | PBKS | 207 | 392 | 189.4 | +33.5 | -8.4 | +2.1 | **63.13** | **64.1%** (Borderline) | 1-Match (`47.9%`), Format |
| **9** | **Yashasvi Jaiswal** | `6819` | RR, IND | 599 | 977 | 163.1 | +22.4 | +0.0 | +15.3 | **61.49** | **51.4%** (Borderline) | Format (`92.0%` IPL) |
| **10** | **Rinku Singh** | `4708` | KKR, IND | 260 | 430 | 165.4 | +16.4 | -7.0 | +17.6 | **61.41** | **57.3%** (Borderline) | Format (`87.3%` IPL) |

### Top 10 Bowlers Under Pressure
| Rank | Player Name | `player_id` | Style | Primary Teams | HP Legal | HP Wkts | HP Econ | EB RSAE24 | PBC EB | Bound. Supp. | Away $\Delta$ | Own $\Delta$ | Score (0-100) | 1,000-Boot Certainty | Flags |
|:---:|:---|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **Wanindu Hasaranga** | `4900` | Spin | SRH, RR, SL | 409 | 32 | 8.10 | +4.46 | +0.370 | 84.1% | +1.86 | +3.49 | **72.85** | **64.2%** (Borderline) | None (`66.0%` IPL) |
| **2** | **Sunil Narine** | `781` | Spin | KKR | 390 | 19 | 6.37 | +5.04 | +0.378 | 90.3% | +0.50 | +2.64 | **72.55** | **66.7%** (Likely) | Format (`100%` IPL) |
| **3** | **Josh Hazlewood** | `830` | Pace | RCB, AUS | 452 | 33 | 8.02 | +4.62 | +0.284 | 80.1% | +1.06 | +5.61 | **70.60** | **65.5%** (Likely) | None (`73.2%` IPL) |
| **4** | **Lockie Ferguson** | `4692` | Pace | KKR, RCB, NZ | 291 | 22 | 8.02 | +3.37 | +0.223 | 81.4% | +1.36 | +6.52 | **67.45** | **55.0%** (Borderline) | 1-Match (`42.1%`) |
| **5** | **Krunal Pandya** | `4219` | Spin | LSG, RCB, IND | 370 | 18 | 7.04 | +3.03 | +0.216 | 88.9% | +1.47 | +4.49 | **66.55** | **43.8%** (Borderline) | 1-Match (`47.1%`), Format |
| **6** | **Rashid Khan** | `4722` | Spin | GT, AFG | 640 | 33 | 6.80 | +2.34 | +0.312 | 89.1% | +3.27 | +1.29 | **65.31** | **30.7%** (Borderline) | 1-Match (`38.4%`) |
| **7** | **Varun Chakravarthy** | `6256` | Spin | KKR, IND | 451 | 29 | 7.70 | +3.97 | +0.314 | 84.0% | -0.55 | -0.05 | **64.87** | **33.4%** (Borderline) | None (`77.6%` IPL) |
| **8** | **Trent Boult** | `2320` | Pace | RR, MI, NZ | 532 | 27 | 7.52 | +2.06 | +0.282 | 81.8% | +1.96 | +6.20 | **64.50** | **28.0%** (Borderline) | Format (`93.8%` IPL) |
| **9** | **Harshit Rana** | `29888` | Pace | KKR, IND | 285 | 22 | 8.55 | +3.25 | +0.281 | 79.3% | -4.48 | +7.75 | **63.88** | **31.2%** (Borderline) | 1-Match (`39.8%`) |
| **10** | **Mujeeb Ur Rahman** | `6450` | Spin | KKR, AFG | 259 | 15 | 6.58 | +1.26 | +0.398 | 88.0% | -1.32 | +2.17 | **62.99** | **21.8%** (Outside) | 1-Match (`48.2%`), Format |

*Premier Challengers*:
- **#11 Ravindra Jadeja** (Score `62.48`, `PBC = +0.371`, `Away Delta = +1.20`, `Own Delta = +3.65`).
- **#12 Mohammed Shami** (Score `61.86`, 31 HP wickets, `EB RSAE = +4.65`, `Own Delta = +7.15`, **`76.7%` Bootstrap Top-10 Certainty**). Shami is the clear #1 pace alternative if single-match risk is penalized.

---

## 2. Key Methodological Innovations

1. **Gate D1 Repaired (`bye1_repaired`)**:
   - `extras1_runs` is a categorical type ID (wide `2`, leg-bye `3`, bye `4`, no-ball `1`, none `6`), not an additive run count. Fixed across all combinations to prevent bye/leg-bye run inflation.
2. **Win Probability Leverage Index (`LI >= 75th pct`)**:
   - Symmetric ex-ante leverage ($LI = E[|\Delta WP|]$) derived from leak-free pre-delivery state via Logistic Regression with 12-ball CRR smoothing (`AUC = 0.9003` Innings 2).
   - Only tier where **both** batting and bowling split-half correlations are clearly positive (`bat rho = +0.2498`, `bwl rho = +0.2399`) over a deep sample pool (83 batters, 93 bowlers).
3. **The 5-Pillar Architecture**:
   - **40% Shrunk Value (with Opposition Tiers & Marquee Rivalries)**: Joint Context + Player Ridge model (`alpha=150` runs, `250` wkts) adjusted by explicit team tiers (e.g. India/Australia Tier 1; RCB/GT/PBKS IPL Tier 1) and a $1.15\times$ derby multiplier across 11 rivalries (72 matches).
   - **20% Technical Execution & Composure**: Strike rotation, dot ball avoidance, and boundary punch rate for batters; Post-Boundary Composure (PBC: execution on delivery $t+1$ after a boundary), boundary suppression, and wicket strike rate for bowlers.
   - **15% Away Turf Lift ("Travel Warrior" Delta)**: Performance away from home under pressure ($\Delta_{\text{Away}} = \text{EB}_{\text{Away HP}} - \text{EB}_{\text{Home HP}}$). Nicholas Pooran ($+25.40$), Travis Head ($+20.58$), and Abhishek Sharma ($+19.80$) lead world cricket.
   - **15% Own-Baseline Pressure Lift**: Elevation above non-pressure baseline ($\Delta_{\text{Own}} = \text{EB}_{\text{HP}} - \text{EB}_{\text{NonHP}}$).
   - **10% Match Consistency**: Beta-Binomial positive-match rate ($m_0 = 8$).
4. **Empirical Bayes Shrinkage**:
   - Match-ANOVA shrinkage parameters ($k_{\text{bat}} = 180.9$ balls, $k_{\text{bowl}} = 242.0$ legal balls).
5. **The Jasprit Bumrah Paradox**:
   - Bumrah holds the **#1 Post-Boundary Composure across world cricket** (`+0.500` across 213 rebound deliveries).
   - In High Pressure situations, opposing batters defensively shut down and refuse to attack Bumrah, preferring to milk singles rather than risk losing wickets. Consequently, Bumrah conceded zero wickets across prolonged HP spells ($17$ vs $26.75$ expected wkts), resulting in an own-baseline drop ($\Delta_{\text{Pressure}} = -8.36$).
   - *Auction Intelligence*: Bumrah is an unmatched containment weapon whose true pressure contribution suppresses the opposition's scoring rate and induces errors at the other end.

---

## 3. Repository Structure & Key Deliverables

```
├── sonnet/
│   ├── scripts/
│   │   ├── common.py                 # Core constants, team tiers, rivalry pairs
│   │   ├── build_ball_state.py       # Ball-by-ball reconstruction (D1 = bye1_repaired)
│   │   ├── stage1_profile.py         # Data profiling & schema traps audit
│   │   ├── stage2_pressure.py        # WP & Leverage Index model calibration
│   │   ├── stage3_ratings.py         # 5-Pillar ratings, shrinkage, away & PBC enrichment
│   │   ├── stage4_validation.py      # Red-team verification, 1000-match bootstrap, 36 stress tests
│   │   ├── stage5_report_charts.py   # Publication-quality charts
│   │   ├── stage5_audit_checklist.py # Automated submission compliance assertions
│   │   ├── run_gate_combinations.py  # 12-combination multi-gate stability sweep (C01–C12)
│   │   └── build_master_csv.py       # Numbered master cross-combination CSV
│   └── outputs/
│       ├── report.md                 # Complete methodology report
│       ├── batting_top10.md          # Batting top 10 profiles, auction limits, flags
│       ├── bowling_top10.md          # Bowling top 10 profiles, auction limits, flags
│       ├── DECISIONS.md              # Gates D1 to D19 decisions log
│       ├── validator_notes.md        # Red-team audit and registry verification notes
│       ├── robustness_notes.md       # 36 robustness stress test results
│       ├── figures/                  # High-resolution publication charts
│       └── gate_combinations/        # C01–C12 tables and master combination CSV
└── README.md
```

---

## 4. Pipeline Execution & Reproduction

```bash
# 1. Reconstruct ball state with D1 = bye1_repaired
python sonnet/scripts/build_ball_state.py --data data/raw --out sonnet/data/interim/ball_state.csv.gz --bye-runs 1.0

# 2. Run data profiling and WP/LI modeling
python sonnet/scripts/stage1_profile.py
python sonnet/scripts/stage2_pressure.py

# 3. Fit opposition models, enrich away/PBC, and generate 5-pillar ratings
python sonnet/scripts/stage3_ratings.py

# 4. Run red-team verification, 1,000-match bootstrap, and robustness suite
python sonnet/scripts/stage4_validation.py

# 5. Generate publication figures and run gate combinations
python sonnet/scripts/stage5_report_charts.py
python sonnet/scripts/run_gate_combinations.py
python sonnet/scripts/build_master_csv.py

# 6. Verify submission assertions
python sonnet/scripts/stage5_audit_checklist.py
```
