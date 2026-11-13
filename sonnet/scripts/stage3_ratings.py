"""Stage 3: Format Baselines, Joint Batter-Bowler Ridge, Batting/Bowling Pressure Ratings, EB Shrinkage, & Eligibility."""
from __future__ import annotations

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common import (
    SEED,
    assign_format_bucket,
    balls_faced,
    batter_runs,
    bowler_runs,
    canon_player_ids,
    is_striker_dismissed,
    legal_balls,
)

plt.rcParams.update({"figure.dpi": 140, "axes.spines.top": False, "axes.spines.right": False})


def compute_format_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """Compute format x innings x phase empirical run/wicket/boundary/dot baselines."""
    d = df.copy()
    d["bf"] = balls_faced(d).astype(int)
    d["leg"] = legal_balls(d).astype(int)
    d["bat_runs"] = batter_runs(d)
    d["bwl_runs"] = bowler_runs(d)
    d["is_bdry"] = d["runs"].isin([4, 6]).astype(int)
    d["is_dot"] = (d["team_runs"] == 0).astype(int)
    tab = (
        d[d["dls_flag"] == 0]
        .groupby(["fmt", "innings", "phase"], observed=False)
        .agg(
            deliveries=("runs", "size"),
            legal_balls=("leg", "sum"),
            balls_faced=("bf", "sum"),
            team_rpo=("team_runs", lambda s: float(s.sum() / np.maximum(1, d.loc[s.index, "leg"].sum()) * 6.0)),
            bat_rpb=("bat_runs", lambda s: float(s.sum() / np.maximum(1, d.loc[s.index, "bf"].sum()))),
            bwl_rpo=("bwl_runs", lambda s: float(s.sum() / np.maximum(1, d.loc[s.index, "leg"].sum()) * 6.0)),
            team_wkt_pct=("is_wkt_team", lambda s: float(s.mean() * 100.0)),
            bwl_wkt_pct=("is_wkt_bowler", lambda s: float(s.mean() * 100.0)),
            bdry_pct=("is_bdry", lambda s: float(s.mean() * 100.0)),
            dot_pct=("is_dot", lambda s: float(s.mean() * 100.0)),
        )
        .reset_index()
    )
    return tab


