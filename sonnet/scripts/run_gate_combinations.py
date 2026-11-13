"""Systematic Multi-Gate Combination Runner for SupeRR Selector Season 2.

Evaluates 12 curated combinations across Gates D1 (team_runs), D8/D9 (Pressure lens & tier),
D12 (Bowling WAE weight), D13 (EB shrinkage), D14 (Eligibility & recency), and D15 (Pillar weights),
saving Top-25 CSVs, side-by-side Top-10 matrices, and objective split-half & bootstrap stability scores.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import SEED, assign_format_bucket, canon_player_ids, load_raw_tables
from stage2_pressure import compute_expected_li, compute_lens_b, fit_oof_wp, prepare_features
from stage3_ratings import (
    build_batting_ratings,
    build_bowling_ratings,
    fit_expected_and_opposition_models,
)


def build_exact_ball_state(data_dir: str = "data/raw") -> pd.DataFrame:
    """Replicate build_ball_state.py logic using exact team_runs = runs + extras1_runs + extras_2_runs."""
    raw = load_raw_tables(data_dir)
    b = raw["ball_by_ball"].copy()
    m = raw["matches"].copy()
    c = raw["competitions"].copy()

    b = b[b["innings"].isin([1, 2])].sort_values(
        ["match_id", "innings", "overid", "over_ball_num", "innings_ball_num"]
    ).reset_index(drop=True)

    ext = b["extras_type"].fillna("")
    b["is_wide"] = ext.eq("wide").astype(int)
    b["is_noball"] = ext.eq("Overstep").astype(int)
    b["is_bye"] = ext.isin(["byes", "legbyes"]).astype(int)
    b["is_legal"] = (~ext.isin(["wide", "Overstep", "Penalty"])).astype(int)

    # Exact total runs from raw columns (verified 303/303 non-DLS exact match, MAE=0.00)
    b["team_runs"] = b["runs"] + b["extras1_runs"] + b["extras_2_runs"]
    b["bowler_runs"] = b["runs"] + b["is_wide"] + b["is_noball"] + b["extras_2_runs"]
    b["is_wkt_team"] = (b["is_wicket"] == 1).astype(int)
    b["is_wkt_bowler"] = (
        (b["is_wicket"] == 1)
        & (~b["dismissal_type"].fillna("").isin(["RunOut", "Retire Out", "Obstracting the field", "Obstructing the field"]))
    ).astype(int)

    g = b.groupby(["match_id", "innings"], sort=False)
    b["cum_runs_after"] = g["team_runs"].cumsum()
    b["cum_wkts_after"] = g["is_wkt_team"].cumsum()
    b["legal_after"] = g["is_legal"].cumsum()
    b["runs_before"] = b["cum_runs_after"] - b["team_runs"]
    b["wkts_before"] = b["cum_wkts_after"] - b["is_wkt_team"]
    b["legal_before"] = b["legal_after"] - b["is_legal"]
    b["balls_left"] = (120 - b["legal_before"]).clip(lower=0)
    b["wkts_in_hand"] = 10 - b["wkts_before"]
    b["over_idx"] = b["overid"]
    b["phase"] = np.select([b["overid"] <= 6, b["overid"] <= 15], ["powerplay", "middle"], "death")
    b["crr"] = np.where(b["legal_before"] > 0, 6.0 * b["runs_before"] / b["legal_before"].replace(0, np.nan), np.nan)

    tot = b.groupby(["match_id", "innings"])["team_runs"].sum().unstack().rename(columns={1: "inn1_total", 2: "inn2_total"})
    b = b.merge(tot, left_on="match_id", right_index=True, how="left")
    mm = m.merge(c[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")
    keep = ["match_id", "comp_id", "comp_name", "match_format", "season", "match_date", "stage", "knock_out",
            "venue_id", "venue_country", "win_team_id", "revised_target", "first_inn_revised_overs",
            "second_inn_revised_overs", "toss_win_team_id", "toss_opted", "result"]
    b = b.merge(mm[keep], on="match_id", how="left")

    b["batting_won"] = (b["batting_team_id"] == b["win_team_id"]).astype(float)
    b.loc[b["win_team_id"].isna(), "batting_won"] = np.nan
    chase = b["innings"] == 2
    dls = b["revised_target"].notna()
    b["target_raw"] = np.where(chase, np.where(dls, b["revised_target"], b["inn1_total"] + 1), np.nan)
    b["target"] = b["target_raw"]
    b["target_repaired"] = 0
    balls2 = np.where(b["second_inn_revised_overs"].notna(), b["second_inn_revised_overs"], 120)
    b["balls_in_innings"] = np.where(chase, balls2.astype(float), 120.0)
    b["balls_left"] = np.where(chase, (b["balls_in_innings"] - b["legal_before"]).clip(lower=0), b["balls_left"])
    b["runs_needed"] = b["target"] - b["runs_before"]
    b["rrr"] = np.where(chase & (b["balls_left"] > 0), 6.0 * b["runs_needed"] / b["balls_left"].replace(0, np.nan), np.nan)
    b["rrr_minus_crr"] = b["rrr"] - b["crr"]
    b["dls_flag"] = (dls | b["first_inn_revised_overs"].notna()).astype(int)
    b["match_date"] = pd.to_datetime(b["match_date"])
    return b


def build_or_load_exact_modeled() -> pd.DataFrame:
    cache_path = Path("data/interim/ball_pressure_modeled_exact.csv.gz")
    if cache_path.exists():
        return pd.read_csv(cache_path, low_memory=False)

    print("Building Gate D1=exact_extras1 WP/LI and OOF Ridge tables (cached once)...")
    df = build_exact_ball_state("data/raw")
    df["fmt"] = assign_format_bucket(df)

    train_base = (df["fmt"].isin(["IPL", "T20I"])) & (df["dls_flag"] == 0) & (df["batting_won"].notna())
    mask1 = (train_base & (df["innings"] == 1)).to_numpy()
    mask2 = (train_base & (df["innings"] == 2)).to_numpy()
    x1, x2 = prepare_features(df, target_col="target")

    _, _, best1, models1, met1 = fit_oof_wp(df, x1, mask1)
    _, _, best2, models2, met2 = fit_oof_wp(df, x2, mask2)
    print(f"Exact-runs Inn1 AUC={met1['lr_auc']:.4f}, Inn2 AUC={met2['lr_auc']:.4f}, LogLoss={met2['lr_logloss']:.4f}")

    wp_before = np.where(df["innings"] == 1, best1, best2)
    d_after = df.copy()
    d_after["runs_before"] = df["cum_runs_after"]
    d_after["wkts_in_hand"] = 10 - df["cum_wkts_after"]
    d_after["legal_before"] = df["legal_after"]
    d_after["balls_left"] = np.maximum(0.0, df["balls_in_innings"] - df["legal_after"])
    xa1, xa2 = prepare_features(d_after, target_col="target")

    wp_after = np.zeros(len(df))
    i1 = (df["innings"] == 1).to_numpy()
    i2 = (df["innings"] == 2).to_numpy()
    wp_after[i1] = np.mean([m.predict_proba(xa1.iloc[i1].to_numpy())[:, 1] for m in models1], axis=0)
    wp2_a = np.mean([m.predict_proba(xa2.iloc[i2].to_numpy())[:, 1] for m in models2], axis=0)
    rn_after = df.loc[i2, "target"].fillna(165.0).to_numpy() - d_after.loc[i2, "cum_runs_after"].to_numpy()
    bl_after = d_after.loc[i2, "balls_left"].to_numpy()
    wk_after = d_after.loc[i2, "wkts_in_hand"].to_numpy()
    wp2_a = np.where(rn_after <= 0.0, 1.0, np.where((wk_after <= 0.0) | (bl_after <= 0.0), 0.0, wp2_a))
    wp_after[i2] = wp2_a

    li_raw = compute_expected_li(df, list(x1.columns), list(x2.columns), models1, models2, wp_before)
    norm_pool = (df["fmt"].isin(["IPL", "T20I"])) & (df["dls_flag"] == 0)
    li = li_raw / float(li_raw[norm_pool].mean())
    p75, p90, p95 = np.quantile(li[norm_pool], [0.75, 0.90, 0.95])
    rule_score, rule_flag = compute_lens_b(df)

    df["wp_before"] = wp_before
    df["wp_after"] = wp_after
    df["delta_wp"] = wp_after - wp_before
    df["li"] = li
    df["is_hp_75"] = (li >= p75).astype(int)
    df["is_hp_90"] = (li >= p90).astype(int)
    df["is_hp_95"] = (li >= p95).astype(int)
    df["rule_score"] = rule_score
    df["is_hp_rule"] = rule_flag

    df = canon_player_ids(df, merge_split_ids=True)
    d_mod, _ = fit_expected_and_opposition_models(df)
    clean_ex = d_mod[(d_mod["fmt"].isin(["IPL", "T20I"])) & (d_mod["dls_flag"] == 0)].copy()
    clean_ex.to_csv(cache_path, index=False)
    print(f"Saved {cache_path} ({len(clean_ex):,} clean rows)")
    return clean_ex


def quick_bootstrap_p_top10(
    df_full: pd.DataFrame,
    elig_df: pd.DataFrame,
    hp_col: str,
    role: str,
    k_val: float,
    wts: tuple[float, float, float, float],
    wkt_val: float = 12.0,
    n_boot: int = 300,
) -> dict[int, float]:
    """Compute P(Rank <= 10) for eligible players under exact combination spec."""
    rng = np.random.default_rng(SEED)
    elig_pids = elig_df.loc[elig_df["eligible"], "player_id"].astype(int).tolist()
    elig_set = set(elig_pids)
    match_ids = df_full["match_id"].unique()
    n_m = len(match_ids)
    m_to_idx = {m: i for i, m in enumerate(match_ids)}

    hp = df_full[df_full[hp_col] == 1].copy()
    nhp = df_full[df_full[hp_col] == 0].copy()

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
    else:
        hp["pid"] = hp["bowler_id"].astype(int)
        nhp["pid"] = nhp["bowler_id"].astype(int)
        hp["val"] = (hp["x_bwl_runs_adj"] - hp["bwl_runs"]) + wkt_val * (hp["is_wkt_bowler"] - hp["x_bwl_wkt_adj"])
        hp["n"] = hp["leg"].astype(float)
        hp["wpa"] = 0.5 * (-hp["delta_wp"]) + 0.5 * (hp["x_bwl_extra_ctx"] - hp["is_extra_bwl"])
        nhp["val"] = (nhp["x_bwl_runs_adj"] - nhp["bwl_runs"]) + wkt_val * (nhp["is_wkt_bowler"] - nhp["x_bwl_wkt_adj"])
        nhp["n"] = nhp["leg"].astype(float)
        scale = 24.0

    pm_hp = hp[hp["pid"].isin(elig_set)].groupby(["pid", "match_id"]).agg(n=("n", "sum"), val=("val", "sum"), wpa=("wpa", "sum")).reset_index()
    pm_nhp = nhp[nhp["pid"].isin(elig_set)].groupby(["pid", "match_id"]).agg(n=("n", "sum"), val=("val", "sum")).reset_index()
    pm_hp["midx"] = pm_hp["match_id"].map(m_to_idx)
    pm_nhp["midx"] = pm_nhp["match_id"].map(m_to_idx)

    p_to_idx = {p: i for i, p in enumerate(elig_pids)}
    P = len(elig_pids)
    mat_hn, mat_hv, mat_hw, mat_hpos, mat_hcnt = [np.zeros((n_m, P)) for _ in range(5)]
    mat_nn, mat_nv = np.zeros((n_m, P)), np.zeros((n_m, P))

    for r in pm_hp.itertuples(index=False):
        j = p_to_idx[r.pid]
        mat_hn[r.midx, j] = r.n
        mat_hv[r.midx, j] = r.val
        mat_hw[r.midx, j] = r.wpa
        if r.n >= 4:
            mat_hcnt[r.midx, j] = 1.0
            if r.val > 0:
                mat_hpos[r.midx, j] = 1.0
    for r in pm_nhp.itertuples(index=False):
        j = p_to_idx[r.pid]
        mat_nn[r.midx, j] = r.n
        mat_nv[r.midx, j] = r.val

    ranks = np.zeros((n_boot, P))
    if len(wts) == 5:
        w1, _, _, w2, w3 = wts
        w4 = 0.0
    else:
        w1, w2, w3, w4 = wts
    m0 = 8.0
    for b in range(n_boot):
        idx = rng.integers(0, n_m, size=n_m)
        hn, hv, hw = mat_hn[idx].sum(0), mat_hv[idx].sum(0), mat_hw[idx].sum(0)
        hc, hpos = mat_hcnt[idx].sum(0), mat_hpos[idx].sum(0)
        nn, nv = mat_nn[idx].sum(0), mat_nv[idx].sum(0)

        r_hp_eb = (hn / (hn + k_val)) * np.where(hn > 0, scale * hv / np.maximum(1.0, hn), 0.0)
        r_nhp_eb = (nn / (nn + max(k_val, 80.0))) * np.where(nn > 0, scale * nv / np.maximum(1.0, nn), 0.0)
        delta = r_hp_eb - r_nhp_eb
        pos_eb = (hpos + m0 * 0.5) / (hc + m0)
        wpa_eb = (hn / (hn + k_val)) * np.where(hn > 0, scale * hw / np.maximum(1.0, hn), 0.0)

        def zs(a):
            s = np.std(a)
            return np.zeros_like(a) if s < 1e-12 else (a - np.mean(a)) / s

        comp = w1 * zs(r_hp_eb) + w2 * zs(delta) + w3 * zs(pos_eb) + w4 * zs(wpa_eb)
        order = np.argsort(-comp)
        rk = np.empty(P)
        rk[order] = np.arange(1, P + 1)
        ranks[b] = rk

    return {pid: float((ranks[:, j] <= 10).mean() * 100.0) for j, pid in enumerate(elig_pids)}


def split_half_rho(df_full: pd.DataFrame, fn, odd_m: set, even_m: set, kw: dict) -> tuple[float, int]:
    """Compute odd-vs-even match split-half Spearman rho & Top-10 overlap."""
    kw_half = dict(kw)
    kw_half["min_hp_balls"] = max(25, int(kw["min_hp_balls"] * 0.45))
    kw_half["min_hp_matches"] = max(3, int(kw["min_hp_matches"] * 0.45))
    da, _ = fn(df_full[df_full["match_id"].isin(odd_m)], **kw_half)
    db, _ = fn(df_full[df_full["match_id"].isin(even_m)], **kw_half)
    ea = da[da["eligible"]][["player_id", "rank_eb"]].rename(columns={"rank_eb": "ra"})
    eb = db[db["eligible"]][["player_id", "rank_eb"]].rename(columns={"rank_eb": "rb"})
    m = ea.merge(eb, on="player_id", how="inner")
    rho = float(spearmanr(m["ra"], m["rb"]).statistic) if len(m) >= 5 else np.nan
    ov = len(set(ea.nsmallest(10, "ra")["player_id"]) & set(eb.nsmallest(10, "rb")["player_id"]))
    return (round(rho, 4) if not np.isnan(rho) else np.nan), int(ov)


def main() -> None:
    clean_def = pd.read_csv("data/interim/ball_pressure_modeled.csv.gz", low_memory=False)
    clean_ex = build_or_load_exact_modeled()
    mapping = pd.read_csv("data/raw/competition_team_player_mapping.csv")
    map_2026 = set(mapping.loc[mapping["comp_id"] == 3298, "player_id"].astype(int))

    m_sorted = clean_ex[["match_id", "match_date"]].drop_duplicates().sort_values(["match_date", "match_id"])
    odd_m = set(m_sorted.iloc[0::2]["match_id"])
    even_m = set(m_sorted.iloc[1::2]["match_id"])

    combos = [
        {"id": "C01_bye1_li90_anova", "d1": "bye1_repaired", "hp": "is_hp_90", "bat_b": 120, "bwl_b": 100, "min_m": 10, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C02_exact_extras1_diag", "d1": "exact_extras1", "hp": "is_hp_90", "bat_b": 120, "bwl_b": 100, "min_m": 10, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C03_bye1_li75_anova", "d1": "bye1_repaired", "hp": "is_hp_75", "bat_b": 180, "bwl_b": 150, "min_m": 12, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.40, 0.20, 0.15, 0.15, 0.10)},
        {"id": "C04_bye1_li75_k100_w15", "d1": "bye1_repaired", "hp": "is_hp_75", "bat_b": 140, "bwl_b": 120, "min_m": 10, "rec": 2025, "wkt": 15.0, "k_ovr": 100.0, "wts": (0.40, 0.20, 0.15, 0.15, 0.10)},
        {"id": "C05_bye1_li90_relaxed", "d1": "bye1_repaired", "hp": "is_hp_90", "bat_b": 80, "bwl_b": 80, "min_m": 8, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C06_bye1_li90_allyrs", "d1": "bye1_repaired", "hp": "is_hp_90", "bat_b": 120, "bwl_b": 100, "min_m": 10, "rec": 2022, "wkt": 12.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C07_bye1_li90_strict", "d1": "bye1_repaired", "hp": "is_hp_90", "bat_b": 150, "bwl_b": 130, "min_m": 12, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C08_bye1_li90_k100_w15", "d1": "bye1_repaired", "hp": "is_hp_90", "bat_b": 100, "bwl_b": 90, "min_m": 10, "rec": 2025, "wkt": 15.0, "k_ovr": 100.0, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C09_bye1_li90_pure_econ", "d1": "bye1_repaired", "hp": "is_hp_90", "bat_b": 120, "bwl_b": 100, "min_m": 10, "rec": 2025, "wkt": 0.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C10_bye1_li95_extreme", "d1": "bye1_repaired", "hp": "is_hp_95", "bat_b": 60, "bwl_b": 50, "min_m": 6, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.50, 0.15, 0.25, 0.10)},
        {"id": "C11_bye1_ruleB", "d1": "bye1_repaired", "hp": "is_hp_rule", "bat_b": 140, "bwl_b": 120, "min_m": 10, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.40, 0.20, 0.15, 0.15, 0.10)},
        {"id": "C12_bye1_li75_consist35", "d1": "bye1_repaired", "hp": "is_hp_75", "bat_b": 160, "bwl_b": 140, "min_m": 12, "rec": 2025, "wkt": 12.0, "k_ovr": None, "wts": (0.35, 0.15, 0.15, 0.10, 0.25)},
    ]

    out_dir = Path("outputs/gate_combinations")
    out_dir.mkdir(parents=True, exist_ok=True)
    # Remove any legacy *_bat_top25.csv / *_bowl_top25.csv files from prior D1=exact_extras1 runs
    for old_f in out_dir.glob("C*_top25.csv"):
        old_f.unlink()

    summary_rows = []
    bat_matrix = {"rank": list(range(1, 11))}
    bwl_matrix = {"rank": list(range(1, 11))}
    base_bat_top10 = None
    base_bwl_top10 = None

    for cfg in combos:
        cid = cfg["id"]
        df_src = clean_def if cfg["d1"] == "bye1_repaired" else clean_ex
        print(f"Running combination {cid}...")

        bat_kw = dict(hp_col=cfg["hp"], min_hp_balls=cfg["bat_b"], min_hp_matches=cfg["min_m"], recent_cutoff_year=cfg["rec"], weights=cfg["wts"], k_override=cfg["k_ovr"])
        bwl_kw = dict(hp_col=cfg["hp"], min_hp_balls=cfg["bwl_b"], min_hp_matches=cfg["min_m"], recent_cutoff_year=cfg["rec"], weights=cfg["wts"], wkt_run_value=cfg["wkt"], k_override=cfg["k_ovr"])

        bat_df, bat_m = build_batting_ratings(df_src, **bat_kw)
        bwl_df, bwl_m = build_bowling_ratings(df_src, **bwl_kw)

        p10_bat = quick_bootstrap_p_top10(df_src, bat_df, cfg["hp"], "batter", bat_m["k_balls"], cfg["wts"], n_boot=300)
        p10_bwl = quick_bootstrap_p_top10(df_src, bwl_df, cfg["hp"], "bowler", bwl_m["k_balls"], cfg["wts"], wkt_val=cfg["wkt"], n_boot=300)

        bat_df["boot_p_top10_pct"] = bat_df["player_id"].map(p10_bat)
        bwl_df["boot_p_top10_pct"] = bwl_df["player_id"].map(p10_bwl)
        bat_df["in_ipl2026"] = bat_df["player_id"].astype(int).isin(map_2026)
        bwl_df["in_ipl2026"] = bwl_df["player_id"].astype(int).isin(map_2026)

        b_top25 = bat_df[bat_df["eligible"]].head(25)
        w_top25 = bwl_df[bwl_df["eligible"]].head(25)
        b_top25.to_csv(out_dir / f"{cid}_bat_top25.csv", index=False)
        w_top25.to_csv(out_dir / f"{cid}_bowl_top25.csv", index=False)

        b10 = b_top25.head(10)
        w10 = w_top25.head(10)
        if base_bat_top10 is None:
            base_bat_top10 = set(b10["player_id"])
            base_bwl_top10 = set(w10["player_id"])

        bat_matrix[cid] = [f"{r.player_name} ({r.boot_p_top10_pct:.0f}%)" for _, r in b10.iterrows()]
        bwl_matrix[cid] = [f"{r.player_name} ({r.boot_p_top10_pct:.0f}%)" for _, r in w10.iterrows()]

        bat_sh_rho, bat_sh_ov = split_half_rho(df_src, build_batting_ratings, odd_m, even_m, bat_kw)
        bwl_sh_rho, bwl_sh_ov = split_half_rho(df_src, build_bowling_ratings, odd_m, even_m, bwl_kw)

        summary_rows.append({
            "combo_id": cid,
            "d1_runs": cfg["d1"],
            "d8_d9_pressure": cfg["hp"],
            "d12_bwl_wkt_val": cfg["wkt"],
            "d13_k_bat": round(bat_m["k_balls"], 1),
            "d13_k_bwl": round(bwl_m["k_balls"], 1),
            "d14_cutoffs": f"{cfg['bat_b']}b/{cfg['bwl_b']}b, {cfg['min_m']}m, >={cfg['rec']}",
            "d15_weights": str(cfg["wts"]),
            "n_elig_bat": bat_m["n_eligible"],
            "n_elig_bwl": bwl_m["n_eligible"],
            "bat_mean_p_top10": round(float(b10["boot_p_top10_pct"].mean()), 1),
            "bwl_mean_p_top10": round(float(w10["boot_p_top10_pct"].mean()), 1),
            "bat_split_half_rho": bat_sh_rho,
            "bwl_split_half_rho": bwl_sh_rho,
            "bat_overlap_vs_C01": len(set(b10["player_id"]) & base_bat_top10),
            "bwl_overlap_vs_C01": len(set(w10["player_id"]) & base_bwl_top10),
            "bat_top10_in_ipl2026": int(b10["in_ipl2026"].sum()),
            "bwl_top10_in_ipl2026": int(w10["in_ipl2026"].sum()),
        })

    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_csv(out_dir / "summary_metrics.csv", index=False)
    pd.DataFrame(bat_matrix).to_csv(out_dir / "top10_side_by_side_batters.csv", index=False)
    pd.DataFrame(bwl_matrix).to_csv(out_dir / "top10_side_by_side_bowlers.csv", index=False)

    print("\n=== GATE COMBINATION COMPARISON SUMMARY ===")
    cols_show = ["combo_id", "n_elig_bat", "n_elig_bwl", "bat_mean_p_top10", "bwl_mean_p_top10", "bat_split_half_rho", "bwl_split_half_rho", "bat_overlap_vs_C01", "bwl_overlap_vs_C01"]
    print(sum_df[cols_show].to_string(index=False))


if __name__ == "__main__":
    main()
