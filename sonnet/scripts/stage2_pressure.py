"""Stage 2: Win Probability, Expected Leverage Index (Lens A), and Rule Pressure (Lens B)."""
from __future__ import annotations

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr
from sklearn.calibration import calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from common import SEED, assign_format_bucket, load_ball_state

plt.rcParams.update({"figure.dpi": 140, "axes.spines.top": False, "axes.spines.right": False})


def prepare_features(df: pd.DataFrame, target_col: str = "target") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build strictly pre-delivery feature matrices for Innings 1 and Innings 2 using smoothed CRR (zero ball-1 spikes)."""
    d = df.copy()
    # Prior-smoothed run rate (12-ball Bayesian prior at 7.5 rpo) eliminates 1-ball denominator spikes
    prior_r = np.where(d["fmt"] == "IPL", 17.0, 15.0)
    d["crr_smooth"] = (6.0 * (d["runs_before"] + prior_r) / (d["legal_before"] + 12.0)).clip(0.0, 22.0)
    d["is_ipl"] = (d["fmt"] == "IPL").astype(float)
    d["is_ko"] = d["knock_out"].fillna(0).astype(float)

    # Innings 1 features (pre-delivery only)
    bl1 = d["balls_left"].astype(float).clip(lower=0.0)
    wk1 = d["wkts_in_hand"].astype(float).clip(lower=0.0)
    # DLS-like projected 1st innings score proxy: current runs + remaining resource * format par
    rem_res = (bl1 / 120.0) ** 0.85 * (wk1 / 10.0) ** 0.55
    par_total = np.where(d["fmt"] == "IPL", 180.0, 162.0)
    proj_score = d["runs_before"].astype(float) + rem_res * par_total
    x1 = pd.DataFrame(
        {
            "balls_left": bl1,
            "wkts_in_hand": wk1,
            "runs_before": d["runs_before"].astype(float),
            "crr_smooth": d["crr_smooth"].astype(float),
            "proj_score": proj_score,
            "is_ipl": d["is_ipl"],
            "is_ko": d["is_ko"],
        },
        index=d.index,
    )

    # Innings 2 features (uses specified target_col: repaired 'target' or 'target_raw')
    tgt = d[target_col].fillna(165.0)
    runs_needed = (tgt - d["runs_before"]).clip(lower=0.0)
    bl = d["balls_left"].clip(lower=0.0)
    wk2 = d["wkts_in_hand"].astype(float).clip(lower=0.0)
    rrr_calc = np.where(bl > 0, 6.0 * runs_needed / np.maximum(bl, 1.0), np.where(runs_needed <= 0, 0.0, 36.0))
    rrr_clip = np.clip(rrr_calc, 0.0, 36.0)
    rrr_minus_crr = np.clip(rrr_clip - d["crr_smooth"], -20.0, 30.0)
    res_rem2 = (bl / 120.0) ** 0.85 * (wk2 / 10.0) ** 0.55
    # Par needed rate minus required rate: positive = batting ahead of chase
    chase_cushion = res_rem2 * tgt - runs_needed
    x2 = pd.DataFrame(
        {
            "balls_left": bl.astype(float),
            "wkts_in_hand": wk2,
            "runs_needed": runs_needed.astype(float),
            "rrr_clip": rrr_clip.astype(float),
            "crr_smooth": d["crr_smooth"].astype(float),
            "rrr_minus_crr": rrr_minus_crr.astype(float),
            "chase_cushion": chase_cushion.astype(float),
            "target": tgt.astype(float),
            "is_ipl": d["is_ipl"],
            "is_ko": d["is_ko"],
        },
        index=d.index,
    )
    return x1, x2


def fit_oof_wp(
    df: pd.DataFrame, x: pd.DataFrame, mask_train: np.ndarray
) -> tuple[np.ndarray, np.ndarray, list, dict]:
    """Fit 5-fold GroupKFold(match_id) Logistic and HGB models; return OOF probs and fold models."""
    gkf = GroupKFold(n_splits=5)
    tr_idx = np.where(mask_train)[0]
    y_tr = df.iloc[tr_idx]["batting_won"].astype(int).to_numpy()
    groups = df.iloc[tr_idx]["match_id"].to_numpy()
    X_tr = x.iloc[tr_idx].to_numpy()

    oof_lr = np.zeros(len(tr_idx))
    oof_hgb = np.zeros(len(tr_idx))
    hgb_models = []
    lr_models = []

    for f_tr, f_val in gkf.split(X_tr, y_tr, groups=groups):
        lr = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=SEED)),
            ]
        )
        lr.fit(X_tr[f_tr], y_tr[f_tr])
        oof_lr[f_val] = lr.predict_proba(X_tr[f_val])[:, 1]
        lr_models.append(lr)

        hgb = HistGradientBoostingClassifier(
            max_iter=150,
            max_depth=4,
            learning_rate=0.06,
            min_samples_leaf=80,
            l2_regularization=2.0,
            random_state=SEED,
        )
        hgb.fit(X_tr[f_tr], y_tr[f_tr])
        oof_hgb[f_val] = hgb.predict_proba(X_tr[f_val])[:, 1]
        hgb_models.append(hgb)

    metrics = {
        "lr_brier": float(brier_score_loss(y_tr, oof_lr)),
        "lr_logloss": float(log_loss(y_tr, oof_lr)),
        "lr_auc": float(roc_auc_score(y_tr, oof_lr)),
        "hgb_brier": float(brier_score_loss(y_tr, oof_hgb)),
        "hgb_logloss": float(log_loss(y_tr, oof_hgb)),
        "hgb_auc": float(roc_auc_score(y_tr, oof_hgb)),
    }

    # Predict for all rows: OOF for training rows, fold-average for held-out (DLS/NR/Emerging)
    X_all = x.to_numpy()
    pred_lr_all = np.mean([m.predict_proba(X_all)[:, 1] for m in lr_models], axis=0)
    pred_hgb_all = np.mean([m.predict_proba(X_all)[:, 1] for m in hgb_models], axis=0)
    pred_lr_all[tr_idx] = oof_lr
    pred_hgb_all[tr_idx] = oof_hgb

    # Also pick strictly best-calibrated OOF model family by LogLoss
    best_name = "lr" if metrics["lr_logloss"] <= metrics["hgb_logloss"] else "hgb"
    best_oof = pred_lr_all if best_name == "lr" else pred_hgb_all
    best_models = lr_models if best_name == "lr" else hgb_models
    metrics["selected_model"] = best_name
    return pred_lr_all, pred_hgb_all, best_oof, best_models, metrics


def compute_expected_li(
    df: pd.DataFrame,
    x1_cols: list[str],
    x2_cols: list[str],
    models1: list,
    models2: list,
    wp_before: np.ndarray,
) -> np.ndarray:
    """Compute ex-ante expected |delta WP| using counterfactual delivery transitions and phase outcome rates."""
    d = df.copy()
    prior_r = np.where(d["fmt"] == "IPL", 17.0, 15.0)
    d["is_ipl"] = (d["fmt"] == "IPL").astype(float)
    d["is_ko"] = d["knock_out"].fillna(0).astype(float)
    d["par_total"] = np.where(d["fmt"] == "IPL", 180.0, 162.0)

    # Canonical legal delivery outcomes: (runs_added, wkt_lost)
    # Estimate empirical outcome distribution by (innings, phase, is_ipl) from clean IPL+T20I legal deliveries
    outcomes = [(0, 0), (1, 0), (2, 0), (4, 0), (6, 0), (0, 1)]
    clean = d[(d["fmt"].isin(["IPL", "T20I"])) & (d["dls_flag"] == 0) & (d["is_legal"] == 1)].copy()
    clean["out_bucket"] = np.select(
        [
            clean["is_wkt_team"] == 1,
            clean["team_runs"] == 0,
            clean["team_runs"] == 1,
            clean["team_runs"].isin([2, 3]),
            clean["team_runs"] == 4,
            clean["team_runs"] >= 6,
        ],
        [5, 0, 1, 2, 3, 4],
        default=1,
    )
    prob_table = (
        clean.groupby(["innings", "phase", "is_ipl"])["out_bucket"]
        .value_counts(normalize=True)
        .unstack(fill_value=0.0)
    )
    for k in range(6):
        if k not in prob_table.columns:
            prob_table[k] = 0.0
    prob_table = prob_table[[0, 1, 2, 3, 4, 5]]

    # Default global outcome probs fallback
    global_p = clean["out_bucket"].value_counts(normalize=True).reindex(range(6), fill_value=0.0).to_numpy()

    li_raw = np.zeros(len(d), dtype=float)
    inn1_mask = (d["innings"] == 1).to_numpy()
    inn2_mask = (d["innings"] == 2).to_numpy()

    # Map empirical transition probability matrix per row
    keys = list(zip(d["innings"], d["phase"], d["is_ipl"]))
    pt_dict = {k: v.to_numpy() for k, v in prob_table.iterrows()}
    row_probs = np.vstack([pt_dict.get(k, global_p) for k in keys])

    # Transition helper for Innings 1
    if inn1_mask.any():
        sub = d.loc[inn1_mask]
        bl_new = np.maximum(0.0, sub["balls_left"].to_numpy() - 1.0)
        legal_new = sub["legal_before"].to_numpy() + 1.0
        pr1 = prior_r[inn1_mask]
        par1 = sub["par_total"].to_numpy()
        exp_abs = np.zeros(len(sub))
        p_sub = row_probs[inn1_mask]
        wp0 = wp_before[inn1_mask]
        for k, (r_add, w_lost) in enumerate(outcomes):
            rb_new = sub["runs_before"].to_numpy() + r_add
            wk_new = np.maximum(0.0, sub["wkts_in_hand"].to_numpy() - w_lost)
            crr_new = np.clip(6.0 * (rb_new + pr1) / (legal_new + 12.0), 0.0, 22.0)
            rem_res_new = ((bl_new / 120.0) ** 0.85) * ((wk_new / 10.0) ** 0.55)
            proj_new = rb_new + rem_res_new * par1
            xk = np.column_stack(
                [
                    bl_new,
                    wk_new,
                    rb_new,
                    crr_new,
                    proj_new,
                    sub["is_ipl"].to_numpy(),
                    sub["is_ko"].to_numpy(),
                ]
            )
            wp_next = np.mean([m.predict_proba(xk)[:, 1] for m in models1], axis=0)
            exp_abs += p_sub[:, k] * np.abs(wp_next - wp0)
        li_raw[inn1_mask] = exp_abs

    # Transition helper for Innings 2
    if inn2_mask.any():
        sub = d.loc[inn2_mask]
        tgt = sub["target"].fillna(165.0).to_numpy()
        bl_new = np.maximum(0.0, sub["balls_left"].to_numpy() - 1.0)
        legal_new = sub["legal_before"].to_numpy() + 1.0
        pr2 = prior_r[inn2_mask]
        exp_abs = np.zeros(len(sub))
        p_sub = row_probs[inn2_mask]
        wp0 = wp_before[inn2_mask]
        for k, (r_add, w_lost) in enumerate(outcomes):
            rb_new = sub["runs_before"].to_numpy() + r_add
            wk_new = np.maximum(0.0, sub["wkts_in_hand"].to_numpy() - w_lost)
            rn_new = np.maximum(0.0, tgt - rb_new)
            crr_new = np.clip(6.0 * (rb_new + pr2) / (legal_new + 12.0), 0.0, 22.0)
            rrr_new = np.where(
                rn_new <= 0.0,
                0.0,
                np.where(bl_new > 0.0, np.clip(6.0 * rn_new / np.maximum(bl_new, 1.0), 0.0, 36.0), 36.0),
            )
            rmc_new = np.clip(rrr_new - crr_new, -20.0, 30.0)
            res2_new = ((bl_new / 120.0) ** 0.85) * ((wk_new / 10.0) ** 0.55)
            cush_new = res2_new * tgt - rn_new
            xk = np.column_stack(
                [
                    bl_new,
                    wk_new,
                    rn_new,
                    rrr_new,
                    crr_new,
                    rmc_new,
                    cush_new,
                    tgt,
                    sub["is_ipl"].to_numpy(),
                    sub["is_ko"].to_numpy(),
                ]
            )
            wp_next = np.mean([m.predict_proba(xk)[:, 1] for m in models2], axis=0)
            # Terminal win/loss pins WP to 1 or 0
            wp_next = np.where(rn_new <= 0.0, 1.0, np.where((wk_new <= 0.0) | (bl_new <= 0.0), 0.0, wp_next))
            exp_abs += p_sub[:, k] * np.abs(wp_next - wp0)
        li_raw[inn2_mask] = exp_abs

    return li_raw


def compute_lens_b(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Lens B: Transparent cricket-logic continuous index + binary high-pressure rule flag (~12% balls)."""
    inn2 = df["innings"] == 2
    bl = df["balls_left"].clip(lower=0.0)
    wk_lost = df["wkts_before"].clip(lower=0.0)
    rrr = df["rrr"].fillna(0.0).clip(lower=0.0, upper=36.0)
    rn = df["runs_needed"].fillna(0.0)

    # Continuous rule-based score: tight chase (rrr around 8-14) + death-over urgency + early wickets
    chase_tightness = np.where(
        inn2 & (rn > 0),
        np.exp(-0.5 * ((np.clip(rrr, 0, 30) - 10.0) / 4.0) ** 2) * (0.6 + 1.4 * (1.0 - bl / 120.0)),
        0.0,
    )
    inn1_pressure = np.where(
        ~inn2,
        0.35 * (wk_lost / 5.0) * (0.5 + 0.5 * (bl / 120.0)) + np.where(df["phase"] == "death", 0.35, 0.0),
        0.0,
    )
    ko_bonus = np.where(df["knock_out"].fillna(0) == 1, 0.12, 0.0)
    rule_score = pd.Series(chase_tightness + inn1_pressure + ko_bonus, index=df.index)

    # Binary transparent rule flag (~top 10-14% cricket-intuitive high-pressure situations)
    rule_hp_inn2 = inn2 & (rn > 0) & (
        ((bl <= 30) & (rrr >= 8.0) & (rrr <= 20.0))
        | ((bl > 30) & (bl <= 60) & (wk_lost >= 3) & (rrr >= 8.0) & (rrr <= 16.0))
        | ((wk_lost >= 4) & (rrr >= 7.5) & (rrr <= 15.0))
    )
    rule_hp_inn1 = (~inn2) & (
        ((df["phase"] == "death") & (wk_lost >= 5) & (wk_lost <= 8))
        | ((df["phase"].isin(["powerplay", "middle"])) & (wk_lost >= 4) & (bl >= 42))
    )
    rule_flag = (rule_hp_inn2 | rule_hp_inn1).astype(int)
    return rule_score, rule_flag


