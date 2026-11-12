#!/usr/bin/env python3
"""
Stage 2: Pressure & Rating Modeling Pipeline
SupeRR Selector Season 2 (Round 1) - Rajasthan Royals Auction Strategy
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import HistGradientBoostingClassifier

def run_stage2_pipeline(data_dir: str = "."):
    print("=" * 70)
    print("STAGE 2: PRESSURE & RATING MODELING PIPELINE")
    print("=" * 70)

    # 1. Load Stage 1 enriched deliveries and player registry
    print("\n[1/6] Loading deliveries_enriched.parquet and player_registry.csv...")
    df = pd.read_parquet(f"{data_dir}/deliveries_enriched.parquet")
    registry = pd.read_csv(f"{data_dir}/player_registry.csv")
    print(f"  - Loaded {len(df):,} deliveries across {df['match_id'].nunique():,} matches.")
    print(f"  - Loaded {len(registry):,} registered players.")

    # 2. Calibrate Win Probability Models (Innings 1 and Innings 2)
    print("\n[2/6] Calibrating Win Probability & Leverage Index models...")
    df_valid = df[df["win_team_id"].notna() & df["innings"].isin([1, 2])].copy()
    df_valid["is_batting_team_win"] = (df_valid["batting_team_id"] == df_valid["win_team_id"]).astype(int)

    # Innings 1 Win Prob Model
    inn1_df = df_valid[df_valid["innings"] == 1]
    features1 = ["pre_legal_balls", "pre_score", "wickets_in_hand", "crr", "wickets_last_18_balls"]
    m1 = HistGradientBoostingClassifier(max_iter=100, min_samples_leaf=50, random_state=42)
    m1.fit(inn1_df[features1], inn1_df["is_batting_team_win"])
    print("  - Innings 1 Win Probability model trained successfully.")

    # Innings 2 Win Prob Model
    inn2_df = df_valid[df_valid["innings"] == 2].copy()
    inn2_df["rrr_safe"] = np.clip(inn2_df["rrr"], 0, 36)
    inn2_df["rate_diff"] = inn2_df["crr"] - inn2_df["rrr_safe"]
    features2 = ["balls_remaining", "runs_needed", "wickets_in_hand", "rrr_safe", "rate_diff", "wickets_last_18_balls"]
    m2 = HistGradientBoostingClassifier(max_iter=100, min_samples_leaf=50, random_state=42)
    m2.fit(inn2_df[features2], inn2_df["is_batting_team_win"])
    print("  - Innings 2 Win Probability model trained successfully.")

    # Predict win probability across all deliveries
    win_prob = np.full(len(df), 0.5, dtype=float)

    # Mask for inn 1
    mask_inn1 = df["innings"] == 1
    win_prob[mask_inn1] = m1.predict_proba(df.loc[mask_inn1, features1])[:, 1]

    # Mask for inn 2
    mask_inn2 = df["innings"] == 2
    temp_inn2 = df.loc[mask_inn2].copy()
    temp_inn2["rrr_safe"] = np.clip(temp_inn2["rrr"], 0, 36)
    temp_inn2["rate_diff"] = temp_inn2["crr"] - temp_inn2["rrr_safe"]
    win_prob[mask_inn2] = m2.predict_proba(temp_inn2[features2])[:, 1]

    # Super Overs: perfectly balanced at 0.5 entering each ball
    mask_so = df["innings"].isin([3, 4])
    win_prob[mask_so] = 0.50

    df["win_prob"] = win_prob

    # Contest Closeness: P_close = 4 * W * (1 - W) in [0, 1]
    df["p_close"] = 4.0 * df["win_prob"] * (1.0 - df["win_prob"])

    # Garbage-time chase filter:
    # When balls_remaining <= 18 and (W < 0.02 or W > 0.98), match is dead.
    is_dead_chase = (df["innings"] == 2) & (df["balls_remaining"] <= 18) & ((df["win_prob"] < 0.02) | (df["win_prob"] > 0.98))
    df["is_dead_chase"] = is_dead_chase.astype(int)

    # 3. Construct Role-Specific Pressure Indices (BPI & BoPI)
    print("\n[3/6] Formulating Batting Pressure Index (BPI) & Bowling Pressure Index (BoPI)...")
    # P_rate
    # Innings 2: Sigmoid on (RRR - par_rr) / 2.2
    rrr_val = df["rrr"].fillna(8.0)
    p_rate_inn2 = 1.0 / (1.0 + np.exp(-(rrr_val - 8.2) / 2.2))
    # Innings 1: Deficit from expected trajectory + over weight
    par_score_by_over = df["overid"] * 8.35
    p_rate_inn1 = 1.0 / (1.0 + np.exp(-(par_score_by_over - df["pre_score"]) / 15.0)) * 0.6 + 0.4 * ((df["overid"] / 20.0) ** 2)
    df["p_rate"] = np.where(df["innings"] == 1, p_rate_inn1, p_rate_inn2)

    # P_wicket: Resource & collapse pressure
    exp_wkts = (df["overid"] / 20.0) * 6.5 + 1.5
    wkt_ratio = df["pre_wickets"] / exp_wkts
    df["p_wicket"] = np.clip(wkt_ratio * 0.5 + 0.25 * df["wickets_last_18_balls"], 0.0, 1.0)

    # P_phase: Time scarcity
    df["p_phase"] = 1.0 - ((df["balls_remaining"] / 120.0) ** 0.75)

    # P_defend (for bowling)
    is_death = df["overid"] >= 16
    is_pp = df["overid"] <= 3
    is_threat = (df["is_set_striker"] == 1) | (df["partnership_runs_pre"] >= 40)
    is_tight_chase = (df["innings"] == 2) & (df["rrr"] >= 6.0) & (df["rrr"] <= 13.5)
    df["p_defend"] = np.clip(
        is_death.astype(float) * 0.40 +
        is_threat.astype(float) * 0.25 +
        is_tight_chase.astype(float) * 0.25 +
        is_pp.astype(float) * 0.10,
        0.0, 1.0
    )

    # Match stakes multiplier
    stakes_mult = np.where(df["is_knockout"] == 1, 1.15, 1.00)

    # Raw BPI & BoPI
    raw_bpi = stakes_mult * (
        0.30 * df["p_close"] +
        0.30 * df["p_rate"] +
        0.25 * df["p_wicket"] +
        0.15 * df["p_phase"]
    )
    raw_bopi = stakes_mult * (
        0.35 * df["p_close"] +
        0.30 * df["p_phase"] +
        0.25 * df["p_defend"] +
        0.10 * (1.0 - df["p_wicket"])
    )

    # Apply garbage-time dead-game attenuation
    bpi = np.where(is_dead_chase, np.minimum(raw_bpi, 0.20), raw_bpi)
    bopi = np.where(is_dead_chase, np.minimum(raw_bopi, 0.20), raw_bopi)

    # Super Overs: fixed at 1.0
    bpi = np.where(df["is_super_over"] == 1, 1.0, bpi)
    bopi = np.where(df["is_super_over"] == 1, 1.0, bopi)

    df["bpi"] = np.clip(bpi, 0.0, 1.0)
    df["bopi"] = np.clip(bopi, 0.0, 1.0)

    # High pressure flags (threshold >= 0.60)
    df["is_hp_bat"] = (df["bpi"] >= 0.60).astype(int)
    df["is_hp_bowl"] = (df["bopi"] >= 0.60).astype(int)

    hp_bat_count = df["is_hp_bat"].sum()
    hp_bowl_count = df["is_hp_bowl"].sum()
    print(f"  - High-Pressure Batting Deliveries (BPI >= 0.60): {hp_bat_count:,} ({hp_bat_count/len(df)*100:.1f}%)")
    print(f"  - High-Pressure Bowling Deliveries (BoPI >= 0.60): {hp_bowl_count:,} ({hp_bowl_count/len(df)*100:.1f}%)")

    # Separation diagnostics
    print("  - Verifying Pressure Index separation properties:")
    for role, p_col in [("Batting (BPI)", "bpi"), ("Bowling (BoPI)", "bopi")]:
        tiers = pd.cut(df[p_col], bins=[-0.01, 0.35, 0.60, 1.01], labels=["Low (<0.35)", "Medium (0.35-0.60)", "High (>=0.60)"])
        diag = df.groupby(tiers, observed=False).agg(
            balls=("match_id", "count"),
            wkt_rate=("is_team_wicket", "mean"),
            dot_rate=("is_dot_batter", "mean"),
            boundary_rate=("is_boundary", "mean"),
            mean_p_close=("p_close", "mean")
        )
        print(f"    * {role}:")
        for idx, row in diag.iterrows():
            print(f"      {idx:18s} | Balls: {int(row['balls']):6,} | Wkt%: {row['wkt_rate']*100:4.1f}% | Dot%: {row['dot_rate']*100:4.1f}% | Bndry%: {row['boundary_rate']*100:4.1f}% | Closeness: {row['mean_p_close']:.2f}")

    # 4. Contextual Par & Expected Value (Dual-Baseline Architecture)
    print("\n[4/6] Computing Contextual Par Expectations (xRuns, xWickets) & Net Value Added...")
    # Stratification bucket: (comp_tier, innings, overid, wkt_bucket)
    wkt_buckets = pd.cut(df["pre_wickets"], bins=[-1, 0, 2, 4, 6, 11], labels=[0, 1, 2, 3, 4]).astype(int)
    df["wkt_bucket"] = wkt_buckets

    strat_keys = ["comp_tier", "innings", "overid", "wkt_bucket"]
    par_table = df.groupby(strat_keys, observed=False).agg(
        mu_runs=("batter_runs", "mean"),
        mu_wkt=("is_batter_out", "mean"),
        mu_bwkt=("is_bowler_wicket", "mean")
    ).reset_index()

    df = df.merge(par_table, on=strat_keys, how="left")

    # Run value of a wicket: dynamically scaled by over (20 down to 8.6 runs)
    lambda_wkt = 8.0 + 12.0 * ((21.0 - np.clip(df["overid"], 1, 20)) / 20.0)
    df["lambda_wkt"] = lambda_wkt

    # Net Value Added per delivery
    df["v_bat"] = (df["batter_runs"] - df["mu_runs"]) - df["lambda_wkt"] * (df["is_batter_out"] - df["mu_wkt"])
    df["v_bowl"] = (df["mu_runs"] - df["bowler_runs"]) + df["lambda_wkt"] * (df["is_bowler_wicket"] - df["mu_bwkt"])

    # 5. Player Aggregation, Empirical Bayes Shrinkage & PRR
    print("\n[5/6] Building Player Baselines, Empirical Bayes Shrinkage, and PRR Ratings...")

    # --- BATTERS ---
    # Filter to legal batter balls for strike rates & value
    bat_df = df[df["is_batter_ball"]].copy()

    # High pressure vs baseline split
    bat_hp = bat_df[bat_df["is_hp_bat"] == 1]
    bat_base = bat_df[bat_df["is_hp_bat"] == 0]

    # Weighted samples
    bat_hp_agg = bat_hp.groupby("striker_id").apply(lambda g: pd.Series({
        "hp_balls": len(g),
        "hp_balls_weighted": (g["comp_weight"]).sum(),
        "hp_balls_ipl_fm": (g["comp_tier"].isin(["IPL", "T20I_FullMember"])).sum(),
        "hp_runs": g["batter_runs"].sum(),
        "hp_outs": g["is_batter_out"].sum(),
        "hp_dots": g["is_dot_batter"].sum(),
        "hp_fours": g["is_four"].sum(),
        "hp_sixes": g["is_six"].sum(),
        "hp_v_sum": (g["v_bat"] * g["comp_weight"]).sum(),
        "hp_matches": g["match_id"].nunique(),
    }), include_groups=False).reset_index()

    bat_base_agg = bat_base.groupby("striker_id").apply(lambda g: pd.Series({
        "base_balls": len(g),
        "base_balls_weighted": (g["comp_weight"]).sum(),
        "base_runs": g["batter_runs"].sum(),
        "base_outs": g["is_batter_out"].sum(),
        "base_v_sum": (g["v_bat"] * g["comp_weight"]).sum(),
    }), include_groups=False).reset_index()

    bat_all = bat_hp_agg.merge(bat_base_agg, on="striker_id", how="left").fillna(0)

    # Compute Match-Level Consistency (C_i) for Batters
    bat_m_outings = bat_hp.groupby(["striker_id", "match_id"]).agg(
        m_balls=("is_batter_ball", "sum"),
        m_v_bat=("v_bat", "sum")
    ).reset_index()
    # Filter to matches where batter faced >= 6 HP balls
    bat_m_qual = bat_m_outings[bat_m_outings["m_balls"] >= 6]
    bat_consistency = bat_m_qual.groupby("striker_id").apply(lambda g: pd.Series({
        "qual_matches": len(g),
        "win_outings": (g["m_v_bat"] > 0).sum(),
        "win_rate": (g["m_v_bat"] > 0).mean() if len(g) > 0 else 0.40,
        "downside_dev": np.sqrt(np.mean(np.minimum(g["m_v_bat"], 0)**2)) if len(g) > 0 else 5.0
    }), include_groups=False).reset_index()
    bat_consistency["consistency_score"] = bat_consistency["win_rate"] - 0.05 * bat_consistency["downside_dev"]

    bat_all = bat_all.merge(bat_consistency, on="striker_id", how="left").fillna({
        "qual_matches": 0, "win_outings": 0, "win_rate": 0.40, "downside_dev": 5.0, "consistency_score": 0.15
    })

    # Eligibility filter for Batters:
    # >= 150 high-pressure balls faced AND >= 100 in IPL + Full Member T20Is
    bat_elig = bat_all[(bat_all["hp_balls"] >= 150) & (bat_all["hp_balls_ipl_fm"] >= 100)].copy()

    # Rates
    bat_elig["hp_sr"] = (bat_elig["hp_runs"] / bat_elig["hp_balls"]) * 100.0
    bat_elig["base_sr"] = np.where(bat_elig["base_balls"] > 0, (bat_elig["base_runs"] / bat_elig["base_balls"]) * 100.0, 130.0)
    bat_elig["hp_dot_pct"] = (bat_elig["hp_dots"] / bat_elig["hp_balls"]) * 100.0
    bat_elig["hp_boundary_pct"] = ((bat_elig["hp_fours"] + bat_elig["hp_sixes"]) / bat_elig["hp_balls"]) * 100.0

    # Mean value per ball
    bat_elig["v_bar_hp"] = bat_elig["hp_v_sum"] / bat_elig["hp_balls_weighted"]
    bat_elig["v_bar_base"] = np.where(bat_elig["base_balls_weighted"] > 0, bat_elig["base_v_sum"] / bat_elig["base_balls_weighted"], 0.0)
    bat_elig["raw_delta"] = bat_elig["v_bar_hp"] - bat_elig["v_bar_base"]

    # Empirical Bayes Shrinkage (kappa_bat = 150, kappa_delta = 120)
    kappa_bat = 150.0
    kappa_delta = 120.0
    prior_mu = 0.0
    bat_elig["shrunk_v_hp"] = (bat_elig["hp_balls_weighted"] / (bat_elig["hp_balls_weighted"] + kappa_bat)) * bat_elig["v_bar_hp"] + (kappa_bat / (bat_elig["hp_balls_weighted"] + kappa_bat)) * prior_mu
    bat_elig["shrunk_delta"] = (bat_elig["hp_balls_weighted"] / (bat_elig["hp_balls_weighted"] + kappa_delta)) * bat_elig["raw_delta"]

    # Z-scores
    def zscore(s):
        std = s.std()
        return (s - s.mean()) / (std if std > 1e-6 else 1.0)

    bat_elig["z_hp"] = zscore(bat_elig["shrunk_v_hp"])
    bat_elig["z_delta"] = zscore(bat_elig["shrunk_delta"])
    bat_elig["z_cons"] = zscore(bat_elig["consistency_score"])

    # Composite PRR: 50% HP Excellence, 25% Delta Over Baseline, 25% Consistency
    bat_elig["raw_prr"] = 0.50 * bat_elig["z_hp"] + 0.25 * bat_elig["z_delta"] + 0.25 * bat_elig["z_cons"]
    # Normalize to 0-100 scouting scale (Mean 50, Std 15)
    bat_elig["prr"] = np.clip(50.0 + 15.0 * bat_elig["raw_prr"], 10.0, 99.9).round(2)

    # Attach player metadata from registry
    bat_leaderboard = bat_elig.merge(registry, left_on="striker_id", right_on="player_id", how="left")
    bat_leaderboard = bat_leaderboard.sort_values("prr", ascending=False).reset_index(drop=True)
    bat_leaderboard["rank"] = bat_leaderboard.index + 1

    # --- BOWLERS ---
    # Filter to legal bowler balls
    bowl_df = df[df["is_bowler_ball"]].copy()

    bowl_hp = bowl_df[bowl_df["is_hp_bowl"] == 1]
    bowl_base = bowl_df[bowl_df["is_hp_bowl"] == 0]

    bowl_hp_agg = bowl_hp.groupby("bowler_id").apply(lambda g: pd.Series({
        "hp_balls": len(g),
        "hp_balls_weighted": (g["comp_weight"]).sum(),
        "hp_balls_ipl_fm": (g["comp_tier"].isin(["IPL", "T20I_FullMember"])).sum(),
        "hp_runs_conceded": g["bowler_runs"].sum(),
        "hp_wickets": g["is_bowler_wicket"].sum(),
        "hp_dots": g["is_dot_bowler"].sum(),
        "hp_boundaries_conceded": g["is_boundary"].sum(),
        "hp_v_sum": (g["v_bowl"] * g["comp_weight"]).sum(),
        "hp_matches": g["match_id"].nunique(),
    }), include_groups=False).reset_index()

    bowl_base_agg = bowl_base.groupby("bowler_id").apply(lambda g: pd.Series({
        "base_balls": len(g),
        "base_balls_weighted": (g["comp_weight"]).sum(),
        "base_runs_conceded": g["bowler_runs"].sum(),
        "base_wickets": g["is_bowler_wicket"].sum(),
        "base_v_sum": (g["v_bowl"] * g["comp_weight"]).sum(),
    }), include_groups=False).reset_index()

    bowl_all = bowl_hp_agg.merge(bowl_base_agg, on="bowler_id", how="left").fillna(0)

    # Match-Level Consistency for Bowlers
    bowl_m_outings = bowl_hp.groupby(["bowler_id", "match_id"]).agg(
        m_balls=("is_bowler_ball", "sum"),
        m_v_bowl=("v_bowl", "sum")
    ).reset_index()
    bowl_m_qual = bowl_m_outings[bowl_m_outings["m_balls"] >= 6]
    bowl_consistency = bowl_m_qual.groupby("bowler_id").apply(lambda g: pd.Series({
        "qual_matches": len(g),
        "win_outings": (g["m_v_bowl"] > 0).sum(),
        "win_rate": (g["m_v_bowl"] > 0).mean() if len(g) > 0 else 0.40,
        "downside_dev": np.sqrt(np.mean(np.minimum(g["m_v_bowl"], 0)**2)) if len(g) > 0 else 5.0
    }), include_groups=False).reset_index()
    bowl_consistency["consistency_score"] = bowl_consistency["win_rate"] - 0.05 * bowl_consistency["downside_dev"]

    bowl_all = bowl_all.merge(bowl_consistency, on="bowler_id", how="left").fillna({
        "qual_matches": 0, "win_outings": 0, "win_rate": 0.40, "downside_dev": 5.0, "consistency_score": 0.15
    })

    # Eligibility filter for Bowlers:
    # >= 180 high-pressure legal balls bowled AND >= 120 in IPL + Full Member T20Is
    bowl_elig = bowl_all[(bowl_all["hp_balls"] >= 180) & (bowl_all["hp_balls_ipl_fm"] >= 120)].copy()

    # Rates
    bowl_elig["hp_econ"] = (bowl_elig["hp_runs_conceded"] / bowl_elig["hp_balls"]) * 6.0
    bowl_elig["base_econ"] = np.where(bowl_elig["base_balls"] > 0, (bowl_elig["base_runs_conceded"] / bowl_elig["base_balls"]) * 6.0, 8.5)
    bowl_elig["hp_dot_pct"] = (bowl_elig["hp_dots"] / bowl_elig["hp_balls"]) * 100.0
    bowl_elig["hp_boundary_conceded_pct"] = (bowl_elig["hp_boundaries_conceded"] / bowl_elig["hp_balls"]) * 100.0

    # Mean value per ball
    bowl_elig["v_bar_hp"] = bowl_elig["hp_v_sum"] / bowl_elig["hp_balls_weighted"]
    bowl_elig["v_bar_base"] = np.where(bowl_elig["base_balls_weighted"] > 0, bowl_elig["base_v_sum"] / bowl_elig["base_balls_weighted"], 0.0)
    bowl_elig["raw_delta"] = bowl_elig["v_bar_hp"] - bowl_elig["v_bar_base"]

    # Empirical Bayes Shrinkage (kappa_bowl = 180, kappa_delta = 140)
    kappa_bowl = 180.0
    kappa_delta_bowl = 140.0
    bowl_elig["shrunk_v_hp"] = (bowl_elig["hp_balls_weighted"] / (bowl_elig["hp_balls_weighted"] + kappa_bowl)) * bowl_elig["v_bar_hp"]
    bowl_elig["shrunk_delta"] = (bowl_elig["hp_balls_weighted"] / (bowl_elig["hp_balls_weighted"] + kappa_delta_bowl)) * bowl_elig["raw_delta"]

    bowl_elig["z_hp"] = zscore(bowl_elig["shrunk_v_hp"])
    bowl_elig["z_delta"] = zscore(bowl_elig["shrunk_delta"])
    bowl_elig["z_cons"] = zscore(bowl_elig["consistency_score"])

    bowl_elig["raw_prr"] = 0.50 * bowl_elig["z_hp"] + 0.25 * bowl_elig["z_delta"] + 0.25 * bowl_elig["z_cons"]
    bowl_elig["prr"] = np.clip(50.0 + 15.0 * bowl_elig["raw_prr"], 10.0, 99.9).round(2)

    bowl_leaderboard = bowl_elig.merge(registry, left_on="bowler_id", right_on="player_id", how="left")
    bowl_leaderboard = bowl_leaderboard.sort_values("prr", ascending=False).reset_index(drop=True)
    bowl_leaderboard["rank"] = bowl_leaderboard.index + 1

    # 6. Extract Top 10 and Save Artifacts
    print("\n[6/6] Extracting Top 10 Batters & Bowlers and Saving Stage 2 Artifacts...")

    top10_bat = bat_leaderboard.head(10).copy()
    top10_bowl = bowl_leaderboard.head(10).copy()

    # Save full leaderboards and Top 10
    bat_leaderboard.to_csv(f"{data_dir}/full_player_pressure_leaderboard_batters.csv", index=False)
    bowl_leaderboard.to_csv(f"{data_dir}/full_player_pressure_leaderboard_bowlers.csv", index=False)

    top10_bat_export = top10_bat[[
        "rank", "player_id", "player_name", "player_display_name", "teams", "is_ipl_player",
        "hp_balls", "hp_runs", "hp_sr", "base_sr", "hp_dot_pct", "hp_boundary_pct",
        "win_rate", "v_bar_hp", "v_bar_base", "shrunk_delta", "prr"
    ]]
    top10_bat_export.to_csv(f"{data_dir}/top_10_batters_under_pressure.csv", index=False)

    top10_bowl_export = top10_bowl[[
        "rank", "player_id", "player_name", "player_display_name", "teams", "is_ipl_player",
        "hp_balls", "hp_wickets", "hp_econ", "base_econ", "hp_dot_pct", "hp_boundary_conceded_pct",
        "win_rate", "v_bar_hp", "v_bar_base", "shrunk_delta", "prr"
    ]]
    top10_bowl_export.to_csv(f"{data_dir}/top_10_bowlers_under_pressure.csv", index=False)

    print("\n" + "=" * 70)
    print("TOP 10 BATTERS UNDER PRESSURE (Rajasthan Royals SupeRR Selector)")
    print("=" * 70)
    print(top10_bat_export[["rank", "player_display_name", "hp_balls", "hp_sr", "base_sr", "win_rate", "prr"]].to_string(index=False))

    print("\n" + "=" * 70)
    print("TOP 10 BOWLERS UNDER PRESSURE (Rajasthan Royals SupeRR Selector)")
    print("=" * 70)
    print(top10_bowl_export[["rank", "player_display_name", "hp_balls", "hp_econ", "base_econ", "hp_wickets", "prr"]].to_string(index=False))

    # Signature Match Case Studies
    print("\nExtracting Signature High-Pressure Match Performances...")
    ranked_pids = set(top10_bat["player_id"]) | set(top10_bowl["player_id"])
    
    # Signature batting innings
    sig_bat = bat_hp[bat_hp["striker_id"].isin(top10_bat["player_id"])].groupby(["striker_id", "match_id"]).agg(
        comp_name=("comp_name", "first"),
        match_date=("match_date", "first"),
        match_result=("result", "first"),
        hp_balls=("is_batter_ball", "sum"),
        hp_runs=("batter_runs", "sum"),
        hp_fours=("is_four", "sum"),
        hp_sixes=("is_six", "sum"),
        net_value=("v_bat", "sum"),
        mean_bpi=("bpi", "mean")
    ).reset_index()
    sig_bat["role"] = "Batter"
    sig_bat = sig_bat.merge(registry[["player_id", "player_name", "player_display_name"]], left_on="striker_id", right_on="player_id")

    # Signature bowling spells
    sig_bowl = bowl_hp[bowl_hp["bowler_id"].isin(top10_bowl["player_id"])].groupby(["bowler_id", "match_id"]).agg(
        comp_name=("comp_name", "first"),
        match_date=("match_date", "first"),
        match_result=("result", "first"),
        hp_balls=("is_bowler_ball", "sum"),
        hp_runs=("bowler_runs", "sum"),
        hp_wickets=("is_bowler_wicket", "sum"),
        net_value=("v_bowl", "sum"),
        mean_bopi=("bopi", "mean")
    ).reset_index()
    sig_bowl["role"] = "Bowler"
    sig_bowl = sig_bowl.merge(registry[["player_id", "player_name", "player_display_name"]], left_on="bowler_id", right_on="player_id")

    # Select top 3 performances per player
    top_sig_bat = sig_bat.sort_values(["player_id", "net_value"], ascending=[True, False]).groupby("player_id").head(3)
    top_sig_bowl = sig_bowl.sort_values(["player_id", "net_value"], ascending=[True, False]).groupby("player_id").head(3)

    sig_all = pd.concat([top_sig_bat, top_sig_bowl], ignore_index=True)
    sig_all.to_csv(f"{data_dir}/signature_pressure_performances.csv", index=False)
    print(f"  - Saved signature_pressure_performances.csv ({len(sig_all)} match case studies).")

    # Save pressure-annotated deliveries parquet for Stage 3 visualizations
    df.to_parquet(f"{data_dir}/deliveries_pressure_modeled.parquet", index=False)
    print(f"  - Saved deliveries_pressure_modeled.parquet ({len(df):,} deliveries).")

    print("\n" + "=" * 70)
    print("STAGE 2 COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_stage2_pipeline(".")
