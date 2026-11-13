# Decisions Log (`sonnet` Pipeline — Corrected `C03` Consolidation Run)

Every methodological choice documents both the `C03` primary specification selected after Gate `D1` audit and 5-combination confirmation across `{C01, C03, C04, C11, C12}`.

---

## Stage 1 — Data Engineering & Profiling (`data-engineer`)

- **D1. `team_runs` & chase target reconstruction (`bye1_repaired` vs `exact_extras1`)**:
  **DECISION LOCKED (`C03` Primary): `D1 = bye1_repaired` (`scripts/build_ball_state.py --bye-runs 1.0`) across all active combinations `{C01, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12}` (`C02` retained solely as an `exact_extras1` diagnostic contrast).**
  - *Why*: `extras1_runs` in `ball_by_ball.csv` is a category code (`6` normal, `2` wide, `3` leg-bye, `4` bye, `1` no-ball), NOT an additive run count. Across 393 non-DLS run-win matches, `bye1` gets `25%` of margins exact (mean error `2.6` runs) vs `exact_extras1` (`6.9%` exact, mean error `5.2` runs, inflating byes/leg-byes). Switching C03/C04/C11/C12 to `D1 = bye1_repaired` eliminates inflated `runs` targets while improving 2nd-innings WP OOF AUC (`0.8954 -> 0.9003`).

- **D2. Treatment of Emerging/A-Team T20 tournaments (`comp_id` `2670` & `3289`)**:
  **DECISION (`C03` Primary): Exclude Emerging/A-Team tournaments `2670` and `3289` (`30` matches) via explicit IPL `comp_id` allowlist `{1358, 1715, 2193, 2725, 3298}` + senior `T20I`.**

- **D3. DLS / Rain-Reduced Matches (`dls_flag == 1`, 34 matches / 4,433 deliveries)**:
  **DECISION (`C03` Primary): Exclude `dls_flag == 1` from WP training AND primary player pressure ratings.**

- **D4. Super Overs (`innings` 3 & 4, 38 deliveries across 6 matches) & No-Result Matches**:
  **DECISION (`C03` Primary): Exclude Super Overs (`innings > 2`) from standard 20-over WP/LI estimation and `batting_won.isna()` (25 NR/tied) from WP fitting.**

- **D5. Player ID Canonicalization (Split IDs vs Homonyms)**:
  **DECISION (`C03` Primary): Group strictly on canonical `player_id`; keep 3 true homonyms separate (`Rashid Khan` `4722` vs `20172`, `Abdul Samad` `7446` vs `6922`, `Haider Ali` `7338` vs `28756`) AND merge the 4 verified split IDs `{39444: 8638, 20229: 3083, 28978: 27373, 39479: 29833}`.**

- **D6. Classification of `extras_type == 'other'` & `bowl_speed`**:
  **DECISION (`C03` Primary): Follow `build_ball_state.py` `is_legal` definition; never use corrupted `bowl_speed` (`-1` to `1456.1` kph) — use `pace_or_spin` and `bowling_type` instead.**

---

## Stage 2 — Pressure Definition (`pressure-modeler`)

- **D7. Win Probability Engine (Logistic Regression vs HistGradientBoosting)**:
  **DECISION (`C03` Primary): Logistic Regression OOF ensemble with 12-ball smoothed CRR + resource proxy, selected strictly on lower 5-fold `GroupKFold(match_id)` LogLoss (`0.6363` vs `0.6464` Inn 1; `0.3946` vs `0.4249` Inn 2, `AUC = 0.9003`).**

- **D8. Primary Pressure Lens (Lens A WP Leverage Index vs Lens B Rule Index)**:
  **DECISION (`C03` Primary): Lens A ex-ante symmetric `LI = E[|ΔWP|]` normalized to `mean = 1.000`; Lens B rule index tested in Stage 4 (`C11`) for confirmation.**

- **D9. High-Pressure Threshold Tier (`75th` vs `90th` vs `95th` percentile)**:
  **DECISION (`C03` Primary): `LI >= 75th pct` (`is_hp_75`) as primary High-Pressure tier.**
  - *Why*: Across the 12-combo sweep under `D1 = bye1_repaired`, `LI >= 75th pct` (`C03` and `C12`) is the ONLY threshold where **both** batting and bowling odd/even split-half correlations are clearly positive (`bat rho = 0.2603` on `66` common batters, `bwl rho = 0.2011` on `84` common bowlers) with deep eligible pools (`83` batters, `93` bowlers). By contrast, `LI >= 90th` (`C01`) collapses bowling split-half to `0.0186`, and `LI >= 95th` (`C10`) collapses batting split-half to `-0.1353`.

- **D10. Repaired Target vs `target_raw` for Innings 2 WP & LI**:
  **DECISION (`C03` Primary): Use `build_ball_state.py` repaired `target`; `target_raw` tested in Stage 4 (`rho = 0.9665` bat, `0.9075` bowl).**

---

## Stage 3 — Analyst Metrics, Shrinkage & Eligibility (`batting-analyst`, `bowling-analyst`)

- **D11. Format Parity & Opposition Adjustment**:
  **DECISION (`C03` Primary): Format-aware Context + Joint Batter-Bowler Ridge (`alpha=150` runs, `250` wkts) across `IPL + T20I` to remove `+0.8–1.0 rpo` IPL environment inflation and adjust for opponent strength.**

