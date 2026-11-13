"""Stage 4: Red-Team Independent Verification, 10-Check Robustness Suite, Match Audit, & Dropdown Compliance."""
from __future__ import annotations

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import SEED, SPLIT_PLAYER_ID_MAP, assign_format_bucket
from stage3_ratings import build_batting_ratings, build_bowling_ratings

plt.rcParams.update({"figure.dpi": 140, "axes.spines.top": False, "axes.spines.right": False})


def red_team_independent_check(bat_df: pd.DataFrame, bwl_df: pd.DataFrame) -> dict:
    """Independently recompute raw HP batting & bowling stats from ball_by_ball.csv + ball_pressure.csv.gz
    without importing ANY helper from common.py or stage3_ratings.py."""
    raw = pd.read_csv("data/raw/ball_by_ball.csv", low_memory=False)
    matches = pd.read_csv("data/raw/matches.csv")
    bp = pd.read_csv("data/interim/ball_pressure.csv.gz", usecols=["match_id", "innings", "overid", "over_ball_num", "innings_ball_num", "is_hp_75"])

    # Independent merge & clean filter
    m_dls = set(matches.loc[
        matches["revised_target"].notna() | matches["first_inn_revised_overs"].notna() | matches["second_inn_revised_overs"].notna(),
        "match_id",
    ])
    ipl_ids = {1358, 1715, 2193, 2725, 3298}
    em_ids = {2670, 3289}
    m_comp = matches.set_index("match_id")["comp_id"].to_dict()

    raw = raw[raw["innings"].isin([1, 2])].copy()
    raw["comp_id"] = raw["match_id"].map(m_comp)
    raw = raw[(~raw["match_id"].isin(m_dls)) & (~raw["comp_id"].isin(em_ids))].copy()

    # Apply split ID map independently
    for c in ["striker_id", "bowler_id", "dismissed_player_id"]:
        raw[c] = raw[c].replace(SPLIT_PLAYER_ID_MAP)

    raw = raw.merge(bp, on=["match_id", "innings", "overid", "over_ball_num", "innings_ball_num"], how="inner")
    hp = raw[raw["is_hp_75"] == 1].copy()

    ext = hp["extras_type"].fillna("").str.lower()
    hp["ind_bf"] = ~ext.isin(["wide", "penalty"])
    # Check build_ball_state is_wide only for penalty check
    hp["ind_bf"] = ext != "wide"
    hp["ind_leg"] = ~ext.isin(["wide", "overstep", "penalty"])
    hp["ind_bat_runs"] = np.where(ext.isin(["wide", "byes", "legbyes", "penalty"]), 0, hp["runs"])
    hp["ind_bwl_runs"] = hp["runs"] + ext.eq("wide").astype(int) + ext.eq("overstep").astype(int) + hp["extras_2_runs"]
    hp["ind_bwl_wkt"] = (hp["is_wicket"] == 1) & (hp["dismissal_type"].fillna("").str.lower().isin(["caught", "bowled", "lbw", "stump", "hit wicket"]))

    top_bat = bat_df[bat_df["eligible"]].head(10)
    pick_bats = [top_bat.iloc[0], top_bat.iloc[4], top_bat.iloc[9]]
    bat_checks = []
    for row in pick_bats:
        pid = int(row["player_id"])
        sub = hp[(hp["striker_id"] == pid) & hp["ind_bf"]]
        outs = int(((hp["is_wicket"] == 1) & (hp["dismissed_player_id"] == pid)).sum())
        bf = int(len(sub))
        runs = int(sub["ind_bat_runs"].sum())
        assert bf == int(row["hp_bf"]), f"Red-team BF mismatch for {pid}: {bf} vs {row['hp_bf']}"
        assert runs == int(row["hp_runs"]), f"Red-team Runs mismatch for {pid}: {runs} vs {row['hp_runs']}"
        assert outs == int(row["hp_outs"]), f"Red-team Outs mismatch for {pid}: {outs} vs {row['hp_outs']}"
        bat_checks.append({"player_id": pid, "player_name": row["player_name"], "hp_bf": bf, "hp_runs": runs, "hp_outs": outs, "status": "EXACT_MATCH"})

    top_bwl = bwl_df[bwl_df["eligible"]].head(10)
    pick_bwls = [top_bwl.iloc[0], top_bwl.iloc[4], top_bwl.iloc[9]]
    bwl_checks = []
    for row in pick_bwls:
        pid = int(row["player_id"])
        sub = hp[hp["bowler_id"] == pid]
        leg = int(sub["ind_leg"].sum())
        bruns = int(sub["ind_bwl_runs"].sum())
        bwkts = int(sub["ind_bwl_wkt"].sum())
        assert leg == int(row["hp_legal"]), f"Red-team legal mismatch for {pid}: {leg} vs {row['hp_legal']}"
        assert bruns == int(row["hp_runs"]), f"Red-team bwl_runs mismatch for {pid}: {bruns} vs {row['hp_runs']}"
        assert bwkts == int(row["hp_wkts"]), f"Red-team bwl_wkts mismatch for {pid}: {bwkts} vs {row['hp_wkts']}"
        bwl_checks.append({"player_id": pid, "player_name": row["player_name"], "hp_legal": leg, "hp_runs": bruns, "hp_wkts": bwkts, "status": "EXACT_MATCH"})

    return {"batting_red_team": bat_checks, "bowling_red_team": bwl_checks}


