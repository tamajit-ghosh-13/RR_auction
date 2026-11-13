"""Combine all 12 gate-combination CSVs and diagnostics into one numbered master CSV."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def main() -> None:
    gdir = Path("outputs/gate_combinations")
    sum_df = pd.read_csv(gdir / "summary_metrics.csv")

    all_rows = []
    for c_idx, srow in sum_df.iterrows():
        cid = srow["combo_id"]
        cnum = int(cid[1:3])  # C01 -> 1, ..., C12 -> 12
        # Parse cutoffs string e.g. "120b/100b, 10m, >=2025"
        parts = [p.strip() for p in str(srow["d14_cutoffs"]).split(",")]
        bat_b = int(parts[0].split("/")[0].replace("b", ""))
        bwl_b = int(parts[0].split("/")[1].replace("b", ""))
        min_m = int(parts[1].replace("m", ""))
        rec_yr = int(parts[2].replace(">=", ""))

        combo_label = (
            f"{cnum:02d} | {srow['d1_runs']} | {srow['d8_d9_pressure']} | "
            f"wkt={srow['d12_bwl_wkt_val']:.0f} | {srow['d14_cutoffs']}"
        )

        # Load batters & bowlers top 25
        bat_df = pd.read_csv(gdir / f"{cid}_bat_top25.csv")
        bwl_df = pd.read_csv(gdir / f"{cid}_bowl_top25.csv")

        for role_num, role_name, df_r in [(1, "Batter", bat_df), (2, "Bowler", bwl_df)]:
            is_bat = role_name == "Batter"
            k_used = srow["d13_k_bat"] if is_bat else srow["d13_k_bwl"]
            n_elig = srow["n_elig_bat"] if is_bat else srow["n_elig_bwl"]
            mean_p10 = srow["bat_mean_p_top10"] if is_bat else srow["bwl_mean_p_top10"]
            sh_rho = srow["bat_split_half_rho"] if is_bat else srow["bwl_split_half_rho"]
            ov_c01 = srow["bat_overlap_vs_C01"] if is_bat else srow["bwl_overlap_vs_C01"]
            ipl26_t10 = srow["bat_top10_in_ipl2026"] if is_bat else srow["bwl_top10_in_ipl2026"]
            min_b = bat_b if is_bat else bwl_b

            for _, r in df_r.iterrows():
                rk = int(r["rank_eb"])
                all_rows.append({
                    "combo_num": cnum,
                    "combo_id": cid,
                    "combo_label": combo_label,
                    "role_num": role_num,
                    "role": role_name,
                    "tier_bucket": "1_Top10" if rk <= 10 else "2_Challenger_11_25",
                    "rank": rk,
                    "gate_D1_team_runs": srow["d1_runs"],
                    "gate_D8_D9_pressure": srow["d8_d9_pressure"],
                    "gate_D12_bwl_wkt_wt": float(srow["d12_bwl_wkt_val"]) if not is_bat else np.nan,
                    "gate_D13_shrinkage_k": float(k_used),
                    "gate_D14_min_hp_balls": min_b,
                    "gate_D14_min_hp_matches": min_m,
                    "gate_D14_recent_yr": rec_yr,
                    "gate_D15_weights": srow["d15_weights"],
                    "combo_n_eligible": int(n_elig),
                    "combo_mean_p_top10_pct": float(mean_p10),
                    "combo_split_half_rho": float(sh_rho) if pd.notna(sh_rho) else np.nan,
                    "combo_top10_overlap_vs_C01": int(ov_c01),
                    "combo_top10_in_ipl2026": int(ipl26_t10),
                    "player_id": int(r["player_id"]),
                    "player_name": r["player_name"],
                    "in_ipl2026": bool(r["in_ipl2026"]),
                    "hp_matches": int(r["hp_matches"]),
                    "hp_balls": int(r["hp_bf"] if is_bat else r["hp_legal"]),
                    "hp_runs": int(r["hp_runs"]),
                    "hp_outs_or_wkts": int(r["hp_outs"] if is_bat else r["hp_wkts"]),
                    "hp_sr_or_econ": round(float(r["hp_sr"] if is_bat else r["hp_econ"]), 2),
                    "primary_raw": round(float(r["hp_rae100_raw"] if is_bat else r["hp_total_rsae24_raw"]), 3),
                    "primary_eb": round(float(r["hp_rae100_eb"] if is_bat else r["hp_total_rsae24_eb"]), 3),
                    "own_baseline_delta": round(float(r["delta_own_rae100"] if is_bat else r["delta_own_rsae24"]), 3),
                    "pos_match_rate_eb": round(float(r["pos_match_rate_eb"]), 4),
                    "pm_sharpe_eb": round(float(r["pm_sharpe_eb"]), 4),
                    "wpa_eb": round(float(r["hp_wpa100_eb"] if is_bat else r["hp_wpa24_eb"]), 3),
                    "bwl_disc24_eb": round(float(r["hp_disc24_eb"]), 3) if not is_bat else np.nan,
                    "composite_z": round(float(r["composite_z"]), 4),
                    "pressure_score_0_100": round(float(r["pressure_score_0_100"]), 2),
                    "boot_p_top10_pct": round(float(r["boot_p_top10_pct"]), 1),
                    "hp_ipl_share": round(float(r["hp_ipl_share"]), 3),
                    "flag_single_match_dep": bool(r["flag_single_match_dep"]),
                    "flag_format_dep": bool(r["flag_format_dep"]),
                })

    mdf = pd.DataFrame(all_rows)
    mdf = mdf.sort_values(["combo_num", "role_num", "rank"]).reset_index(drop=True)

    # Cross-combination consensus counts per (role, player_id)
    top10_counts = (
        mdf[mdf["rank"] <= 10]
        .groupby(["role", "player_id"])["combo_num"]
        .nunique()
        .to_dict()
    )
    top25_counts = (
        mdf.groupby(["role", "player_id"])["combo_num"]
        .nunique()
        .to_dict()
    )
    mdf.insert(
        mdf.columns.get_loc("in_ipl2026") + 1,
        "combos_in_top10_of_12",
        [int(top10_counts.get((r.role, r.player_id), 0)) for r in mdf.itertuples()],
    )
    mdf.insert(
        mdf.columns.get_loc("combos_in_top10_of_12") + 1,
        "combos_in_top25_of_12",
        [int(top25_counts.get((r.role, r.player_id), 0)) for r in mdf.itertuples()],
    )
    mdf.insert(0, "seq_id", np.arange(1, len(mdf) + 1))

    out_path = gdir / "all_gate_combinations_master.csv"
    mdf.to_csv(out_path, index=False)
    print(f"Wrote {len(mdf)} rows x {mdf.shape[1]} cols -> {out_path}")
    print("\nBreakdown by combo_num and role:")
    print(mdf.groupby(["combo_num", "combo_id", "role"])["rank"].agg(["count", "min", "max"]).to_string())
    print("\nTop 10 Batters by cross-combo consensus (combos_in_top10_of_12):")
    print(
        mdf[mdf["role"] == "Batter"][["player_id", "player_name", "combos_in_top10_of_12", "combos_in_top25_of_12", "in_ipl2026"]]
        .drop_duplicates()
        .sort_values(["combos_in_top10_of_12", "combos_in_top25_of_12"], ascending=False)
        .head(12)
        .to_string(index=False)
    )
    print("\nTop 10 Bowlers by cross-combo consensus (combos_in_top10_of_12):")
    print(
        mdf[mdf["role"] == "Bowler"][["player_id", "player_name", "combos_in_top10_of_12", "combos_in_top25_of_12", "in_ipl2026"]]
        .drop_duplicates()
        .sort_values(["combos_in_top10_of_12", "combos_in_top25_of_12"], ascending=False)
        .head(12)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