- **D12. Bowling Value Unification (Runs Saved + Wickets Above Expected)**:
  **DECISION (`C03` Primary): `Total RSAE24 = Runs Saved + 12.0 * Wickets Above Expected` per 24 legal balls.**
  - *Why*: `wkt = 0` (`C09` pure economy) produces negative bowler split-half correlation (`-0.2002`) under `bye1_repaired`; `wkt = 15.0` (`C04`) offers no stability improvement over `12.0`.

- **D13. Empirical Bayes Shrinkage Constant (`k`)**:
  **DECISION (`C03` Primary): Match-ANOVA empirical Bayes `k_bat = 180.9` balls (`sigma2_w = 3489.03`, `sigma2_b = 247.67`), `k_bowl = 242.0` legal balls (`sigma2_w = 692.46`, `sigma2_b = 21.54`); Beta-Binomial consistency `m0 = 8` HP matches.**
  - *Why*: Estimated directly from between-match vs within-match variance in the `LI >= 75th pct` pool rather than fixed ad-hoc `k = 100`.

- **D14. Eligibility Cutoffs & Active Recency Window**:
  **DECISION (`C03` Primary): Batters `>= 180 HP balls`, Bowlers `>= 150 HP legal balls`, both `>= 12 HP matches` and `last_year >= 2025` (`83` eligible batters, `93` eligible bowlers).**
  - *Why*: Stricter floors eliminate single-season fluke profiles without strangling pool depth (`83` / `93` vs only `23` / `38` under strict `C07` or `32` / `59` under `C01`).

- **D15. 5-Pillar Composite Architecture Weights**:
  **DECISION LOCKED (`C03` Primary): `40% Shrunk Value (Tier & Rivalry Adj) + 20% Technical Execution & Composure + 15% Away Turf Delta + 15% Own-Baseline Lift + 10% Match Consistency`, cross-checked against 12-combination sweep and stability panel.**
  - *Batting Execution*: `0.40 * z(SRR) + 0.30 * z(DBA) + 0.30 * z(BPR)`.
  - *Bowling Composure & Execution*: `0.40 * z(PBC_eb) + 0.30 * z(Boundary Suppression) + 0.30 * z(Wicket Strike Rate)`.

---

## Stage 4 — Strategic Enhancements (`strategic-analyst`)

- **D16. Opposition Team Tiers & Strength-of-Schedule Multipliers**:
  **DECISION LOCKED: Apply explicit opponent quality weights at delivery level.**
  - *T20I Tiers*: Tier 1 (`1.25x`): India (`18`), Australia (`20`); Tier 2 (`1.10x`): England (`22`), South Africa (`19`), New Zealand (`17`); Tier 3 (`0.95x`): Pakistan (`25`), West Indies (`28`), Sri Lanka (`27`), Afghanistan (`78`); Tier 4 (`0.75x`): Bangladesh (`21`), Ireland (`23`), Zimbabwe (`72`), Associates.
  - *IPL Tiers (User Explicit)*: Tier 1 (`1.20x`): RCB (`5`), GT (`3508`), PBKS (`4`); Tier 2 (`1.05x`): CSK (`1`), MI (`2`), KKR (`8`), SRH (`242`); Tier 3 (`0.90x`): RR (`3`), DC (`7`), LSG (`3509`).

- **D17. Marquee Rivalry Stakes Multiplier (`1.15x`)**:
  **DECISION LOCKED: Apply `1.15x` high-voltage multiplier on deliveries in 11 historical marquee rivalries (72 matches in clean dataset).**
  - *IPL Derbies (4)*: MI vs CSK (`{1, 2}`), CSK vs RCB (`{1, 5}`), RCB vs KKR (`{5, 8}`), PBKS vs RR (`{4, 3}`).
  - *T20I Derbies (7)*: IND vs PAK (`{18, 25}`), AUS vs ENG (`{20, 22}`), IND vs AUS (`{18, 20}`), ENG vs IND (`{22, 18}`), AUS vs NZ (`{20, 17}`), PAK vs AFG (`{25, 78}`), BAN vs SL (`{21, 27}`).

- **D18. Away Turf Lift ("Travel Warrior" Delta — Option C)**:
  **DECISION LOCKED: $\Delta_{\text{Away}} = \text{EB Performance}_{\text{Away HP}} - \text{EB Performance}_{\text{Home HP}}$ derived from `matches.csv` `home_team_id` vs `away_team_id`.**
  - Isolates players whose performance elevates in hostile away conditions vs comfort-zone home pitches. Shrunk toward neutral baseline to reward verified travel resilience without penalizing small sample splits.

- **D19. Granular Technical Execution & Post-Boundary Composure (PBC)**:
  **DECISION LOCKED: Delivery-level rebound and technical execution scoring.**
  - *Bowler PBC*: On delivery $t+1$ following a boundary in the same over: `+1.0` (dot/wicket), `+0.5` (single), `0.0` (2/3 runs), `-1.0` (consecutive boundary or extra). Shrunk via empirical Bayes ($m=15$, prior mean $\mu=0.237$). Combined with Boundary Suppression ($1 - \text{conceded boundary rate}$) and Wicket Strike Rate ($24 \times \text{wkts}/\text{legal}$).
  - *Batter Technical Radar*: Strike Rotation Rate ($\text{SRR} = \% \text{ 1, 2, 3}$), Dot Ball Avoidance ($\text{DBA} = 1 - \text{dot rate}$), Boundary Punch Rate ($\text{BPR} = \% \text{ 4, 6}$).