def fit_expected_and_opposition_models(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Fit OOF context baseline AND joint context + batter + bowler Ridge models."""
    d = df.copy()
    d["bat_runs"] = batter_runs(d)
    d["bwl_runs"] = bowler_runs(d)
    d["bf"] = balls_faced(d)
    d["leg"] = legal_balls(d)
    d["strk_out"] = is_striker_dismissed(d).astype(float)
    d["crr_fill"] = d["crr"].fillna(7.5).clip(0.0, 24.0)
    d["rrr_fill"] = d["rrr"].fillna(8.0).clip(0.0, 36.0)
    d["is_inn2"] = (d["innings"] == 2).astype(float)

    num_cols = ["balls_left", "wkts_in_hand", "over_idx", "crr_fill", "rrr_fill", "is_inn2"]
    cat_cols = ["fmt", "phase", "venue_country", "pace_or_spin", "bowling_type", "batting_type", "season"]
    d[cat_cols] = d[cat_cols].fillna("Unknown").astype(str)

    # Fit on clean IPL + T20I pool
    clean_mask = (d["fmt"].isin(["IPL", "T20I"])) & (d["dls_flag"] == 0)

    # 1. Context-only OOF expectation via GroupKFold(match_id)
    enc_ctx = OneHotEncoder(handle_unknown="ignore")
    scaler_num = StandardScaler()
    X_num = scaler_num.fit_transform(d[num_cols].fillna(0.0))
    X_cat = enc_ctx.fit_transform(d[cat_cols])
    X_ctx = hstack([csr_matrix(X_num), X_cat]).tocsr()

    # Joint batter + bowler sparse matrix
    enc_bat = OneHotEncoder(handle_unknown="ignore")
    enc_bwl = OneHotEncoder(handle_unknown="ignore")
    X_bat = enc_bat.fit_transform(d[["striker_id"]].astype(int).astype(str))
    X_bwl = enc_bwl.fit_transform(d[["bowler_id"]].astype(int).astype(str))
    X_joint = hstack([X_ctx, X_bat, X_bwl]).tocsr()

    n_ctx = X_ctx.shape[1]
    n_bat = X_bat.shape[1]

    # Helper for OOF context Ridge prediction
    def oof_ridge_ctx(target_col: str, row_mask: np.ndarray, alpha: float = 50.0) -> np.ndarray:
        idx = np.where(clean_mask.to_numpy() & row_mask)[0]
        y = d.iloc[idx][target_col].to_numpy(dtype=float)
        groups = d.iloc[idx]["match_id"].to_numpy()
        gkf = GroupKFold(n_splits=5)
        oof = np.zeros(len(idx))
        models = []
        for tr, va in gkf.split(X_ctx[idx], y, groups=groups):
            m = Ridge(alpha=alpha, solver="lsqr", max_iter=500, random_state=SEED)
            m.fit(X_ctx[idx[tr]], y[tr])
            oof[va] = m.predict(X_ctx[idx[va]])
            models.append(m)
        pred_all = np.mean([m.predict(X_ctx) for m in models], axis=0)
        pred_all[idx] = oof
        return pred_all

    print("  Fitting OOF Context Baselines (xRuns_ctx, xBwlRuns_ctx, xWkt_bat_ctx, xWkt_bwl_ctx)...")
    bf_mask = d["bf"].to_numpy()
    d["x_bat_runs_ctx"] = np.clip(oof_ridge_ctx("bat_runs", bf_mask, alpha=50.0), 0.0, 6.0)
    d["x_bwl_runs_ctx"] = np.clip(oof_ridge_ctx("bwl_runs", np.ones(len(d), dtype=bool), alpha=50.0), 0.0, 6.0)
    d["x_bat_wkt_ctx"] = np.clip(oof_ridge_ctx("strk_out", bf_mask, alpha=100.0), 0.002, 0.35)
    d["x_bwl_wkt_ctx"] = np.clip(oof_ridge_ctx("is_wkt_bowler", np.ones(len(d), dtype=bool), alpha=100.0), 0.002, 0.35)
    d["is_extra_bwl"] = ((d["is_wide"] == 1) | (d["is_noball"] == 1)).astype(float)
    d["x_bwl_extra_ctx"] = np.clip(oof_ridge_ctx("is_extra_bwl", np.ones(len(d), dtype=bool), alpha=100.0), 0.002, 0.25)

    # 2. Joint Batter-Bowler Ridge model (fit OOF across clean pool so player quality effects have zero match leakage!)
    def oof_joint_opp(target_col: str, row_mask: np.ndarray, alpha: float = 150.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        idx = np.where(clean_mask.to_numpy() & row_mask)[0]
        y = d.iloc[idx][target_col].to_numpy(dtype=float)
        groups = d.iloc[idx]["match_id"].to_numpy()
        gkf = GroupKFold(n_splits=5)
        bat_eff_all = np.zeros(len(d))
        bwl_eff_all = np.zeros(len(d))
        ctx_pred_all = np.zeros(len(d))
        models = []
        for tr, va in gkf.split(X_joint[idx], y, groups=groups):
            m = Ridge(alpha=alpha, solver="lsqr", max_iter=500, random_state=SEED)
            m.fit(X_joint[idx[tr]], y[tr])
            va_rows = idx[va]
            coef_ctx = m.coef_[:n_ctx]
            coef_bat = m.coef_[n_ctx : n_ctx + n_bat]
            coef_bwl = m.coef_[n_ctx + n_bat :]
            ctx_pred_all[va_rows] = X_ctx[va_rows].dot(coef_ctx) + m.intercept_
            bat_eff_all[va_rows] = X_bat[va_rows].dot(coef_bat)
            bwl_eff_all[va_rows] = X_bwl[va_rows].dot(coef_bwl)
            models.append(m)
        # Fallback for rows outside clean_mask: mean fold coefficients
        outside = ~np.isin(np.arange(len(d)), idx)
        if outside.any():
            mean_coef = np.mean([m.coef_ for m in models], axis=0)
            mean_int = float(np.mean([m.intercept_ for m in models]))
            ctx_pred_all[outside] = X_ctx[outside].dot(mean_coef[:n_ctx]) + mean_int
            bat_eff_all[outside] = X_bat[outside].dot(mean_coef[n_ctx : n_ctx + n_bat])
            bwl_eff_all[outside] = X_bwl[outside].dot(mean_coef[n_ctx + n_bat :])
        return ctx_pred_all, bat_eff_all, bwl_eff_all

    print("  Fitting OOF Joint Context + Batter + Bowler Ridge (alpha=150)...")
    c_br, bat_r_eff, bwl_r_eff = oof_joint_opp("bat_runs", bf_mask, alpha=150.0)
    c_bw, bat_w_eff, bwl_w_eff = oof_joint_opp("bwl_runs", np.ones(len(d), dtype=bool), alpha=150.0)
    c_kw, bat_kw_eff, bwl_kw_eff = oof_joint_opp("is_wkt_bowler", np.ones(len(d), dtype=bool), alpha=250.0)

    # Opposition-adjusted expected value:
    # For batter facing bowler j: expected runs = context baseline + bowler j's run-suppression effect (bwl_r_eff)
    # Center bowler/batter opponent effects at zero in clean pool
    bwl_r_eff -= bwl_r_eff[clean_mask & bf_mask].mean()
    bat_w_eff -= bat_w_eff[clean_mask].mean()
    bat_kw_eff -= bat_kw_eff[clean_mask].mean()

    d["opp_bwl_runs_eff"] = bwl_r_eff
    d["opp_bat_runs_eff"] = bat_w_eff
    d["opp_bat_wkt_eff"] = bat_kw_eff

    d["x_bat_runs_adj"] = np.clip(c_br + bwl_r_eff, 0.0, 6.0)
    d["x_bwl_runs_adj"] = np.clip(c_bw + bat_w_eff, 0.0, 6.0)
    d["x_bwl_wkt_adj"] = np.clip(c_kw + bat_kw_eff, 0.002, 0.35)

    meta = {
        "n_clean_rows": int(clean_mask.sum()),
        "x_bat_runs_ctx_mean": float(d.loc[clean_mask & d["bf"], "x_bat_runs_ctx"].mean()),
        "bat_runs_mean": float(d.loc[clean_mask & d["bf"], "bat_runs"].mean()),
        "x_bwl_runs_ctx_mean": float(d.loc[clean_mask, "x_bwl_runs_ctx"].mean()),
        "bwl_runs_mean": float(d.loc[clean_mask, "bwl_runs"].mean()),
        "opp_bwl_runs_eff_std": float(d.loc[clean_mask & d["bf"], "opp_bwl_runs_eff"].std()),
        "opp_bat_runs_eff_std": float(d.loc[clean_mask, "opp_bat_runs_eff"].std()),
    }
    return d, meta


def anova_shrinkage_k(match_vals: pd.Series, match_weights: pd.Series, player_ids: pd.Series) -> tuple[float, float, float]:
    """Estimate Normal-Normal EB shrinkage k = sigma2_within / sigma2_between (in effective ball units).

    Uses one-way random-effects variance decomposition on per-match performance among players with >= 8 matches.
    """
    tmp = pd.DataFrame({"pid": player_ids, "val": match_vals, "w": match_weights}).dropna()
    counts = tmp.groupby("pid")["val"].size()
    keep_pids = counts[counts >= 8].index
    sub = tmp[tmp["pid"].isin(keep_pids)]
    if sub["pid"].nunique() < 10:
        return 60.0, float(tmp["val"].var()), 1.0
    g_stats = sub.groupby("pid").agg(mean=("val", "mean"), var=("val", "var"), n=("val", "size"), w_mean=("w", "mean"))
    sigma2_within_match = float(g_stats["var"].dropna().median())
    var_of_means = float(g_stats["mean"].var())
    mean_n = float(g_stats["n"].mean())
    sigma2_between = max(1e-4, var_of_means - sigma2_within_match / max(1.0, mean_n))
    mean_balls_per_match = float(sub["w"].mean())
    # Within-ball variance ~ sigma2_within_match * mean_balls_per_match -> k in balls
    k_matches = np.clip(sigma2_within_match / sigma2_between, 2.0, 20.0)
    k_balls = float(k_matches * mean_balls_per_match)
    return k_balls, sigma2_within_match, sigma2_between


def zscore(s: pd.Series) -> pd.Series:
    std = float(s.std(ddof=0))
    if std < 1e-12:
        return pd.Series(0.0, index=s.index)
    return (s - float(s.mean())) / std


def build_batting_ratings(
    df: pd.DataFrame,
    hp_col: str = "is_hp_90",
    min_hp_balls: int = 120,
    min_hp_matches: int = 10,
    recent_cutoff_year: int = 2025,
    weights: tuple[float, float, float, float] = (0.50, 0.15, 0.25, 0.10),
    use_opp_adj: bool = True,
    k_override: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Compute batting pressure metrics, EB shrinkage, composite scores, and metadata."""
    d = df.copy()
    d["year"] = pd.to_datetime(d["match_date"]).dt.year
    d["hp"] = d[hp_col].astype(bool)
    x_col = "x_bat_runs_adj" if use_opp_adj else "x_bat_runs_ctx"

    # Canonical names per player_id (most frequent spelling)
    name_map = (
        d.groupby("striker_id")["striker_name"]
        .agg(lambda s: s.value_counts().index[0])
        .to_dict()
    )

    # Dismissals attributed cleanly to dismissed_player_id (including non-striker run-outs!)
    wkt_rows = d[(d["is_wicket"] == 1) & d["dismissed_player_id"].notna()].copy()
    wkt_rows["pid"] = wkt_rows["dismissed_player_id"].astype(int)
    wkt_hp = wkt_rows[wkt_rows["hp"]].groupby("pid").size()
    wkt_nonhp = wkt_rows[~wkt_rows["hp"]].groupby("pid").size()

    # Deliveries faced
    bf_df = d[d["bf"]].copy()
    bf_df["pid"] = bf_df["striker_id"].astype(int)
    bf_df["rae_ball"] = bf_df["bat_runs"] - bf_df[x_col]
    bf_df["rae_ctx_ball"] = bf_df["bat_runs"] - bf_df["x_bat_runs_ctx"]

    # Overall activity per batter (IPL + T20I non-DLS)
    act = (
        bf_df.groupby("pid")
        .agg(
            player_name=("striker_name", lambda s: s.value_counts().index[0]),
            total_matches=("match_id", "nunique"),
            total_bf=("bf", "sum"),
            last_year=("year", "max"),
            ipl_bf=("fmt", lambda s: int((s == "IPL").sum())),
            t20i_bf=("fmt", lambda s: int((s == "T20I").sum())),
        )
    )

    hp_df = bf_df[bf_df["hp"]].copy()
    nhp_df = bf_df[~bf_df["hp"]].copy()

    hp_agg = hp_df.groupby("pid").agg(
        hp_matches=("match_id", "nunique"),
        hp_bf=("bf", "sum"),
        hp_runs=("bat_runs", "sum"),
        hp_xruns=("x_bat_runs_ctx", "sum"),
        hp_xruns_adj=(x_col, "sum"),
        hp_wpa=("delta_wp", "sum"),
        hp_rae_sum=("rae_ball", "sum"),
        hp_rae_ctx_sum=("rae_ctx_ball", "sum"),
        hp_bdries=("runs", lambda s: int(s.isin([4, 6]).sum())),
        hp_dots=("bat_runs", lambda s: int((s == 0).sum())),
        hp_ipl_bf=("fmt", lambda s: int((s == "IPL").sum())),
        hp_t20i_bf=("fmt", lambda s: int((s == "T20I").sum())),
        hp_ipl_rae=("rae_ball", lambda s: float(s[hp_df.loc[s.index, "fmt"] == "IPL"].sum())),
        hp_t20i_rae=("rae_ball", lambda s: float(s[hp_df.loc[s.index, "fmt"] == "T20I"].sum())),
        hp_mean_li=("li", "mean"),
        opp_bwl_diff=("opp_bwl_runs_eff", lambda s: float(-s.mean())),  # positive = tougher bowlers faced
    )

    nhp_agg = nhp_df.groupby("pid").agg(
        nhp_bf=("bf", "sum"),
        nhp_rae_sum=("rae_ball", "sum"),
        nhp_runs=("bat_runs", "sum"),
    )

    # Per-match consistency (matches with >= 4 HP balls faced; winsorised 1-99th pct)
    pm = (
        hp_df.groupby(["pid", "match_id"])
        .agg(m_bf=("bf", "sum"), m_rae=("rae_ball", "sum"), m_wpa=("delta_wp", "sum"))
        .reset_index()
    )
    pm["m_rae100"] = 100.0 * pm["m_rae"] / pm["m_bf"].clip(lower=1)
    pm_elig = pm[pm["m_bf"] >= 4].copy()
    q01, q99 = pm_elig["m_rae100"].quantile([0.01, 0.99]) if len(pm_elig) > 10 else (-150.0, 200.0)
    pm_elig["m_rae100_win"] = pm_elig["m_rae100"].clip(q01, q99)
    pm_elig["pos_match"] = (pm_elig["m_rae"] > 0).astype(float)

    # Estimate EB k from match ANOVA on winsorised m_rae100
    k_auto, sig_w, sig_b = anova_shrinkage_k(pm_elig["m_rae100_win"], pm_elig["m_bf"], pm_elig["pid"])
    k_balls = k_override if k_override is not None else k_auto
    k_wpa = k_balls
    k_nhp = max(k_balls, 80.0)

    cons_agg = pm_elig.groupby("pid").agg(
        hp_cons_matches=("match_id", "nunique"),
        pm_mean_rae100=("m_rae100_win", "mean"),
        pm_std_rae100=("m_rae100_win", lambda s: float(s.std(ddof=1)) if len(s) > 1 else 60.0),
        pm_pos_count=("pos_match", "sum"),
        max_match_rae=("m_rae", "max"),
    )

    res = act.join(hp_agg, how="left").join(nhp_agg, how="left").join(cons_agg, how="left")
    for col in ["hp_matches", "hp_bf", "hp_runs", "hp_xruns", "hp_xruns_adj", "hp_wpa", "hp_rae_sum", "hp_rae_ctx_sum", "nhp_bf", "nhp_rae_sum", "hp_ipl_bf", "hp_t20i_bf", "hp_ipl_rae", "hp_t20i_rae", "hp_cons_matches", "pm_pos_count", "max_match_rae"]:
        res[col] = res[col].fillna(0.0)

    res["hp_outs"] = res.index.map(wkt_hp).fillna(0.0)
    res["nhp_outs"] = res.index.map(wkt_nonhp).fillna(0.0)
    res["hp_sr"] = np.where(res["hp_bf"] > 0, 100.0 * res["hp_runs"] / res["hp_bf"], 0.0)
    res["hp_avg"] = res["hp_runs"] / np.maximum(1.0, res["hp_outs"])
    res["hp_rae100_raw"] = np.where(res["hp_bf"] > 0, 100.0 * res["hp_rae_sum"] / res["hp_bf"], 0.0)
    res["hp_rae100_ctx_raw"] = np.where(res["hp_bf"] > 0, 100.0 * res["hp_rae_ctx_sum"] / res["hp_bf"], 0.0)
    res["hp_wpa100_raw"] = np.where(res["hp_bf"] > 0, 100.0 * res["hp_wpa"] / res["hp_bf"], 0.0)
    res["nhp_rae100_raw"] = np.where(res["nhp_bf"] > 0, 100.0 * res["nhp_rae_sum"] / res["nhp_bf"], 0.0)

    # Prior means estimated on players with >= 60 HP balls
    pool_p = res[res["hp_bf"] >= 60]
    mu_rae = float(pool_p["hp_rae_sum"].sum() / np.maximum(1.0, pool_p["hp_bf"].sum()) * 100.0) if len(pool_p) else 0.0
    mu_wpa = float(pool_p["hp_wpa"].sum() / np.maximum(1.0, pool_p["hp_bf"].sum()) * 100.0) if len(pool_p) else 0.0
    mu_nhp = float(pool_p["nhp_rae_sum"].sum() / np.maximum(1.0, pool_p["nhp_bf"].sum()) * 100.0) if len(pool_p) else 0.0
    mu_pos = float(pool_p["pm_pos_count"].sum() / np.maximum(1.0, pool_p["hp_cons_matches"].sum())) if len(pool_p) else 0.5

    # Empirical Bayes shrinkage towards prior mean
    w_hp = res["hp_bf"] / (res["hp_bf"] + k_balls)
    w_nhp = res["nhp_bf"] / (res["nhp_bf"] + k_nhp)
    res["hp_rae100_eb"] = w_hp * res["hp_rae100_raw"] + (1.0 - w_hp) * mu_rae
    res["hp_wpa100_eb"] = w_hp * res["hp_wpa100_raw"] + (1.0 - w_hp) * mu_wpa
    res["nhp_rae100_eb"] = w_nhp * res["nhp_rae100_raw"] + (1.0 - w_nhp) * mu_nhp
    res["delta_own_rae100"] = res["hp_rae100_eb"] - res["nhp_rae100_eb"]

    # Beta-Binomial positive-match rate shrunk toward pool rate (prior strength m0 = 8 matches) + mean_pm_rae
    m0 = 8.0
    res["pos_match_rate_eb"] = (res["pm_pos_count"] + m0 * mu_pos) / (res["hp_cons_matches"] + m0)
    # Combined consistency metric: 50% shrunk positive-match rate + 50% shrunk Sharpe-like stability
    w_m = res["hp_cons_matches"] / (res["hp_cons_matches"] + m0)
    sharpe_raw = res["pm_mean_rae100"].fillna(0.0) / np.maximum(25.0, res["pm_std_rae100"].fillna(60.0))
    res["pm_sharpe_eb"] = w_m * sharpe_raw

    # Eligibility flag & dependency flags
    res["eligible"] = (
        (res["hp_bf"] >= min_hp_balls)
        & (res["hp_matches"] >= min_hp_matches)
        & (res["last_year"] >= recent_cutoff_year)
    )
    res["max_1match_share"] = np.where(res["hp_rae_sum"] > 0, res["max_match_rae"] / res["hp_rae_sum"], 0.0)
    res["flag_single_match_dep"] = res["max_1match_share"] > 0.35
    res["hp_ipl_share"] = np.where(res["hp_bf"] > 0, res["hp_ipl_bf"] / res["hp_bf"], 0.0)
    res["flag_format_dep"] = (res["hp_ipl_share"] > 0.85) | (res["hp_ipl_share"] < 0.15)
    res["hp_ipl_rae100"] = np.where(res["hp_ipl_bf"] > 0, 100.0 * res["hp_ipl_rae"] / res["hp_ipl_bf"], np.nan)
    res["hp_t20i_rae100"] = np.where(res["hp_t20i_bf"] > 0, 100.0 * res["hp_t20i_rae"] / res["hp_t20i_bf"], np.nan)

    # Composite scoring within eligible pool
    elig = res[res["eligible"]].copy()
    if len(elig) > 1:
        z_rae = zscore(elig["hp_rae100_eb"])
        z_del = zscore(elig["delta_own_rae100"])
        z_con = 0.5 * zscore(elig["pos_match_rate_eb"]) + 0.5 * zscore(elig["pm_sharpe_eb"])
        z_wpa = zscore(elig["hp_wpa100_eb"])
        w1, w2, w3, w4 = weights
        elig["z_rae100"] = z_rae
        elig["z_delta"] = z_del
        elig["z_consistency"] = z_con
        elig["z_wpa100"] = z_wpa
        elig["composite_z"] = w1 * z_rae + w2 * z_del + w3 * z_con + w4 * z_wpa
        elig["pressure_score_0_100"] = 50.0 + 15.0 * elig["composite_z"]
        elig["rank_eb"] = elig["composite_z"].rank(ascending=False, method="min").astype(int)
        elig["rank_raw_rae100"] = elig["hp_rae100_raw"].rank(ascending=False, method="min").astype(int)
        for col in ["z_rae100", "z_delta", "z_consistency", "z_wpa100", "composite_z", "pressure_score_0_100", "rank_eb", "rank_raw_rae100"]:
            res[col] = np.nan
            res.loc[elig.index, col] = elig[col]

    res = res.reset_index().rename(columns={"pid": "player_id"})
    res = res.sort_values(["eligible", "composite_z", "hp_rae100_eb"], ascending=[False, False, False])
    meta = {
        "k_balls": float(k_balls),
        "sigma2_within_match": sig_w,
        "sigma2_between_match": sig_b,
        "prior_mu_rae100": mu_rae,
        "prior_mu_wpa100": mu_wpa,
        "prior_mu_nhp_rae100": mu_nhp,
        "prior_mu_pos_match": mu_pos,
        "pm_winsor_bounds": [float(q01), float(q99)],
        "n_eligible": int(res["eligible"].sum()),
    }
    return res, meta


def build_bowling_ratings(
    df: pd.DataFrame,
    hp_col: str = "is_hp_90",
    min_hp_balls: int = 100,
    min_hp_matches: int = 10,
    recent_cutoff_year: int = 2025,
    weights: tuple[float, float, float, float] = (0.50, 0.15, 0.25, 0.10),
    use_opp_adj: bool = True,
    wkt_run_value: float = 12.0,
    k_override: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Compute bowling pressure metrics, EB shrinkage, composite scores, and metadata."""
    d = df.copy()
    d["year"] = pd.to_datetime(d["match_date"]).dt.year
    d["hp"] = d[hp_col].astype(bool)
    d["pid"] = d["bowler_id"].astype(int)
    xr_col = "x_bwl_runs_adj" if use_opp_adj else "x_bwl_runs_ctx"
    xw_col = "x_bwl_wkt_adj" if use_opp_adj else "x_bwl_wkt_ctx"

    # Per-ball value: Runs Saved + Wicket Value Above Expected (Bowler Perspective)
    d["rsae_runs_ball"] = d[xr_col] - d["bwl_runs"]
    d["wae_ball"] = d["is_wkt_bowler"] - d[xw_col]
    d["total_rsae_ball"] = d["rsae_runs_ball"] + wkt_run_value * d["wae_ball"]
    d["total_rsae_ctx_ball"] = (d["x_bwl_runs_ctx"] - d["bwl_runs"]) + wkt_run_value * (d["is_wkt_bowler"] - d["x_bwl_wkt_ctx"])
    d["disc_saved_ball"] = d["x_bwl_extra_ctx"] - d["is_extra_bwl"]
    d["wpa_saved_ball"] = -d["delta_wp"]

    act = (
        d.groupby("pid")
        .agg(
            player_name=("bowler_name", lambda s: s.value_counts().index[0]),
            primary_pace_spin=("pace_or_spin", lambda s: s.value_counts().index[0]),
            primary_bwl_type=("bowling_type", lambda s: s.value_counts().index[0]),
            total_matches=("match_id", "nunique"),
            total_legal=("leg", "sum"),
            last_year=("year", "max"),
            ipl_legal=("leg", lambda s: int(s[d.loc[s.index, "fmt"] == "IPL"].sum())),
            t20i_legal=("leg", lambda s: int(s[d.loc[s.index, "fmt"] == "T20I"].sum())),
        )
    )

    hp_df = d[d["hp"]].copy()
    nhp_df = d[~d["hp"]].copy()

    hp_agg = hp_df.groupby("pid").agg(
        hp_matches=("match_id", "nunique"),
        hp_balls_all=("runs", "size"),
        hp_legal=("leg", "sum"),
        hp_runs=("bwl_runs", "sum"),
        hp_xruns=(xr_col, "sum"),
        hp_wkts=("is_wkt_bowler", "sum"),
        hp_xwkts=(xw_col, "sum"),
        hp_rsae_sum=("rsae_runs_ball", "sum"),
        hp_total_rsae_sum=("total_rsae_ball", "sum"),
        hp_total_rsae_ctx_sum=("total_rsae_ctx_ball", "sum"),
        hp_wpa_saved=("wpa_saved_ball", "sum"),
        hp_extras_cnt=("is_extra_bwl", "sum"),
        hp_disc_saved=("disc_saved_ball", "sum"),
        hp_dots=("bwl_runs", lambda s: int((s == 0).sum())),
        hp_ipl_legal=("leg", lambda s: int(s[hp_df.loc[s.index, "fmt"] == "IPL"].sum())),
        hp_t20i_legal=("leg", lambda s: int(s[hp_df.loc[s.index, "fmt"] == "T20I"].sum())),
        hp_ipl_trsa=("total_rsae_ball", lambda s: float(s[hp_df.loc[s.index, "fmt"] == "IPL"].sum())),
        hp_t20i_trsa=("total_rsae_ball", lambda s: float(s[hp_df.loc[s.index, "fmt"] == "T20I"].sum())),
        hp_death_share=("phase", lambda s: float((s == "death").mean())),
        hp_pp_share=("phase", lambda s: float((s == "powerplay").mean())),
        hp_mean_li=("li", "mean"),
        opp_bat_quality=("opp_bat_runs_eff", "mean"),  # positive = tougher batters faced
    )

    nhp_agg = nhp_df.groupby("pid").agg(
        nhp_legal=("leg", "sum"),
        nhp_total_rsae_sum=("total_rsae_ball", "sum"),
    )

    # Per-match consistency (>= 4 legal HP balls in a match; winsorised 1-99th pct)
    pm = (
        hp_df.groupby(["pid", "match_id"])
        .agg(m_leg=("leg", "sum"), m_trsa=("total_rsae_ball", "sum"), m_wpa=("wpa_saved_ball", "sum"))
        .reset_index()
    )
    pm["m_trsa24"] = 24.0 * pm["m_trsa"] / pm["m_leg"].clip(lower=1)
    pm_elig = pm[pm["m_leg"] >= 4].copy()
    q01, q99 = pm_elig["m_trsa24"].quantile([0.01, 0.99]) if len(pm_elig) > 10 else (-50.0, 60.0)
    pm_elig["m_trsa24_win"] = pm_elig["m_trsa24"].clip(q01, q99)
    pm_elig["pos_match"] = (pm_elig["m_trsa"] > 0).astype(float)

    k_auto, sig_w, sig_b = anova_shrinkage_k(pm_elig["m_trsa24_win"], pm_elig["m_leg"], pm_elig["pid"])
    k_balls = k_override if k_override is not None else k_auto
    k_nhp = max(k_balls, 80.0)

    cons_agg = pm_elig.groupby("pid").agg(
        hp_cons_matches=("match_id", "nunique"),
        pm_mean_trsa24=("m_trsa24_win", "mean"),
        pm_std_trsa24=("m_trsa24_win", lambda s: float(s.std(ddof=1)) if len(s) > 1 else 25.0),
        pm_pos_count=("pos_match", "sum"),
        max_match_trsa=("m_trsa", "max"),
    )

    res = act.join(hp_agg, how="left").join(nhp_agg, how="left").join(cons_agg, how="left")
    for col in ["hp_matches", "hp_balls_all", "hp_legal", "hp_runs", "hp_xruns", "hp_wkts", "hp_xwkts", "hp_rsae_sum", "hp_total_rsae_sum", "hp_total_rsae_ctx_sum", "hp_wpa_saved", "hp_extras_cnt", "hp_disc_saved", "nhp_legal", "nhp_total_rsae_sum", "hp_ipl_legal", "hp_t20i_legal", "hp_ipl_trsa", "hp_t20i_trsa", "hp_cons_matches", "pm_pos_count", "max_match_trsa"]:
        res[col] = res[col].fillna(0.0)

    res["hp_econ"] = np.where(res["hp_legal"] > 0, 6.0 * res["hp_runs"] / res["hp_legal"], 0.0)
    res["hp_rsae24_runs_raw"] = np.where(res["hp_legal"] > 0, 24.0 * res["hp_rsae_sum"] / res["hp_legal"], 0.0)
    res["hp_wae24_raw"] = np.where(res["hp_legal"] > 0, 24.0 * (res["hp_wkts"] - res["hp_xwkts"]) / res["hp_legal"], 0.0)
    res["hp_total_rsae24_raw"] = np.where(res["hp_legal"] > 0, 24.0 * res["hp_total_rsae_sum"] / res["hp_legal"], 0.0)
    res["hp_total_rsae24_ctx_raw"] = np.where(res["hp_legal"] > 0, 24.0 * res["hp_total_rsae_ctx_sum"] / res["hp_legal"], 0.0)
    res["hp_wpa24_raw"] = np.where(res["hp_legal"] > 0, 24.0 * res["hp_wpa_saved"] / res["hp_legal"], 0.0)
    res["hp_disc24_raw"] = np.where(res["hp_legal"] > 0, 24.0 * res["hp_disc_saved"] / res["hp_legal"], 0.0)
    res["nhp_total_rsae24_raw"] = np.where(res["nhp_legal"] > 0, 24.0 * res["nhp_total_rsae_sum"] / res["nhp_legal"], 0.0)
    res["hp_balls_per_match"] = res["hp_legal"] / np.maximum(1.0, res["total_matches"])

    pool_p = res[res["hp_legal"] >= 60]
    mu_trsa = float(pool_p["hp_total_rsae_sum"].sum() / np.maximum(1.0, pool_p["hp_legal"].sum()) * 24.0) if len(pool_p) else 0.0
    mu_wpa = float(pool_p["hp_wpa_saved"].sum() / np.maximum(1.0, pool_p["hp_legal"].sum()) * 24.0) if len(pool_p) else 0.0
    mu_disc = float(pool_p["hp_disc_saved"].sum() / np.maximum(1.0, pool_p["hp_legal"].sum()) * 24.0) if len(pool_p) else 0.0
    mu_nhp = float(pool_p["nhp_total_rsae_sum"].sum() / np.maximum(1.0, pool_p["nhp_legal"].sum()) * 24.0) if len(pool_p) else 0.0
    mu_pos = float(pool_p["pm_pos_count"].sum() / np.maximum(1.0, pool_p["hp_cons_matches"].sum())) if len(pool_p) else 0.5

    w_hp = res["hp_legal"] / (res["hp_legal"] + k_balls)
    w_nhp = res["nhp_legal"] / (res["nhp_legal"] + k_nhp)
    res["hp_total_rsae24_eb"] = w_hp * res["hp_total_rsae24_raw"] + (1.0 - w_hp) * mu_trsa
    res["hp_wpa24_eb"] = w_hp * res["hp_wpa24_raw"] + (1.0 - w_hp) * mu_wpa
    res["hp_disc24_eb"] = w_hp * res["hp_disc24_raw"] + (1.0 - w_hp) * mu_disc
    res["nhp_total_rsae24_eb"] = w_nhp * res["nhp_total_rsae24_raw"] + (1.0 - w_nhp) * mu_nhp
    res["delta_own_rsae24"] = res["hp_total_rsae24_eb"] - res["nhp_total_rsae24_eb"]

    m0 = 8.0
    res["pos_match_rate_eb"] = (res["pm_pos_count"] + m0 * mu_pos) / (res["hp_cons_matches"] + m0)
    w_m = res["hp_cons_matches"] / (res["hp_cons_matches"] + m0)
    sharpe_raw = res["pm_mean_trsa24"].fillna(0.0) / np.maximum(8.0, res["pm_std_trsa24"].fillna(25.0))
    res["pm_sharpe_eb"] = w_m * sharpe_raw

    res["eligible"] = (
        (res["hp_legal"] >= min_hp_balls)
        & (res["hp_matches"] >= min_hp_matches)
        & (res["last_year"] >= recent_cutoff_year)
    )
    res["max_1match_share"] = np.where(res["hp_total_rsae_sum"] > 0, res["max_match_trsa"] / res["hp_total_rsae_sum"], 0.0)
    res["flag_single_match_dep"] = res["max_1match_share"] > 0.35
    res["hp_ipl_share"] = np.where(res["hp_legal"] > 0, res["hp_ipl_legal"] / res["hp_legal"], 0.0)
    res["flag_format_dep"] = (res["hp_ipl_share"] > 0.85) | (res["hp_ipl_share"] < 0.15)
    res["hp_ipl_trsa24"] = np.where(res["hp_ipl_legal"] > 0, 24.0 * res["hp_ipl_trsa"] / res["hp_ipl_legal"], np.nan)
    res["hp_t20i_trsa24"] = np.where(res["hp_t20i_legal"] > 0, 24.0 * res["hp_t20i_trsa"] / res["hp_t20i_legal"], np.nan)

    elig = res[res["eligible"]].copy()
    if len(elig) > 1:
        z_rsae = zscore(elig["hp_total_rsae24_eb"])
        z_del = zscore(elig["delta_own_rsae24"])
        z_con = 0.5 * zscore(elig["pos_match_rate_eb"]) + 0.5 * zscore(elig["pm_sharpe_eb"])
        z_disc_wpa = 0.5 * zscore(elig["hp_disc24_eb"]) + 0.5 * zscore(elig["hp_wpa24_eb"])
        w1, w2, w3, w4 = weights
        elig["z_rsae24"] = z_rsae
        elig["z_delta"] = z_del
        elig["z_consistency"] = z_con
        elig["z_disc_wpa"] = z_disc_wpa
        elig["composite_z"] = w1 * z_rsae + w2 * z_del + w3 * z_con + w4 * z_disc_wpa
        elig["pressure_score_0_100"] = 50.0 + 15.0 * elig["composite_z"]
        elig["rank_eb"] = elig["composite_z"].rank(ascending=False, method="min").astype(int)
        elig["rank_raw_trsa24"] = elig["hp_total_rsae24_raw"].rank(ascending=False, method="min").astype(int)
        for col in ["z_rsae24", "z_delta", "z_consistency", "z_disc_wpa", "composite_z", "pressure_score_0_100", "rank_eb", "rank_raw_trsa24"]:
            res[col] = np.nan
            res.loc[elig.index, col] = elig[col]

    res = res.reset_index().rename(columns={"pid": "player_id"})
    res = res.sort_values(["eligible", "composite_z", "hp_total_rsae24_eb"], ascending=[False, False, False])
    meta = {
        "k_balls": float(k_balls),
        "sigma2_within_match": sig_w,
        "sigma2_between_match": sig_b,
        "prior_mu_trsa24": mu_trsa,
        "prior_mu_wpa24": mu_wpa,
        "prior_mu_disc24": mu_disc,
        "prior_mu_nhp_trsa24": mu_nhp,
        "prior_mu_pos_match": mu_pos,
        "pm_winsor_bounds": [float(q01), float(q99)],
        "n_eligible": int(res["eligible"].sum()),
    }
    return res, meta


def main() -> None:
    df = pd.read_csv("data/interim/ball_pressure.csv.gz", low_memory=False)
    df = canon_player_ids(df, merge_split_ids=True)
    df["fmt"] = assign_format_bucket(df)

    # Format baselines saved across all non-DLS data (IPL, T20I, Emerging_T20)
    fmt_tab = compute_format_baselines(df)
    fmt_tab.to_csv("outputs/format_baselines.csv", index=False)
    print("Saved outputs/format_baselines.csv")

    print("Fitting Stage 3 expectation and opposition-adjustment models...")
    d_mod, opp_meta = fit_expected_and_opposition_models(df)
    print("Opposition model summary:", json.dumps(opp_meta, indent=2))

    # Primary clean analysis pool: IPL + T20I, non-DLS
    clean = d_mod[(d_mod["fmt"].isin(["IPL", "T20I"])) & (d_mod["dls_flag"] == 0)].copy()

    # Eligibility curve sweep (centered around C03 LI >= 75th pct primary spec)
    print("\nScanning eligibility cutoffs (LI >= 75th pct)...")
    bat_elig_scan = []
    for min_b in [100, 140, 160, 180, 200, 240]:
        for min_m in [10, 12, 14]:
            for rec in [2022, 2025]:
                tmp, _ = build_batting_ratings(clean, hp_col="is_hp_75", min_hp_balls=min_b, min_hp_matches=min_m, recent_cutoff_year=rec)
                bat_elig_scan.append({"role": "batter", "min_hp_balls": min_b, "min_hp_matches": min_m, "recent_yr": rec, "n_eligible": int(tmp["eligible"].sum())})
    bwl_elig_scan = []
    for min_b in [100, 120, 140, 150, 180, 200]:
        for min_m in [10, 12, 14]:
            for rec in [2022, 2025]:
                tmp, _ = build_bowling_ratings(clean, hp_col="is_hp_75", min_hp_balls=min_b, min_hp_matches=min_m, recent_cutoff_year=rec)
                bwl_elig_scan.append({"role": "bowler", "min_hp_balls": min_b, "min_hp_matches": min_m, "recent_yr": rec, "n_eligible": int(tmp["eligible"].sum())})
    elig_scan_df = pd.DataFrame(bat_elig_scan + bwl_elig_scan)
    elig_scan_df.to_csv("outputs/eligibility_scan.csv", index=False)

    # Primary ratings (C03 under D1=bye1_repaired: LI >= 75th pct, >=180 HP balls bat / >=150 HP legal bowl, >=12 HP matches, active >=2025, 50/15/25/10)
    bat_df, bat_meta = build_batting_ratings(clean, hp_col="is_hp_75", min_hp_balls=180, min_hp_matches=12, recent_cutoff_year=2025)
    bwl_df, bwl_meta = build_bowling_ratings(clean, hp_col="is_hp_75", min_hp_balls=150, min_hp_matches=12, recent_cutoff_year=2025)

    # Quick +-10 weight sensitivity check in Stage 3 (including C12 40/15/35/10 consistency tilt)
    weight_configs = [
        ("base_50_15_25_10", (0.50, 0.15, 0.25, 0.10)),
        ("rae_60_10_20_10", (0.60, 0.10, 0.20, 0.10)),
        ("C12_con_40_15_35_10", (0.40, 0.15, 0.35, 0.10)),
        ("wpa_45_15_20_20", (0.45, 0.15, 0.20, 0.20)),
    ]
    for cname, wts in weight_configs:
        if cname == "base_50_15_25_10":
            continue
        tb, _ = build_batting_ratings(clean, hp_col="is_hp_75", min_hp_balls=180, min_hp_matches=12, recent_cutoff_year=2025, weights=wts)
        tw, _ = build_bowling_ratings(clean, hp_col="is_hp_75", min_hp_balls=150, min_hp_matches=12, recent_cutoff_year=2025, weights=wts)
        bat_df[f"rank_{cname}"] = bat_df["player_id"].map(tb.set_index("player_id")["rank_eb"])
        bwl_df[f"rank_{cname}"] = bwl_df["player_id"].map(tw.set_index("player_id")["rank_eb"])

    bat_df.to_csv("outputs/batting_ratings.csv", index=False)
    bwl_df.to_csv("outputs/bowling_ratings.csv", index=False)

    # Save shrinkage_params.json & modeled dataset cache for fast Stage 4
    clean.to_csv("data/interim/ball_pressure_modeled.csv.gz", index=False)
    shrink_params = {"opposition_meta": opp_meta, "batting": bat_meta, "bowling": bwl_meta}
    Path("outputs/shrinkage_params.json").write_text(json.dumps(shrink_params, indent=2))

    # Plot eligibility elbow & raw-vs-EB shrinkage
    fig_dir = Path("outputs/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
    for role, ax, title in [("batter", axes[0], "Batter Eligibility Curve (LI >= 75th pct)"), ("bowler", axes[1], "Bowler Eligibility Curve (LI >= 75th pct)")]:
        sub = elig_scan_df[(elig_scan_df["role"] == role) & (elig_scan_df["min_hp_matches"] == 12)]
        for rec, lbl, col in [(2022, "All 2022-26", "#718096"), (2025, "Active 2025-26 (C03 Primary)", "#2b6cb0")]:
            s2 = sub[sub["recent_yr"] == rec]
            ax.plot(s2["min_hp_balls"], s2["n_eligible"], "o-", label=lbl, color=col)
        ax.axvline(180 if role == "batter" else 150, color="#c53030", linestyle="--", label="C03 Cutoff (180b / 150b)")
        ax.set_title(title)
        ax.set_xlabel("Min High-Pressure Balls (>=12 HP Matches)")
        ax.set_ylabel("Eligible Players")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "eligibility_elbow.png", bbox_inches="tight")
    plt.close(fig)

    print("\n--- TOP 15 BATTERS UNDER PRESSURE (C03 Primary: D1=bye1_repaired, LI >= 75th pct) ---")
    cols_b = ["rank_eb", "player_id", "player_name", "hp_matches", "hp_bf", "hp_runs", "hp_sr", "hp_rae100_raw", "hp_rae100_eb", "delta_own_rae100", "pos_match_rate_eb", "hp_wpa100_eb", "composite_z", "hp_ipl_share"]
    print(bat_df[bat_df["eligible"]].head(15)[cols_b].round(3).to_string(index=False))

    print("\n--- TOP 15 BOWLERS UNDER PRESSURE (C03 Primary: D1=bye1_repaired, LI >= 75th pct) ---")
    cols_w = ["rank_eb", "player_id", "player_name", "primary_pace_spin", "hp_matches", "hp_legal", "hp_wkts", "hp_econ", "hp_total_rsae24_raw", "hp_total_rsae24_eb", "delta_own_rsae24", "pos_match_rate_eb", "hp_wpa24_eb", "composite_z", "hp_ipl_share"]
    print(bwl_df[bwl_df["eligible"]].head(15)[cols_w].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