def main() -> None:
    df = load_ball_state("data/interim/ball_state.csv.gz")
    df["fmt"] = assign_format_bucket(df)

    # Clean non-DLS, completed, IPL+T20I pool for training WP models
    train_base = (df["fmt"].isin(["IPL", "T20I"])) & (df["dls_flag"] == 0) & (df["batting_won"].notna())
    mask1 = (train_base & (df["innings"] == 1)).to_numpy()
    mask2 = (train_base & (df["innings"] == 2)).to_numpy()

    x1, x2 = prepare_features(df, target_col="target")
    _, x2_raw = prepare_features(df, target_col="target_raw")

    print("Fitting GroupKFold(5, match_id) WP models...")
    lr1, hgb1, best1, models1, met1 = fit_oof_wp(df, x1, mask1)
    lr2, hgb2, best2, models2, met2 = fit_oof_wp(df, x2, mask2)
    lr2_raw, hgb2_raw, best2_raw, models2_raw, met2_raw = fit_oof_wp(df, x2_raw, mask2)

    print("WP OOF Metrics Inn 1:", json.dumps(met1, indent=2))
    print("WP OOF Metrics Inn 2 (repaired target):", json.dumps(met2, indent=2))
    print("WP OOF Metrics Inn 2 (target_raw):", json.dumps(met2_raw, indent=2))

    # Pick OOF-selected best-calibrated WP model per innings
    wp_before = np.where(df["innings"] == 1, best1, best2)
    wp_before_lr = np.where(df["innings"] == 1, lr1, lr2)
    wp_before_raw = np.where(df["innings"] == 1, best1, best2_raw)

    # Compute post-delivery WP for realized WPA (using actual runs_before + team_runs, wkts, balls_left - is_legal)
    d_after = df.copy()
    d_after["runs_before"] = df["cum_runs_after"]
    d_after["wkts_in_hand"] = 10 - df["cum_wkts_after"]
    d_after["legal_before"] = df["legal_after"]
    d_after["balls_left"] = np.maximum(0.0, df["balls_in_innings"] - df["legal_after"])
    d_after["crr"] = np.where(df["legal_after"] > 0, 6.0 * df["cum_runs_after"] / df["legal_after"].replace(0, np.nan), np.nan)
    xa1, xa2 = prepare_features(d_after, target_col="target")

    wp_after = np.zeros(len(df))
    i1 = (df["innings"] == 1).to_numpy()
    i2 = (df["innings"] == 2).to_numpy()
    wp_after[i1] = np.mean([m.predict_proba(xa1.iloc[i1].to_numpy())[:, 1] for m in models1], axis=0)
    wp2_a = np.mean([m.predict_proba(xa2.iloc[i2].to_numpy())[:, 1] for m in models2], axis=0)
    # Terminal chase states after delivery
    rn_after = df.loc[i2, "target"].fillna(165.0).to_numpy() - d_after.loc[i2, "cum_runs_after"].to_numpy()
    bl_after = d_after.loc[i2, "balls_left"].to_numpy()
    wk_after = d_after.loc[i2, "wkts_in_hand"].to_numpy()
    wp2_a = np.where(rn_after <= 0.0, 1.0, np.where((wk_after <= 0.0) | (bl_after <= 0.0), 0.0, wp2_a))
    wp_after[i2] = wp2_a
    delta_wp = wp_after - wp_before

    print("Computing ex-ante Leverage Index (LI = E[|ΔWP|])...")
    li_raw = compute_expected_li(df, list(x1.columns), list(x2.columns), models1, models2, wp_before)
    li_raw_unrep = compute_expected_li(df, list(x1.columns), list(x2_raw.columns), models1, models2_raw, wp_before_raw)

    # Normalize LI so mean == 1.0 across clean IPL + T20I deliveries
    norm_pool = (df["fmt"].isin(["IPL", "T20I"])) & (df["dls_flag"] == 0)
    li_mean = float(li_raw[norm_pool].mean())
    li = li_raw / li_mean
    li_unrep = li_raw_unrep / float(li_raw_unrep[norm_pool].mean())

    p50, p75, p90, p95 = np.quantile(li[norm_pool], [0.50, 0.75, 0.90, 0.95])
    print(f"LI quantiles (clean IPL+T20I): mean={li[norm_pool].mean():.4f}, p50={p50:.3f}, p75={p75:.3f}, p90={p90:.3f}, p95={p95:.3f}, max={li[norm_pool].max():.2f}")

    # Lens B
    rule_score, rule_flag = compute_lens_b(df)
    hp75 = (li >= p75).astype(int)
    hp90 = (li >= p90).astype(int)
    hp95 = (li >= p95).astype(int)

    # Lens A vs Lens B agreement on norm_pool
    rho, _ = spearmanr(li[norm_pool], rule_score[norm_pool])
    j75 = float(((hp75[norm_pool] == 1) & (rule_flag[norm_pool] == 1)).sum() / ((hp75[norm_pool] == 1) | (rule_flag[norm_pool] == 1)).sum())
    j90 = float(((hp90[norm_pool] == 1) & (rule_flag[norm_pool] == 1)).sum() / ((hp90[norm_pool] == 1) | (rule_flag[norm_pool] == 1)).sum())
    j95 = float(((hp95[norm_pool] == 1) & (rule_flag[norm_pool] == 1)).sum() / ((hp95[norm_pool] == 1) | (rule_flag[norm_pool] == 1)).sum())
    rho_raw_tgt, _ = spearmanr(li[norm_pool & i2], li_unrep[norm_pool & i2])
    print(f"Lens A vs Lens B: Spearman rho={rho:.4f}, Jaccard(75)={j75:.4f}, Jaccard(90)={j90:.4f}, Jaccard(95)={j95:.4f}")
    print(f"Inn2 target_repaired vs target_raw LI Spearman rho={rho_raw_tgt:.4f}")

    # Save enriched dataframe
    out_df = df.copy()
    out_df["wp_before"] = wp_before
    out_df["wp_after"] = wp_after
    out_df["delta_wp"] = delta_wp
    out_df["wp_before_lr"] = wp_before_lr
    out_df["li_raw"] = li_raw
    out_df["li"] = li
    out_df["li_target_raw"] = li_unrep
    out_df["is_hp_75"] = hp75
    out_df["is_hp_90"] = hp90
    out_df["is_hp_95"] = hp95
    out_df["pressure_tier"] = np.select(
        [li >= p95, li >= p90, li >= p75, li >= p50],
        ["Extreme (>=95th)", "High (90-95th)", "Elevated (75-90th)", "Medium (50-75th)"],
        default="Low (<50th)",
    )
    out_df["rule_score"] = rule_score
    out_df["is_hp_rule"] = rule_flag
    out_df.to_csv("data/interim/ball_pressure.csv.gz", index=False)
    print(f"Saved data/interim/ball_pressure.csv.gz ({len(out_df):,} rows)")

    # Separation diagnostics on clean IPL+T20I
    sub_c = out_df[norm_pool].copy()
    sub_c["li_bucket"] = np.select(
        [sub_c["li"] >= p90, sub_c["li"] >= p75, sub_c["li"] >= p50],
        ["High+Extreme (>=90th)", "Elevated (75-90th)", "Medium (50-75th)"],
        default="Low (<50th)",
    )
    sep = (
        sub_c.groupby("li_bucket")
        .agg(
            balls=("runs", "size"),
            pct_inn2=("innings", lambda s: float((s == 2).mean() * 100)),
            run_rate=("team_runs", lambda s: float(s.sum() / np.maximum(1, sub_c.loc[s.index, "is_legal"].sum()) * 6.0)),
            boundary_pct=("runs", lambda s: float(s.isin([4, 6]).mean() * 100)),
            dot_pct=("team_runs", lambda s: float((s == 0).mean() * 100)),
            wicket_pct=("is_wkt_team", lambda s: float(s.mean() * 100)),
            mean_li=("li", "mean"),
        )
        .reindex(["Low (<50th)", "Medium (50-75th)", "Elevated (75-90th)", "High+Extreme (>=90th)"])
    )
    print("\nSeparation by LI Bucket (Clean IPL+T20I):")
    print(sep.to_string())

    # Format & Innings LI share
    fmt_inn = (
        sub_c.groupby(["fmt", "innings"])
        .agg(
            balls=("li", "size"),
            mean_li=("li", "mean"),
            pct_hp75=("is_hp_75", lambda s: float(s.mean() * 100)),
            pct_hp90=("is_hp_90", lambda s: float(s.mean() * 100)),
            pct_hp95=("is_hp_95", lambda s: float(s.mean() * 100)),
            pct_rule=("is_hp_rule", lambda s: float(s.mean() * 100)),
        )
    )
    print("\nPressure Share by Format & Innings:")
    print(fmt_inn.to_string())

    # ---- FIGURES ----
    fig_dir = Path("outputs/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Fig 1: LI distribution & threshold tiers
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    vals_i1 = sub_c.loc[sub_c["innings"] == 1, "li"].clip(upper=6.0)
    vals_i2 = sub_c.loc[sub_c["innings"] == 2, "li"].clip(upper=6.0)
    axes[0].hist(vals_i1, bins=55, alpha=0.55, density=True, label="Innings 1 (Setting)", color="#2b6cb0")
    axes[0].hist(vals_i2, bins=55, alpha=0.55, density=True, label="Innings 2 (Chasing)", color="#dd6b20")
    for pct_val, lbl, col in [(p75, f"75th ({p75:.2f})", "#718096"), (p90, f"90th ({p90:.2f})", "#c53030"), (p95, f"95th ({p95:.2f})", "#742a2a")]:
        axes[0].axvline(pct_val, color=col, linestyle="--", linewidth=1.4, label=lbl)
    axes[0].set_title("Leverage Index (LI) Distribution (Normalized Mean = 1.0)")
    axes[0].set_xlabel("Leverage Index (clipped at 6.0 for display)")
    axes[0].set_ylabel("Density")
    axes[0].legend(fontsize=8)

    # Separation bar chart
    x_pos = np.arange(len(sep))
    w = 0.28
    axes[1].bar(x_pos - w, sep["run_rate"], width=w, label="Run Rate (rpo)", color="#3182ce")
    axes[1].bar(x_pos, sep["wicket_pct"] * 2.0, width=w, label="Wicket Rate (%) x 2", color="#e53e3e")
    axes[1].bar(x_pos + w, sep["boundary_pct"], width=w, label="Boundary Rate (%)", color="#38a169")
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(["Low\n(<50th)", "Medium\n(50-75th)", "Elevated\n(75-90th)", "High+\n(>=90th)"], fontsize=9)
    axes[1].set_title("Behavioral Separation Across LI Tiers")
    axes[1].set_ylabel("Rate")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "li_distribution.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 2: 2nd-innings heatmap (balls_left bin x wkts_in_hand)
    sub2 = sub_c[sub_c["innings"] == 2].copy()
    sub2["over_bin"] = pd.cut(20 - sub2["balls_left"] / 6.0, bins=[0, 4, 8, 12, 16, 18, 20.1], labels=["1-4", "5-8", "9-12", "13-16", "17-18", "19-20"])
    piv_li = sub2.pivot_table(index="wkts_in_hand", columns="over_bin", values="li", aggfunc="mean", observed=False).sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    sns.heatmap(piv_li, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax, cbar_kws={"label": "Mean Leverage Index (LI)"})
    ax.set_title("2nd-Innings Mean Leverage Index by Overs Elapsed & Wickets in Hand")
    ax.set_xlabel("Overs Elapsed Bucket")
    ax.set_ylabel("Wickets in Hand")
    fig.tight_layout()
    fig.savefig(fig_dir / "pressure_heatmap_chase.png", bbox_inches="tight")
    plt.close(fig)

    # Fig 3: WP calibration curves (Innings 1 & Innings 2 OOF)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, mask, lr_p, hgb_p, title in [
        (axes[0], mask1, lr1, hgb1, "Innings 1 WP Calibration (OOF)"),
        (axes[1], mask2, lr2, hgb2, "Innings 2 WP Calibration (OOF)"),
    ]:
        yt = df.loc[mask, "batting_won"].astype(int).to_numpy()
        p_lr_t, p_lr_p = calibration_curve(yt, lr_p[mask], n_bins=10)
        p_hg_t, p_hg_p = calibration_curve(yt, hgb_p[mask], n_bins=10)
        ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect")
        ax.plot(p_lr_p, p_lr_t, "o-", label=f"Logistic", color="#3182ce")
        ax.plot(p_hg_p, p_hg_t, "s-", label=f"HGB", color="#dd6b20")
        ax.set_title(title)
        ax.set_xlabel("Predicted Win Probability")
        ax.set_ylabel("Observed Win Frequency")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "wp_calibration.png", bbox_inches="tight")
    plt.close(fig)

    # Save structured stage 2 stats JSON for notes & report
    stats = {
        "inn1_wp": met1,
        "inn2_wp_repaired": met2,
        "inn2_wp_raw": met2_raw,
        "li_quantiles": {"p50": float(p50), "p75": float(p75), "p90": float(p90), "p95": float(p95)},
        "lens_agreement": {
            "spearman_rho": float(rho),
            "jaccard_75": j75,
            "jaccard_90": j90,
            "jaccard_95": j95,
            "target_repaired_vs_raw_rho": float(rho_raw_tgt),
            "rule_pct_clean": float(rule_flag[norm_pool].mean() * 100),
        },
        "separation": sep.reset_index().to_dict(orient="records"),
        "format_innings": fmt_inn.reset_index().to_dict(orient="records"),
    }
    Path("outputs/stage2_stats.json").write_text(json.dumps(stats, indent=2))
    print("Saved outputs/stage2_stats.json and figures.")


if __name__ == "__main__":
    main()