def match_cluster_bootstrap(
    clean: pd.DataFrame,
    base_bat: pd.DataFrame,
    base_bwl: pd.DataFrame,
    n_boot: int = 1000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fast vectorized 1,000-match cluster bootstrap across pre-aggregated (player_id, match_id) tables."""
    rng = np.random.default_rng(SEED)

    # Pre-aggregate per-(match, player) HP & NHP stats so 1,000 resamples take < 3 seconds!
    def boot_role(df_full: pd.DataFrame, role: str, elig_df: pd.DataFrame, k_val: float, wts: tuple[float, float, float, float]) -> pd.DataFrame:
        elig_pids = elig_df.loc[elig_df["eligible"], "player_id"].astype(int).tolist()
        elig_set = set(elig_pids)
        match_ids = df_full["match_id"].unique()
        n_m = len(match_ids)
        m_to_idx = {m: i for i, m in enumerate(match_ids)}

        hp = df_full[df_full["is_hp_75"] == 1].copy()
        nhp = df_full[df_full["is_hp_75"] == 0].copy()

        if role == "batter":
            hp = hp[hp["bf"]].copy()
            nhp = nhp[nhp["bf"]].copy()
            hp["pid"] = hp["striker_id"].astype(int)
            nhp["pid"] = nhp["striker_id"].astype(int)
            hp["val"] = hp["bat_runs"] - hp["x_bat_runs_adj"]
            hp["n"] = 1.0
            hp["wpa"] = hp["delta_wp"]
            nhp["val"] = nhp["bat_runs"] - nhp["x_bat_runs_adj"]
            nhp["n"] = 1.0
            scale = 100.0
            base_ranks = elig_df.loc[elig_df["eligible"]].set_index("player_id")["rank_eb"].to_dict()
        else:
            hp["pid"] = hp["bowler_id"].astype(int)
            nhp["pid"] = nhp["bowler_id"].astype(int)
            hp["val"] = (hp["x_bwl_runs_adj"] - hp["bwl_runs"]) + 12.0 * (hp["is_wkt_bowler"] - hp["x_bwl_wkt_adj"])
            hp["n"] = hp["leg"].astype(float)
            hp["wpa"] = 0.5 * (-hp["delta_wp"]) + 0.5 * (hp["x_bwl_extra_ctx"] - hp["is_extra_bwl"])  # combined signal
            nhp["val"] = (nhp["x_bwl_runs_adj"] - nhp["bwl_runs"]) + 12.0 * (nhp["is_wkt_bowler"] - nhp["x_bwl_wkt_adj"])
            nhp["n"] = nhp["leg"].astype(float)
            scale = 24.0
            base_ranks = elig_df.loc[elig_df["eligible"]].set_index("player_id")["rank_eb"].to_dict()

        hp_sub = hp[hp["pid"].isin(elig_set)]
        nhp_sub = nhp[nhp["pid"].isin(elig_set)]

        pm_hp = hp_sub.groupby(["pid", "match_id"]).agg(n=("n", "sum"), val=("val", "sum"), wpa=("wpa", "sum")).reset_index()
        pm_nhp = nhp_sub.groupby(["pid", "match_id"]).agg(n=("n", "sum"), val=("val", "sum")).reset_index()
        pm_hp["midx"] = pm_hp["match_id"].map(m_to_idx)
        pm_nhp["midx"] = pm_nhp["match_id"].map(m_to_idx)

        p_to_idx = {p: i for i, p in enumerate(elig_pids)}
        P = len(elig_pids)
        mat_hp_n = np.zeros((n_m, P))
        mat_hp_v = np.zeros((n_m, P))
        mat_hp_w = np.zeros((n_m, P))
        mat_hp_pos = np.zeros((n_m, P))
        mat_hp_cnt = np.zeros((n_m, P))
        mat_nhp_n = np.zeros((n_m, P))
        mat_nhp_v = np.zeros((n_m, P))

        for r in pm_hp.itertuples(index=False):
            j = p_to_idx[r.pid]
            mat_hp_n[r.midx, j] = r.n
            mat_hp_v[r.midx, j] = r.val
            mat_hp_w[r.midx, j] = r.wpa
            if r.n >= 4:
                mat_hp_cnt[r.midx, j] = 1.0
                if r.val > 0:
                    mat_hp_pos[r.midx, j] = 1.0

        for r in pm_nhp.itertuples(index=False):
            j = p_to_idx[r.pid]
            mat_nhp_n[r.midx, j] = r.n
            mat_nhp_v[r.midx, j] = r.val

        ranks = np.zeros((n_boot, P))
        scores = np.zeros((n_boot, P))
        w1, w2, w3, w4 = wts
        m0 = 8.0
        for b in range(n_boot):
            idx = rng.integers(0, n_m, size=n_m)
            hn = mat_hp_n[idx].sum(axis=0)
            hv = mat_hp_v[idx].sum(axis=0)
            hw = mat_hp_w[idx].sum(axis=0)
            hc = mat_hp_cnt[idx].sum(axis=0)
            hp_pos = mat_hp_pos[idx].sum(axis=0)
            nn = mat_nhp_n[idx].sum(axis=0)
            nv = mat_nhp_v[idx].sum(axis=0)

            rate_hp = np.where(hn > 0, scale * hv / np.maximum(1.0, hn), 0.0)
            rate_hp_eb = (hn / (hn + k_val)) * rate_hp
            rate_nhp = np.where(nn > 0, scale * nv / np.maximum(1.0, nn), 0.0)
            rate_nhp_eb = (nn / (nn + max(k_val, 80.0))) * rate_nhp
            delta = rate_hp_eb - rate_nhp_eb
            pos_eb = (hp_pos + m0 * 0.5) / (hc + m0)
            wpa_eb = (hn / (hn + k_val)) * np.where(hn > 0, scale * hw / np.maximum(1.0, hn), 0.0)

            def zs(a):
                s = np.std(a)
                return np.zeros_like(a) if s < 1e-12 else (a - np.mean(a)) / s

            comp = w1 * zs(rate_hp_eb) + w2 * zs(delta) + w3 * zs(pos_eb) + w4 * zs(wpa_eb)
            scores[b] = comp
            # Rank descending: rank 1 is highest
            order = np.argsort(-comp)
            r_arr = np.empty(P)
            r_arr[order] = np.arange(1, P + 1)
            ranks[b] = r_arr

        rows = []
        for j, pid in enumerate(elig_pids):
            rk = ranks[:, j]
            p_top10 = float((rk <= 10).mean() * 100.0)
            tier = (
                "Lock Top 10"
                if p_top10 >= 90
                else ("Likely Top 10" if p_top10 >= 65 else ("Borderline (8-14)" if p_top10 >= 25 else "Outside / Volatile"))
            )
            rows.append(
                {
                    "player_id": pid,
                    "base_rank": int(base_ranks[pid]),
                    "boot_rank_mean": float(rk.mean()),
                    "boot_rank_median": float(np.median(rk)),
                    "boot_rank_p025": float(np.quantile(rk, 0.025)),
                    "boot_rank_p975": float(np.quantile(rk, 0.975)),
                    "p_in_top10_pct": p_top10,
                    "ci_tier": tier,
                }
            )
        return pd.DataFrame(rows).sort_values("base_rank")

    shrink = json.loads(Path("outputs/shrinkage_params.json").read_text())
    bat_boot = boot_role(clean, "batter", base_bat, shrink["batting"]["k_balls"], (0.50, 0.15, 0.25, 0.10))
    bwl_boot = boot_role(clean, "bowler", base_bwl, shrink["bowling"]["k_balls"], (0.50, 0.15, 0.25, 0.10))
    return bat_boot, bwl_boot


def compare_rankings(base_df: pd.DataFrame, alt_df: pd.DataFrame, name: str) -> dict:
    """Compute Spearman rho and Top-10 Jaccard overlap on mutually eligible players."""
    eb = base_df[base_df["eligible"]][["player_id", "rank_eb"]].rename(columns={"rank_eb": "r_base"})
    ea = alt_df[alt_df["eligible"]][["player_id", "rank_eb"]].rename(columns={"rank_eb": "r_alt"})
    m = eb.merge(ea, on="player_id", how="inner")
    rho = float(spearmanr(m["r_base"], m["r_alt"]).statistic) if len(m) > 3 else np.nan
    top10_b = set(eb.nsmallest(10, "r_base")["player_id"])
    top10_a = set(ea.nsmallest(10, "r_alt")["player_id"])
    ov = len(top10_b & top10_a)
    jac = ov / len(top10_b | top10_a) if (top10_b | top10_a) else 0.0
    return {
        "check": name,
        "n_common_elig": int(len(m)),
        "spearman_rho": round(rho, 4) if not np.isnan(rho) else np.nan,
        "top10_overlap_n": int(ov),
        "top10_jaccard": round(float(jac), 4),
    }


def main() -> None:
    clean = pd.read_csv("data/interim/ball_pressure_modeled.csv.gz", low_memory=False)
    clean["year"] = pd.to_datetime(clean["match_date"]).dt.year
    bat_base = pd.read_csv("outputs/batting_ratings.csv")
    bwl_base = pd.read_csv("outputs/bowling_ratings.csv")

    print("=== 1. RED-TEAM INDEPENDENT RECOMPUTATION ===")
    rt = red_team_independent_check(bat_base, bwl_base)
    print(json.dumps(rt, indent=2))

    print("\n=== 2. 1,000-MATCH CLUSTER BOOTSTRAP ===")
    bat_boot, bwl_boot = match_cluster_bootstrap(clean, bat_base, bwl_base, n_boot=1000)
    print("Top 15 Batters Bootstrap Rank CIs:")
    print(bat_boot.head(15).merge(bat_base[["player_id", "player_name"]], on="player_id")[["base_rank", "player_id", "player_name", "boot_rank_mean", "boot_rank_p025", "boot_rank_p975", "p_in_top10_pct", "ci_tier"]].to_string(index=False))
    print("\nTop 15 Bowlers Bootstrap Rank CIs:")
    print(bwl_boot.head(15).merge(bwl_base[["player_id", "player_name"]], on="player_id")[["base_rank", "player_id", "player_name", "boot_rank_mean", "boot_rank_p025", "boot_rank_p975", "p_in_top10_pct", "ci_tier"]].to_string(index=False))

    print("\n=== 3. 10-CHECK MANDATORY ROBUSTNESS SUITE (C03 PRIMARY: LI >= 75th pct) ===")
    rob_rows = []
    # Match-ID chronological split (Odd vs Even)
    m_sorted = clean[["match_id", "match_date"]].drop_duplicates().sort_values(["match_date", "match_id"])
    odd_m = set(m_sorted.iloc[0::2]["match_id"])
    even_m = set(m_sorted.iloc[1::2]["match_id"])
    bat_odd, _ = build_batting_ratings(clean[clean["match_id"].isin(odd_m)], hp_col="is_hp_75", min_hp_balls=81, min_hp_matches=5)
    bat_evn, _ = build_batting_ratings(clean[clean["match_id"].isin(even_m)], hp_col="is_hp_75", min_hp_balls=81, min_hp_matches=5)
    bwl_odd, _ = build_bowling_ratings(clean[clean["match_id"].isin(odd_m)], hp_col="is_hp_75", min_hp_balls=67, min_hp_matches=5)
    bwl_evn, _ = build_bowling_ratings(clean[clean["match_id"].isin(even_m)], hp_col="is_hp_75", min_hp_balls=67, min_hp_matches=5)
    for role, df_a, df_b, lbl in [("batter", bat_odd, bat_evn, "Split-half (Odd vs Even matches)"), ("bowler", bwl_odd, bwl_evn, "Split-half (Odd vs Even matches)")]:
        r = compare_rankings(df_a, df_b, lbl)
        r["role"] = role
        rob_rows.append(r)

    # Sensitivity variations relative to C03 primary (LI >= 75th, 180b/150b, 12m, >=2025)
    for role, fn, base_df, mb in [("batter", build_batting_ratings, bat_base, 180), ("bowler", build_bowling_ratings, bwl_base, 150)]:
        for lbl, kw in [
            ("LI >= 90th pct (C01)", {"hp_col": "is_hp_90", "min_hp_balls": 120 if role == "batter" else 100, "min_hp_matches": 10}),
            ("LI >= 95th pct (C10)", {"hp_col": "is_hp_95", "min_hp_balls": 60 if role == "batter" else 50, "min_hp_matches": 6}),
            ("Lens B (Rule index, C11)", {"hp_col": "is_hp_rule", "min_hp_balls": 140 if role == "batter" else 120, "min_hp_matches": 10}),
            ("Weights +10% Primary (60/10/20/10)", {"weights": (0.60, 0.10, 0.20, 0.10)}),
            ("Weights +10% Consist (40/15/35/10, C12)", {"weights": (0.40, 0.15, 0.35, 0.10), "min_hp_balls": 160 if role == "batter" else 140}),
            ("Weights +10% WPA/Disc (45/15/20/20)", {"weights": (0.45, 0.15, 0.20, 0.20)}),
            ("Cutoff relaxed (140b/120b, 10m)", {"min_hp_balls": 140 if role == "batter" else 120, "min_hp_matches": 10}),
            ("Cutoff strict (200b/180b, 14m)", {"min_hp_balls": 200 if role == "batter" else 180, "min_hp_matches": 14}),
            ("Cutoff all years (2022-26)", {"recent_cutoff_year": 2022}),
            ("IPL-only (min 80b, 8m)", {"df_sub": clean[clean["fmt"] == "IPL"], "min_hp_balls": 80, "min_hp_matches": 8}),
            ("T20I-only (min 60b, 6m)", {"df_sub": clean[clean["fmt"] == "T20I"], "min_hp_balls": 60, "min_hp_matches": 6}),
            ("Temporal 2022-24 vs Base", {"df_sub": clean[clean["year"] <= 2024], "min_hp_balls": 80, "min_hp_matches": 6, "recent_cutoff_year": 2022}),
            ("Temporal 2025-26 vs Base", {"df_sub": clean[clean["year"] >= 2025], "min_hp_balls": 80, "min_hp_matches": 6}),
            ("Unadjusted (Context-only vs Opp-Adj)", {"use_opp_adj": False}),
        ]:
            df_in = kw.pop("df_sub", clean)
            kw.setdefault("hp_col", "is_hp_75")
            kw.setdefault("min_hp_balls", mb)
            kw.setdefault("min_hp_matches", 12)
            alt_df, _ = fn(df_in, **kw)
            r = compare_rankings(base_df, alt_df, lbl)
            r["role"] = role
            rob_rows.append(r)

        # Leave-one-season-out
        loso_rhos, loso_ovs = [], []
        for yr in [2022, 2023, 2024, 2025, 2026]:
            alt_yr, _ = fn(clean[clean["year"] != yr], hp_col="is_hp_75", min_hp_balls=int(mb * 0.8), min_hp_matches=10, recent_cutoff_year=2024)
            c_yr = compare_rankings(base_df, alt_yr, f"LOSO excl {yr}")
            loso_rhos.append(c_yr["spearman_rho"])
            loso_ovs.append(c_yr["top10_overlap_n"])
        rob_rows.append({
            "role": role,
            "check": "Leave-One-Season-Out (2022-26 min)",
            "n_common_elig": int(base_df["eligible"].sum()),
            "spearman_rho": round(float(np.min(loso_rhos)), 4),
            "top10_overlap_n": int(np.min(loso_ovs)),
            "top10_jaccard": round(float(np.min(loso_ovs) / (20 - np.min(loso_ovs))), 4),
        })

    # Target noise (+-5 runs in Inn2) & Bye 1.5x proxy: compare against target_raw LI (is_hp_75_raw)
    p75_raw_tgt = clean["li_target_raw"].quantile(0.75)
    clean_noise = clean.copy()
    clean_noise["is_hp_raw_tgt"] = (clean_noise["li_target_raw"] >= p75_raw_tgt).astype(int)
    for role, fn, base_df, mb in [("batter", build_batting_ratings, bat_base, 180), ("bowler", build_bowling_ratings, bwl_base, 150)]:
        alt_n, _ = fn(clean_noise, hp_col="is_hp_raw_tgt", min_hp_balls=mb, min_hp_matches=12)
        r = compare_rankings(base_df, alt_n, "Target-raw (unrepaired target sensitivity)")
        r["role"] = role
        rob_rows.append(r)

    rng_n = np.random.default_rng(SEED)
    clean_noise["li_noisy"] = clean_noise["li"] + rng_n.normal(0.0, 0.05, size=len(clean_noise))
    p75_noisy = clean_noise["li_noisy"].quantile(0.75)
    clean_noise["is_hp_noisy"] = (clean_noise["li_noisy"] >= p75_noisy).astype(int)
    for role, fn, base_df, mb in [("batter", build_batting_ratings, bat_base, 180), ("bowler", build_bowling_ratings, bwl_base, 150)]:
        alt_n2, _ = fn(clean_noise, hp_col="is_hp_noisy", min_hp_balls=mb, min_hp_matches=12)
        r = compare_rankings(base_df, alt_n2, "Target/LI noise sensitivity")
        r["role"] = role
        rob_rows.append(r)

    rob_df = pd.DataFrame(rob_rows)[["role", "check", "n_common_elig", "spearman_rho", "top10_overlap_n", "top10_jaccard"]]
    rob_df.to_csv("outputs/robustness_summary.csv", index=False)
    print(rob_df.to_string(index=False))

    print("\n=== 4. UNSTOP DROPDOWN & ID COMPLIANCE CHECK ===")
    mapping = pd.read_csv("data/raw/competition_team_player_mapping.csv")
    map_pids = set(mapping["player_id"].replace(SPLIT_PLAYER_ID_MAP).astype(int))
    map_2026_pids = set(mapping.loc[mapping["comp_id"] == 3298, "player_id"].astype(int))
    top10_bat = bat_base[bat_base["eligible"]].head(10).merge(bat_boot, on="player_id", how="left")
    top10_bwl = bwl_base[bwl_base["eligible"]].head(10).merge(bwl_boot, on="player_id", how="left")
    for role, tdf in [("Batter", top10_bat), ("Bowler", top10_bwl)]:
        in_all = [int(pid) in map_pids for pid in tdf["player_id"]]
        in_2026 = [int(pid) in map_2026_pids for pid in tdf["player_id"]]
        print(f"  {role} Top-10 in mapping.csv: {sum(in_all)}/10 | in IPL 2026 (comp 3298): {sum(in_2026)}/10")

    # Compute 5-combo stability count (C01, C03, C04, C11, C12 under D1=bye1_repaired) if bye1_panel exists
    panel_dir = Path("outputs/bye1_panel")
    panel_ids = ["C01_bye1_li90_anova", "C03_bye1_li75_anova", "C04_bye1_li75_k100_w15", "C11_bye1_ruleB", "C12_bye1_li75_cons35"]
    bat_cnt5, bwl_cnt5 = {}, {}
    for cid in panel_ids:
        bf, wf = panel_dir / f"{cid}_bat_all.csv", panel_dir / f"{cid}_bowl_all.csv"
        if bf.exists():
            bdf = pd.read_csv(bf)
            for pid in bdf.loc[bdf["eligible"] & (bdf["rank_eb"] <= 10), "player_id"].astype(int):
                bat_cnt5[pid] = bat_cnt5.get(pid, 0) + 1
        if wf.exists():
            wdf = pd.read_csv(wf)
            for pid in wdf.loc[wdf["eligible"] & (wdf["rank_eb"] <= 10), "player_id"].astype(int):
                bwl_cnt5[pid] = bwl_cnt5.get(pid, 0) + 1

    # Attach bootstrap columns + 5-combo count cleanly & save final_rankings.csv (Top 25 Batters + Top 25 Bowlers)
    bat_top25 = bat_base[bat_base["eligible"]].head(25).merge(bat_boot, on="player_id", how="left")
    bat_top25["top10_cnt_of_5"] = [bat_cnt5.get(int(p), np.nan) for p in bat_top25["player_id"]]
    bat_top25["role"] = "Batter"
    bwl_top25 = bwl_base[bwl_base["eligible"]].head(25).merge(bwl_boot, on="player_id", how="left")
    bwl_top25["top10_cnt_of_5"] = [bwl_cnt5.get(int(p), np.nan) for p in bwl_top25["player_id"]]
    bwl_top25["role"] = "Bowler"
    final_df = pd.concat([bat_top25, bwl_top25], ignore_index=True)
    final_df.to_csv("outputs/final_rankings.csv", index=False)

    print("\n=== 5. MATCH-BY-MATCH AUDIT (TOP-10 BEST & WORST HP MATCHES) ===")
    audit_lines = ["# Match-by-Match Audit of Top-10 Batters & Bowlers (C03: LI >= 75th pct)\n"]
    hp_clean = clean[clean["is_hp_75"] == 1].copy()
    for role, tdf in [("Batter", top10_bat), ("Bowler", top10_bwl)]:
        audit_lines.append(f"## Top 10 {role}s\n")
        for _, r in tdf.iterrows():
            pid = int(r["player_id"])
            if role == "Batter":
                sub = hp_clean[(hp_clean["striker_id"] == pid) & (hp_clean["bf"])].copy()
                sub["val"] = sub["bat_runs"] - sub["x_bat_runs_adj"]
                pm = sub.groupby(["match_id", "match_date", "comp_name"]).agg(bf=("bf", "sum"), runs=("bat_runs", "sum"), rae=("val", "sum"), wpa=("delta_wp", "sum")).reset_index()
                metric_col = "rae"
            else:
                sub = hp_clean[hp_clean["bowler_id"] == pid].copy()
                sub["val"] = (sub["x_bwl_runs_adj"] - sub["bwl_runs"]) + 12.0 * (sub["is_wkt_bowler"] - sub["x_bwl_wkt_adj"])
                pm = sub.groupby(["match_id", "match_date", "comp_name"]).agg(leg=("leg", "sum"), runs=("bwl_runs", "sum"), wkts=("is_wkt_bowler", "sum"), rsae=("val", "sum"), wpa_s=("delta_wp", lambda s: -s.sum())).reset_index()
                metric_col = "rsae"
            best3 = pm.sort_values(metric_col, ascending=False).head(3)
            worst3 = pm.sort_values(metric_col, ascending=True).head(3)
            audit_lines.append(f"### #{int(r['rank_eb'])} {r['player_name']} (`player_id={pid}`, CI={r['ci_tier']}, P(Top10)={r['p_in_top10_pct']:.1f}%)")
            audit_lines.append("**Best 3 HP matches:**")
            for _, mr in best3.iterrows():
                audit_lines.append(f"- `{mr['match_date']}` ({mr['comp_name']}, `match_id={mr['match_id']}`): {dict(mr.drop(['match_id','match_date','comp_name']).round(2))}")
            audit_lines.append("**Worst 3 HP matches:**")
            for _, mr in worst3.iterrows():
                audit_lines.append(f"- `{mr['match_date']}` ({mr['comp_name']}, `match_id={mr['match_id']}`): {dict(mr.drop(['match_id','match_date','comp_name']).round(2))}")
            audit_lines.append("")
    Path("outputs/top10_match_audit.md").write_text("\n".join(audit_lines))

    # Plot Robustness Rank CIs for Top 15 Batters & Top 15 Bowlers
    fig_dir = Path("outputs/figures")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for role, t25, ax in [("Top 15 Batters (95% Match-Bootstrap Rank CI)", bat_top25.head(15), axes[0]), ("Top 15 Bowlers (95% Match-Bootstrap Rank CI)", bwl_top25.head(15), axes[1])]:
        sub = t25.iloc[::-1].reset_index(drop=True)
        y = np.arange(len(sub))
        err_low = np.maximum(0.0, sub["base_rank"] - sub["boot_rank_p025"])
        err_high = np.maximum(0.0, sub["boot_rank_p975"] - sub["base_rank"])
        cols = ["#2f855a" if p >= 90 else ("#2b6cb0" if p >= 65 else "#dd6b20") for p in sub["p_in_top10_pct"]]
        ax.errorbar(sub["base_rank"], y, xerr=[err_low, err_high], fmt="o", color="#1a202c", ecolor="#718096", elinewidth=1.4, capsize=3)
        ax.scatter(sub["base_rank"], y, c=cols, s=55, zorder=3)
        ax.axvline(10.5, color="#c53030", linestyle="--", lw=1.2, label="Top-10 Cutoff")
        ax.set_yticks(y)
        ax.set_yticklabels([f"{r.player_name} ({r.p_in_top10_pct:.0f}%)" for _, r in sub.iterrows()], fontsize=8.5)
        ax.set_xlabel("Rank (with 95% Match-Bootstrap CI)")
        ax.set_title(role)
        ax.set_xlim(0, 26)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "robustness_rank_ci.png", bbox_inches="tight")
    plt.close(fig)

    Path("outputs/red_team_checks.json").write_text(json.dumps(rt, indent=2))
    print("Saved outputs/final_rankings.csv, robustness_summary.csv, top10_match_audit.md, robustness_rank_ci.png.")


if __name__ == "__main__":
    main()
