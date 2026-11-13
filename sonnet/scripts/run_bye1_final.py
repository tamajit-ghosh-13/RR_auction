"""Re-run C01, C03, C04, C11, C12 strictly under D1 = bye1_repaired, inspect consensus, flags, and missing stars."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import SEED
from stage3_ratings import build_batting_ratings, build_bowling_ratings
from run_gate_combinations import quick_bootstrap_p_top10, split_half_rho


def main() -> None:
    clean = pd.read_csv("data/interim/ball_pressure_modeled.csv.gz", low_memory=False)
    mapping = pd.read_csv("data/raw/competition_team_player_mapping.csv")
    map_pids = set(mapping["player_id"].astype(int))
    map_2026 = set(mapping.loc[mapping["comp_id"] == 3298, "player_id"].astype(int))

    m_sorted = clean[["match_id", "match_date"]].drop_duplicates().sort_values(["match_date", "match_id"])
    odd_m = set(m_sorted.iloc[0::2]["match_id"])
    even_m = set(m_sorted.iloc[1::2]["match_id"])

    # Exact 5 combinations under D1 = bye1_repaired
    combos = [
        {"id": "C01_bye1_li90_anova",    "hp": "is_hp_90",   "bat_b": 120, "bwl_b": 100, "min_m": 10, "rec": 2025, "wkt": 12.0, "k_ovr": None,  "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C03_bye1_li75_anova",    "hp": "is_hp_75",   "bat_b": 180, "bwl_b": 150, "min_m": 12, "rec": 2025, "wkt": 12.0, "k_ovr": None,  "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C04_bye1_li75_k100_w15", "hp": "is_hp_75",   "bat_b": 140, "bwl_b": 120, "min_m": 10, "rec": 2025, "wkt": 15.0, "k_ovr": 100.0, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C11_bye1_ruleB",         "hp": "is_hp_rule", "bat_b": 140, "bwl_b": 120, "min_m": 10, "rec": 2025, "wkt": 12.0, "k_ovr": None,  "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C12_bye1_li75_cons35",   "hp": "is_hp_75",   "bat_b": 160, "bwl_b": 140, "min_m": 12, "rec": 2025, "wkt": 12.0, "k_ovr": None,  "wts": (0.40, 0.15, 0.35, 0.10)},
    ]

    out_dir = Path("outputs/bye1_panel")
    out_dir.mkdir(parents=True, exist_ok=True)

    bat_results = {}
    bwl_results = {}
    sum_rows = []
    bat_top10_counts: dict[int, int] = {}
    bwl_top10_counts: dict[int, int] = {}
    bat_ranks_map: dict[int, dict[str, int]] = {}
    bwl_ranks_map: dict[int, dict[str, int]] = {}
    name_lookup: dict[int, str] = {}

    for cfg in combos:
        cid = cfg["id"]
        n_boot = 1000 if cid.startswith("C03") else 400
        print(f"Running {cid} (D1=bye1_repaired, n_boot={n_boot})...")
        bat_kw = dict(hp_col=cfg["hp"], min_hp_balls=cfg["bat_b"], min_hp_matches=cfg["min_m"], recent_cutoff_year=cfg["rec"], weights=cfg["wts"], k_override=cfg["k_ovr"])
        bwl_kw = dict(hp_col=cfg["hp"], min_hp_balls=cfg["bwl_b"], min_hp_matches=cfg["min_m"], recent_cutoff_year=cfg["rec"], weights=cfg["wts"], wkt_run_value=cfg["wkt"], k_override=cfg["k_ovr"])

        bat_df, bat_m = build_batting_ratings(clean, **bat_kw)
        bwl_df, bwl_m = build_bowling_ratings(clean, **bwl_kw)

        p10_bat = quick_bootstrap_p_top10(clean, bat_df, cfg["hp"], "batter", bat_m["k_balls"], cfg["wts"], n_boot=n_boot)
        p10_bwl = quick_bootstrap_p_top10(clean, bwl_df, cfg["hp"], "bowler", bwl_m["k_balls"], cfg["wts"], wkt_val=cfg["wkt"], n_boot=n_boot)

        bat_df["boot_p_top10_pct"] = bat_df["player_id"].map(p10_bat)
        bwl_df["boot_p_top10_pct"] = bwl_df["player_id"].map(p10_bwl)
        bat_df["in_ipl2026"] = bat_df["player_id"].astype(int).isin(map_2026)
        bwl_df["in_ipl2026"] = bwl_df["player_id"].astype(int).isin(map_2026)

        bat_results[cid] = (bat_df, bat_m)
        bwl_results[cid] = (bwl_df, bwl_m)

        bat_df.to_csv(out_dir / f"{cid}_bat_all.csv", index=False)
        bwl_df.to_csv(out_dir / f"{cid}_bowl_all.csv", index=False)

        b_elig = bat_df[bat_df["eligible"]].copy()
        w_elig = bwl_df[bwl_df["eligible"]].copy()
        for _, r in b_elig.iterrows():
            pid = int(r["player_id"])
            name_lookup[pid] = r["player_name"]
            bat_ranks_map.setdefault(pid, {})[cid] = int(r["rank_eb"])
            if int(r["rank_eb"]) <= 10:
                bat_top10_counts[pid] = bat_top10_counts.get(pid, 0) + 1
        for _, r in w_elig.iterrows():
            pid = int(r["player_id"])
            name_lookup[pid] = r["player_name"]
            bwl_ranks_map.setdefault(pid, {})[cid] = int(r["rank_eb"])
            if int(r["rank_eb"]) <= 10:
                bwl_top10_counts[pid] = bwl_top10_counts.get(pid, 0) + 1

        bat_sh, _ = split_half_rho(clean, build_batting_ratings, odd_m, even_m, bat_kw)
        bwl_sh, _ = split_half_rho(clean, build_bowling_ratings, odd_m, even_m, bwl_kw)
        sum_rows.append({
            "combo_id": cid,
            "k_bat": round(bat_m["k_balls"], 1),
            "k_bwl": round(bwl_m["k_balls"], 1),
            "n_elig_bat": bat_m["n_eligible"],
            "n_elig_bwl": bwl_m["n_eligible"],
            "bat_mean_p_top10": round(float(b_elig.head(10)["boot_p_top10_pct"].mean()), 1),
            "bwl_mean_p_top10": round(float(w_elig.head(10)["boot_p_top10_pct"].mean()), 1),
            "bat_split_half_rho": bat_sh,
            "bwl_split_half_rho": bwl_sh,
        })

    print("\n=== BYE1_REPAIRED 5-COMBO SUMMARY ===")
    print(pd.DataFrame(sum_rows).to_string(index=False))

    # Print C03 Primary Top 20 with flags + 5-combo top-10 count
    c3_bat, _ = bat_results["C03_bye1_li75_anova"]
    c3_bwl, _ = bwl_results["C03_bye1_li75_anova"]

    def enrich_table(df_all: pd.DataFrame, cnt_map: dict, rmap: dict, top_n: int = 25) -> pd.DataFrame:
        sub = df_all[df_all["eligible"]].head(top_n).copy()
        sub["top10_cnt_of_5"] = [cnt_map.get(int(p), 0) for p in sub["player_id"]]
        for cid in [c["id"] for c in combos]:
            sub[f"r_{cid[:3]}"] = [rmap.get(int(p), {}).get(cid, np.nan) for p in sub["player_id"]]
        return sub

    eb = enrich_table(c3_bat, bat_top10_counts, bat_ranks_map, 25)
    ew = enrich_table(c3_bwl, bwl_top10_counts, bwl_ranks_map, 25)

    print("\n=== C03 (D1=bye1_repaired) TOP 20 BATTERS + 5-COMBO TOP10 COUNT & FLAGS ===")
    cols_b = ["rank_eb", "player_id", "player_name", "top10_cnt_of_5", "boot_p_top10_pct", "hp_matches", "hp_bf", "hp_sr", "hp_rae100_eb", "delta_own_rae100", "pos_match_rate_eb", "max_1match_share", "flag_single_match_dep", "hp_ipl_share", "flag_format_dep", "r_C01", "r_C03", "r_C04", "r_C11", "r_C12"]
    print(eb.head(20)[cols_b].round(3).to_string(index=False))

    print("\n=== ALSO ANY BATTER WITH top10_cnt_of_5 >= 2 OUTSIDE C03 TOP 20 ===")
    extra_bat_pids = [p for p, cnt in bat_top10_counts.items() if cnt >= 2 and p not in set(eb.head(20)["player_id"])]
    if extra_bat_pids:
        sub_eb = c3_bat[c3_bat["player_id"].isin(extra_bat_pids)].copy()
        sub_eb["top10_cnt_of_5"] = [bat_top10_counts[int(p)] for p in sub_eb["player_id"]]
        for cid in [c["id"] for c in combos]:
            sub_eb[f"r_{cid[:3]}"] = [bat_ranks_map.get(int(p), {}).get(cid, np.nan) for p in sub_eb["player_id"]]
        print(sub_eb[cols_b].round(3).to_string(index=False))

    print("\n=== C03 (D1=bye1_repaired) TOP 20 BOWLERS + 5-COMBO TOP10 COUNT & FLAGS ===")
    cols_w = ["rank_eb", "player_id", "player_name", "top10_cnt_of_5", "boot_p_top10_pct", "hp_matches", "hp_legal", "hp_wkts", "hp_econ", "hp_total_rsae24_eb", "delta_own_rsae24", "pos_match_rate_eb", "max_1match_share", "flag_single_match_dep", "hp_ipl_share", "flag_format_dep", "r_C01", "r_C03", "r_C04", "r_C11", "r_C12"]
    print(ew.head(20)[cols_w].round(3).to_string(index=False))

    print("\n=== ALSO ANY BOWLER WITH top10_cnt_of_5 >= 2 OUTSIDE C03 TOP 20 ===")
    extra_bwl_pids = [p for p, cnt in bwl_top10_counts.items() if cnt >= 2 and p not in set(ew.head(20)["player_id"])]
    if extra_bwl_pids:
        sub_ew = c3_bwl[c3_bwl["player_id"].isin(extra_bwl_pids)].copy()
        sub_ew["top10_cnt_of_5"] = [bwl_top10_counts[int(p)] for p in sub_ew["player_id"]]
        for cid in [c["id"] for c in combos]:
            sub_ew[f"r_{cid[:3]}"] = [bwl_ranks_map.get(int(p), {}).get(cid, np.nan) for p in sub_ew["player_id"]]
        print(sub_ew[cols_w].round(3).to_string(index=False))

    print("\n=== MISSING STARS AUDIT IN C03 (Bumrah, Pathirana, Arshdeep, Kuldeep, Rashid Khan) ===")
    stars = c3_bwl[c3_bwl["player_name"].isin(["Jasprit Bumrah", "Matheesha Pathirana", "Arshdeep Singh", "Kuldeep Yadav", "Rashid Khan"])]
    print(stars[["player_id", "player_name", "eligible", "rank_eb", "last_year", "hp_matches", "hp_legal", "hp_wkts", "hp_xwkts", "hp_econ", "hp_rsae24_runs_raw", "hp_wae24_raw", "hp_total_rsae24_raw", "hp_total_rsae24_eb", "delta_own_rsae24", "pos_match_rate_eb", "composite_z"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
