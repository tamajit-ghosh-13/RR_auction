"""Stage 1 Data Profiling and Ball-State Verification for SupeRR Selector Season 2."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

from common import (
    EMERGING_COMP_IDS,
    IPL_COMP_IDS,
    SPLIT_PLAYER_ID_MAP,
    assign_format_bucket,
    balls_faced,
    bowler_runs,
    legal_balls,
    load_ball_state,
    load_raw_tables,
)


def main() -> None:
    tables = load_raw_tables("data/raw")
    comp = tables["competitions"]
    teams = tables["teams"]
    matches = tables["matches"]
    p11 = tables["playing_eleven"]
    mapping = tables["mapping"]
    bbb = tables["ball_by_ball"]
    bs = load_ball_state("data/interim/ball_state.csv.gz")

    print("=== 1. ROW COUNTS & MATCH COVERAGE ===")
    for k, df in tables.items():
        print(f"  {k}: {df.shape[0]:,} rows x {df.shape[1]} cols")
    print(f"  ball_state: {bs.shape[0]:,} rows x {bs.shape[1]} cols")
    print(f"  matches unique match_id: {matches['match_id'].nunique()}")
    print(f"  ball_by_ball unique match_id: {bbb['match_id'].nunique()}")
    missing_in_bbb = set(matches["match_id"]) - set(bbb["match_id"])
    print(f"  matches with 0 balls in ball_by_ball: {len(missing_in_bbb)}")
    if missing_in_bbb:
        m_miss = matches[matches["match_id"].isin(missing_in_bbb)][
            ["match_id", "comp_id", "match_date", "result", "win_team_id"]
        ]
        print(m_miss.to_string(index=False))

    print("\n=== 2. COMPETITIONS BREAKDOWN ===")
    m_comp = matches.merge(comp, on="comp_id", how="left")
    comp_summary = (
        comp.assign(
            n_matches=comp["comp_id"].map(matches.groupby("comp_id")["match_id"].nunique()).fillna(0).astype(int),
            n_bbb_matches=comp["comp_id"].map(
                bbb.merge(matches[["match_id", "comp_id"]], on="match_id").groupby("comp_id")["match_id"].nunique()
            ).fillna(0).astype(int),
        )
        .sort_values(["match_format", "season", "comp_id"])
    )
    print(comp_summary.to_string(index=False))

    print("\n=== 3. DATE RANGE & SUPER OVERS & DLS ===")
    print(f"  match_date min={matches['match_date'].min()} max={matches['match_date'].max()}")
    print(f"  innings distribution in bbb:\n{bbb['innings'].value_counts().sort_index().to_dict()}")
    super_over_matches = bbb.loc[bbb["innings"] > 2, "match_id"].nunique()
    print(f"  matches with innings > 2 (Super Over): {super_over_matches}")
    dls_matches = matches[
        matches["revised_target"].notna()
        | matches["first_inn_revised_overs"].notna()
        | matches["second_inn_revised_overs"].notna()
    ]
    print(f"  DLS / revised matches count: {len(dls_matches)}")
    print(f"  matches win_team_id isna: {matches['win_team_id'].isna().sum()}")
    print(f"  results sample for win_team_id isna:")
    print(matches.loc[matches["win_team_id"].isna(), ["match_id", "comp_id", "result"]].value_counts("result").head(10))

    print("\n=== 4. EXTRAS & EXTRAS1_RUNS TRAP ===")
    ext_tab = (
        bbb.assign(extras_type_clean=bbb["extras_type"].fillna("NONE"))
        .groupby("extras_type_clean", dropna=False)
        .agg(
            n_rows=("runs", "size"),
            extras1_mean=("extras1_runs", "mean"),
            extras1_unique=("extras1_runs", lambda s: sorted(s.dropna().unique().tolist())[:10]),
            extras2_vals=("extras_2_runs", lambda s: sorted(s.dropna().unique().tolist())[:10]),
            runs_min=("runs", "min"),
            runs_max=("runs", "max"),
            max_over_ball_num=("over_ball_num", "max"),
        )
    )
    print(ext_tab.to_string())
    print(f"  NONE rows with extras1_runs==1: {int(((bbb['extras_type'].isna()) & (bbb['extras1_runs'] == 1)).sum())}")

    print("\n=== 5. WICKET & DISMISSAL TYPES ===")
    wkt_tab = (
        bbb[bbb["is_wicket"] == 1]
        .assign(dismissal_clean=bbb["dismissal_type"].fillna("NONE"))
        .groupby("dismissal_clean")
        .agg(
            n=("is_wicket", "size"),
            striker_eq_dismissed=("dismissed_player_id", lambda s: int((s == bbb.loc[s.index, "striker_id"]).sum())),
            non_striker_eq_dismissed=("dismissed_player_id", lambda s: int((s == bbb.loc[s.index, "non_striker_id"]).sum())),
            dismissed_isna=("dismissed_player_id", lambda s: int(s.isna().sum())),
        )
    )
    print(wkt_tab.to_string())

    print("\n=== 6. BOWL_SPEED & TELEMETRY NULLS ===")
    for col in ["bowl_speed", "pace_or_spin", "stroke", "delivery_style", "over_or_around", "on_or_off", "batting_type", "bowling_type"]:
        n_null = int(bbb[col].isna().sum())
        pct_null = 100.0 * n_null / len(bbb)
        print(f"  {col}: {n_null:,} nulls ({pct_null:.2f}%)")
    bs_valid = bbb["bowl_speed"].dropna()
    print(
        f"  bowl_speed stats (non-null n={len(bs_valid):,}): min={bs_valid.min():.2f}, p01={bs_valid.quantile(0.01):.2f}, "
        f"median={bs_valid.median():.2f}, p99={bs_valid.quantile(0.99):.2f}, max={bs_valid.max():.2f}, "
        f"n_gt_165={(bs_valid > 165).sum()}, n_lt_50={(bs_valid < 50).sum()}"
    )

    print("\n=== 7. PLAYER ID <-> NAME COLLISIONS & SPLIT IDS ===")
    id_pairs = pd.concat(
        [
            bbb[["striker_id", "striker_name"]].rename(columns={"striker_id": "player_id", "striker_name": "player_name"}),
            bbb[["non_striker_id", "non_striker_name"]].rename(columns={"non_striker_id": "player_id", "non_striker_name": "player_name"}),
            bbb[["bowler_id", "bowler_name"]].rename(columns={"bowler_id": "player_id", "bowler_name": "player_name"}),
            mapping[["player_id", "player_name"]],
        ],
        ignore_index=True,
    ).dropna(subset=["player_id", "player_name"]).drop_duplicates()
    id_pairs["player_id"] = id_pairs["player_id"].astype(int)
    id_pairs["name_norm"] = id_pairs["player_name"].str.strip().str.lower()

    # Check IDs with multiple names
    id_multi_name = id_pairs.groupby("player_id")["player_name"].nunique()
    ids_with_multi = id_multi_name[id_multi_name > 1]
    print(f"  player_ids with >1 distinct string name: {len(ids_with_multi)}")
    if len(ids_with_multi) > 0:
        print(id_pairs[id_pairs["player_id"].isin(ids_with_multi.index)].sort_values("player_id").to_string(index=False))

    # Check names with multiple player_ids
    name_multi_id = id_pairs.groupby("name_norm")["player_id"].nunique()
    names_with_multi = name_multi_id[name_multi_id > 1]
    print(f"  normalized player_names mapping to >1 player_id: {len(names_with_multi)}")
    if len(names_with_multi) > 0:
        sub = id_pairs[id_pairs["name_norm"].isin(names_with_multi.index)].sort_values(["name_norm", "player_id"])
        # attach teams from mapping
        tm = mapping.groupby("player_id")["team_name"].apply(lambda s: ", ".join(sorted(s.unique()))).to_dict()
        sub = sub.assign(teams=sub["player_id"].map(tm).fillna("N/A"))
        print(sub.to_string(index=False))

    # Also check comp_id 3298 (IPL 2026) mapping coverage vs matches
    map_3298 = mapping[mapping["comp_id"] == 3298]
    bbb_3298 = bbb[bbb["match_id"].isin(matches.loc[matches["comp_id"] == 3298, "match_id"])]
    print(f"  comp_id 3298 (IPL 2026): matches={matches[matches['comp_id']==3298]['match_id'].nunique()}, "
          f"bbb_matches={bbb_3298['match_id'].nunique()}, mapping_players={map_3298['player_id'].nunique()}")

    print("\n=== 8. BALL_STATE VERIFICATION VS MATCHES.RESULT ===")
    # Check innings totals from ball_state vs result in non-DLS completed matches
    inn_tot = bs[bs["innings"].isin([1, 2])].groupby(["match_id", "innings"])["team_runs"].sum().unstack()
    m_chk = matches.merge(inn_tot, on="match_id", how="inner")
    m_chk["diff_inn1_inn2"] = m_chk[1] - m_chk[2]
    m_chk["dls"] = m_chk["revised_target"].notna() | m_chk["first_inn_revised_overs"].notna() | m_chk["second_inn_revised_overs"].notna()
    reg_chk = m_chk[~m_chk["dls"] & m_chk["win_team_id"].notna()].copy()

    # Check whether batting_won matches win_team_id consistently
    b2 = bs[bs["innings"] == 2].groupby("match_id").first().reset_index()
    b2["expected_inn2_won"] = (b2["batting_team_id"] == b2["win_team_id"]).astype(int)
    mismatch_bwon = b2[b2["batting_won"].notna() & (b2["batting_won"] != b2["expected_inn2_won"])]
    print(f"  batting_won vs batting_team_id == win_team_id mismatches in inn2: {len(mismatch_bwon)}")

    # Check bye_runs impact & target repair flag in inn2 non-DLS
    b2_clean = bs[(bs["innings"] == 2) & (bs["dls_flag"] == 0) & (bs["win_team_id"].notna())].copy()
    print(f"  Target repair rate in inn2 non-DLS: {b2_clean['target_repaired'].mean()*100:.2f}% rows "
          f"({b2_clean.groupby('match_id')['target_repaired'].max().sum()} matches)")
    # Check match-level inn2 vs target when chasing team won vs lost (non-DLS)
    m2 = b2_clean.groupby("match_id").agg(
        inn1_total=("inn1_total", "first"),
        inn2_total=("inn2_total", "first"),
        target_raw=("target_raw", "first"),
        target=("target", "first"),
        target_repaired=("target_repaired", "first"),
        batting_won=("batting_won", "first"),
        result=("result", "first"),
    )
    # Anomaly check: chasing team won with inn2_total < target, OR chasing team lost with inn2_total >= target
    anom_raw = m2[((m2["batting_won"] == 1) & (m2["inn2_total"] < m2["target_raw"])) | ((m2["batting_won"] == 0) & (m2["inn2_total"] >= m2["target_raw"]))]
    anom_rep = m2[((m2["batting_won"] == 1) & (m2["inn2_total"] < m2["target"])) | ((m2["batting_won"] == 0) & (m2["inn2_total"] >= m2["target"]))]
    print(f"  Non-DLS chase outcome vs inn2_total anomalies: target_raw={len(anom_raw)}, target_repaired={len(anom_rep)}")
    if len(anom_rep) > 0:
        print("  Remaining anomalies with repaired target:")
        print(anom_rep.head(15).to_string())

    # Check common.py helpers match build_ball_state.py
    assert (balls_faced(bs) == (~bs["is_wide"].astype(bool))).all(), "balls_faced mismatch!"
    assert (legal_balls(bs) == bs["is_legal"].astype(bool)).all(), "legal_balls mismatch!"
    assert np.allclose(bowler_runs(bs), bs["bowler_runs"]), "bowler_runs mismatch!"
    print("  common.py helper assertions PASSED (balls_faced, legal_balls, bowler_runs).")

    # Also inspect bye_runs=0.0 vs 1.0 impact on inn1_total vs result margin
    # Parse numeric run-win margins from result for completed non-DLS inn1 wins
    reg1 = m2[m2["batting_won"] == 0].copy()
    reg1["margin_str"] = reg1["result"].str.extract(r"by\s+(\d+)\s+run", expand=False).astype(float)
    reg1["calc_margin_b1"] = reg1["inn1_total"] - reg1["inn2_total"]
    valid_m = reg1.dropna(subset=["margin_str"])
    exact_match_b1 = int((valid_m["margin_str"] == valid_m["calc_margin_b1"]).sum())
    print(f"  Inn1-win margin exact match with bye=1.0: {exact_match_b1}/{len(valid_m)} matches "
          f"(mean abs err={(valid_m['margin_str'] - valid_m['calc_margin_b1']).abs().mean():.2f} runs)")

    # Save structured JSON summary for downstream scripts/notes
    summary = {
        "n_competitions": int(len(comp)),
        "n_teams_rows": int(len(teams)),
        "n_matches": int(len(matches)),
        "n_playing_eleven": int(len(p11)),
        "n_mapping": int(len(mapping)),
        "n_bbb_rows": int(len(bbb)),
        "n_ball_state_rows": int(len(bs)),
        "n_bbb_matches": int(bbb["match_id"].nunique()),
        "n_missing_bbb_matches": int(len(missing_in_bbb)),
        "n_super_over_matches": int(super_over_matches),
        "n_dls_matches": int(len(dls_matches)),
        "n_no_result_or_tie_matches": int(matches["win_team_id"].isna().sum()),
        "n_anom_target_raw": int(len(anom_raw)),
        "n_anom_target_rep": int(len(anom_rep)),
    }
    Path("outputs").mkdir(parents=True, exist_ok=True)
    Path("outputs/stage1_summary.json").write_text(json.dumps(summary, indent=2))
    print("\nSaved outputs/stage1_summary.json")


if __name__ == "__main__":
    main()
