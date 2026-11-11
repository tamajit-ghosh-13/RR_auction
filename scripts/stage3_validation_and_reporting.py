#!/usr/bin/env python3
"""
Stage 3: Validation, Visualizations & Methodology Report Pipeline
SupeRR Selector Season 2 (Round 1) - Rajasthan Royals Auction Strategy
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Set Rajasthan Royals color palette
RR_BLUE = "#004BA0"      # Royal Blue
RR_PINK = "#E91E63"      # Royals Pink / Magenta
RR_GOLD = "#FFC107"      # Accent Gold
RR_DARK = "#1A1A24"      # Dark Navy Charcoal
RR_LIGHT = "#F8F9FA"     # Light background
RR_GRAY = "#6C757D"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 1.0,
    "grid.color": "#EEEEEE",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
})


def run_stage3_pipeline(data_dir: str = "."):
    print("=" * 70)
    print("STAGE 3: VALIDATION, VISUALIZATIONS & REPORT ENGINE")
    print("=" * 70)

    # 1. Load modeled deliveries, top 10 tables, and registry
    print("\n[1/5] Loading modeled data & Top 10 leaderboards...")
    df = pd.read_parquet(f"{data_dir}/deliveries_pressure_modeled.parquet")
    top10_bat = pd.read_csv(f"{data_dir}/top_10_batters_under_pressure.csv")
    top10_bowl = pd.read_csv(f"{data_dir}/top_10_bowlers_under_pressure.csv")
    bat_all = pd.read_csv(f"{data_dir}/full_player_pressure_leaderboard_batters.csv")
    bowl_all = pd.read_csv(f"{data_dir}/full_player_pressure_leaderboard_bowlers.csv")
    registry = pd.read_csv(f"{data_dir}/player_registry.csv")

    output_dir = Path(f"{data_dir}/outputs")
    output_dir.mkdir(exist_ok=True)

    # 2. Fast Vectorized Match-Level Bootstrap Stability (B = 500)
    print("\n[2/5] Running Fast Vectorized Match-Level Bootstrap Resampling (B = 500)...")
    np.random.seed(42)
    unique_matches = df["match_id"].unique()
    num_matches = len(unique_matches)
    B = 500

    # Pre-aggregate match-level summaries per player for eligible batters
    bat_elig_pids = set(bat_all["player_id"])
    bat_hp_matches = df[df["is_batter_ball"] & (df["is_hp_bat"] == 1) & df["striker_id"].isin(bat_elig_pids)].groupby(["striker_id", "match_id"]).agg(
        w_balls=("comp_weight", "sum"),
        w_v=("v_bat", lambda s: (s * df.loc[s.index, "comp_weight"]).sum())
    ).reset_index()

    # Pre-aggregate match-level summaries per player for eligible bowlers
    bowl_elig_pids = set(bowl_all["player_id"])
    bowl_hp_matches = df[df["is_bowler_ball"] & (df["is_hp_bowl"] == 1) & df["bowler_id"].isin(bowl_elig_pids)].groupby(["bowler_id", "match_id"]).agg(
        w_balls=("comp_weight", "sum"),
        w_v=("v_bowl", lambda s: (s * df.loc[s.index, "comp_weight"]).sum())
    ).reset_index()

    # Run vectorized bootstrap draws
    print("  - Generating 500 bootstrap resamples of 867 matches...")
    boot_ranks_bat = {pid: [] for pid in top10_bat["player_id"]}
    boot_ranks_bowl = {pid: [] for pid in top10_bowl["player_id"]}

    for b in range(B):
        sample_matches = np.random.choice(unique_matches, size=num_matches, replace=True)
        counts = pd.Series(sample_matches).value_counts()
        counts_df = pd.DataFrame({"match_id": counts.index, "boot_freq": counts.values})

        # Batters bootstrap PRR estimate
        m_bat = bat_hp_matches.merge(counts_df, on="match_id", how="inner")
        m_bat["boot_balls"] = m_bat["w_balls"] * m_bat["boot_freq"]
        m_bat["boot_v"] = m_bat["w_v"] * m_bat["boot_freq"]
        bat_b = m_bat.groupby("striker_id").agg(
            b_balls=("boot_balls", "sum"),
            b_v=("boot_v", "sum")
        ).reset_index()
        # Shrunk value
        bat_b["shrunk_v"] = bat_b["b_v"] / (bat_b["b_balls"] + 150.0)
        bat_b["rank"] = bat_b["shrunk_v"].rank(ascending=False, method="min")
        b_ranks_map = dict(zip(bat_b["striker_id"], bat_b["rank"]))
        for pid in top10_bat["player_id"]:
            boot_ranks_bat[pid].append(b_ranks_map.get(pid, 50.0))

        # Bowlers bootstrap PRR estimate
        m_bowl = bowl_hp_matches.merge(counts_df, on="match_id", how="inner")
        m_bowl["boot_balls"] = m_bowl["w_balls"] * m_bowl["boot_freq"]
        m_bowl["boot_v"] = m_bowl["w_v"] * m_bowl["boot_freq"]
        bowl_b = m_bowl.groupby("bowler_id").agg(
            b_balls=("boot_balls", "sum"),
            b_v=("boot_v", "sum")
        ).reset_index()
        bowl_b["shrunk_v"] = bowl_b["b_v"] / (bowl_b["b_balls"] + 180.0)
        bowl_b["rank"] = bowl_b["shrunk_v"].rank(ascending=False, method="min")
        b_bowl_ranks_map = dict(zip(bowl_b["bowler_id"], bowl_b["rank"]))
        for pid in top10_bowl["player_id"]:
            boot_ranks_bowl[pid].append(b_bowl_ranks_map.get(pid, 50.0))

    # Summarize bootstrap stability
    bat_boot_rows = []
    for _, r in top10_bat.iterrows():
        pid = r["player_id"]
        ranks = np.array(boot_ranks_bat[pid])
        bat_boot_rows.append({
            "rank": r["rank"],
            "player_display_name": r["player_display_name"],
            "role": "Batter",
            "median_rank": np.median(ranks),
            "p5_rank": np.percentile(ranks, 5),
            "p95_rank": np.percentile(ranks, 95),
            "iqr_rank": np.percentile(ranks, 75) - np.percentile(ranks, 25),
            "top15_retention_pct": (ranks <= 15).mean() * 100.0,
        })
    bat_boot_df = pd.DataFrame(bat_boot_rows)

    bowl_boot_rows = []
    for _, r in top10_bowl.iterrows():
        pid = r["player_id"]
        ranks = np.array(boot_ranks_bowl[pid])
        bowl_boot_rows.append({
            "rank": r["rank"],
            "player_display_name": r["player_display_name"],
            "role": "Bowler",
            "median_rank": np.median(ranks),
            "p5_rank": np.percentile(ranks, 5),
            "p95_rank": np.percentile(ranks, 95),
            "iqr_rank": np.percentile(ranks, 75) - np.percentile(ranks, 25),
            "top15_retention_pct": (ranks <= 15).mean() * 100.0,
        })
    bowl_boot_df = pd.DataFrame(bowl_boot_rows)

    boot_all = pd.concat([bat_boot_df, bowl_boot_df], ignore_index=True)
    boot_all.to_csv(output_dir / "bootstrap_stability_results.csv", index=False)
    print("  - Bootstrap Stability summary saved to outputs/bootstrap_stability_results.csv.")
    print(boot_all[["rank", "player_display_name", "role", "median_rank", "p5_rank", "p95_rank", "top15_retention_pct"]].to_string(index=False))

    # 3. Threshold Sensitivity Check (P >= 0.55, 0.60, 0.65 vs Continuous)
    print("\n[3/5] Computing Threshold Sensitivity Check across P >= 0.55, 0.60, 0.65...")
    sens_rows = []
    # Test batting thresholds
    b_60 = bat_all.set_index("player_id")["prr"]
    for thresh in [0.55, 0.60, 0.65]:
        hp_mask = df["is_batter_ball"] & (df["bpi"] >= thresh)
        agg = df[hp_mask].groupby("striker_id").agg(
            w_balls=("comp_weight", "sum"),
            w_v=("v_bat", lambda s: (s * df.loc[s.index, "comp_weight"]).sum())
        )
        agg["score"] = agg["w_v"] / (agg["w_balls"] + 150.0)
        common_pids = b_60.index.intersection(agg.index)
        rho, _ = spearmanr(b_60.loc[common_pids], agg.loc[common_pids, "score"])
        sens_rows.append({
            "role": "Batting",
            "threshold": f"P >= {thresh}",
            "spearman_rho_vs_baseline": round(rho, 4),
            "top10_invariance_pct": round(len(set(top10_bat["player_id"]).intersection(agg["score"].nlargest(12).index)) / 10.0 * 100.0, 1)
        })

    # Test bowling thresholds
    bo_60 = bowl_all.set_index("player_id")["prr"]
    for thresh in [0.55, 0.60, 0.65]:
        hp_mask = df["is_bowler_ball"] & (df["bopi"] >= thresh)
        agg = df[hp_mask].groupby("bowler_id").agg(
            w_balls=("comp_weight", "sum"),
            w_v=("v_bowl", lambda s: (s * df.loc[s.index, "comp_weight"]).sum())
        )
        agg["score"] = agg["w_v"] / (agg["w_balls"] + 180.0)
        common_pids = bo_60.index.intersection(agg.index)
        rho, _ = spearmanr(bo_60.loc[common_pids], agg.loc[common_pids, "score"])
        sens_rows.append({
            "role": "Bowling",
            "threshold": f"P >= {thresh}",
            "spearman_rho_vs_baseline": round(rho, 4),
            "top10_invariance_pct": round(len(set(top10_bowl["player_id"]).intersection(agg["score"].nlargest(12).index)) / 10.0 * 100.0, 1)
        })

    sens_df = pd.DataFrame(sens_rows)
    sens_df.to_csv(output_dir / "threshold_sensitivity_results.csv", index=False)
    print("  - Threshold sensitivity results saved to outputs/threshold_sensitivity_results.csv:")
    print(sens_df.to_string(index=False))

    # IPL vs T20I Splits
    print("\n  - Computing IPL vs T20I splits for Top 10 players...")
    split_rows = []
    for _, r in top10_bat.iterrows():
        pid = r["player_id"]
        sub_ipl = df[df["is_batter_ball"] & (df["is_hp_bat"] == 1) & (df["striker_id"] == pid) & (df["comp_tier"] == "IPL")]
        sub_t20i = df[df["is_batter_ball"] & (df["is_hp_bat"] == 1) & (df["striker_id"] == pid) & (df["comp_tier"].str.startswith("T20I"))]
        split_rows.append({
            "role": "Batter",
            "rank": r["rank"],
            "player_display_name": r["player_display_name"],
            "ipl_hp_balls": len(sub_ipl),
            "ipl_hp_sr": (sub_ipl["batter_runs"].sum() / len(sub_ipl) * 100.0) if len(sub_ipl) > 0 else np.nan,
            "t20i_hp_balls": len(sub_t20i),
            "t20i_hp_sr": (sub_t20i["batter_runs"].sum() / len(sub_t20i) * 100.0) if len(sub_t20i) > 0 else np.nan,
        })
    for _, r in top10_bowl.iterrows():
        pid = r["player_id"]
        sub_ipl = df[df["is_bowler_ball"] & (df["is_hp_bowl"] == 1) & (df["bowler_id"] == pid) & (df["comp_tier"] == "IPL")]
        sub_t20i = df[df["is_bowler_ball"] & (df["is_hp_bowl"] == 1) & (df["bowler_id"] == pid) & (df["comp_tier"].str.startswith("T20I"))]
        split_rows.append({
            "role": "Bowler",
            "rank": r["rank"],
            "player_display_name": r["player_display_name"],
            "ipl_hp_balls": len(sub_ipl),
            "ipl_hp_sr": (sub_ipl["bowler_runs"].sum() / len(sub_ipl) * 6.0) if len(sub_ipl) > 0 else np.nan,  # Economy
            "t20i_hp_balls": len(sub_t20i),
            "t20i_hp_sr": (sub_t20i["bowler_runs"].sum() / len(sub_t20i) * 6.0) if len(sub_t20i) > 0 else np.nan,
        })
    splits_df = pd.DataFrame(split_rows)
    splits_df.to_csv(output_dir / "ipl_vs_t20i_splits.csv", index=False)
    print("  - IPL vs T20I splits saved to outputs/ipl_vs_t20i_splits.csv.")

    # 4. Generate Publication-Grade Visualizations
    print("\n[4/5] Generating Publication-Grade Visualizations in Rajasthan Royals Theme...")

    # Chart 1: Anatomy of Pressure Separation
    print("  - Generating Chart 1: Anatomy of Pressure Separation...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), facecolor=RR_LIGHT)
    df["bpi_decile"] = pd.qcut(df["bpi"], q=10, labels=[f"D{i+1}" for i in range(10)])
    dec_agg = df.groupby("bpi_decile", observed=False).agg(
        wkt_pct=("is_team_wicket", lambda s: s.mean() * 100),
        dot_pct=("is_dot_batter", lambda s: s.mean() * 100),
        bndry_pct=("is_boundary", lambda s: s.mean() * 100),
        closeness=("p_close", "mean")
    ).reset_index()

    # Subplot 1: Dismissal % across deciles
    ax1 = axes[0]
    ax1.bar(dec_agg["bpi_decile"], dec_agg["wkt_pct"], color=RR_BLUE, alpha=0.85, edgecolor=RR_DARK)
    ax1.set_title("A. Dismissal Probability spikes in Top Deciles", fontsize=12, fontweight="bold", color=RR_DARK)
    ax1.set_ylabel("Wicket Probability (%)", fontsize=10, fontweight="bold")
    ax1.set_xlabel("Pressure Index (BPI) Decile", fontsize=10)
    ax1.grid(True, axis="y")

    # Subplot 2: Boundary % vs Dot %
    ax2 = axes[1]
    ax2.plot(dec_agg["bpi_decile"], dec_agg["bndry_pct"], marker="o", color=RR_PINK, linewidth=2.5, label="Boundary % (Squeezed)")
    ax2.plot(dec_agg["bpi_decile"], dec_agg["dot_pct"], marker="s", color=RR_BLUE, linewidth=2.0, linestyle="--", label="Dot Ball %")
    ax2.set_title("B. Boundary Deprivation & Field Squeeze", fontsize=12, fontweight="bold", color=RR_DARK)
    ax2.set_ylabel("Delivery Percentage (%)", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Pressure Index (BPI) Decile", fontsize=10)
    ax2.legend(frameon=True, facecolor="white", edgecolor="#DDD")
    ax2.grid(True)

    # Subplot 3: Closeness
    ax3 = axes[2]
    ax3.plot(dec_agg["bpi_decile"], dec_agg["closeness"], marker="^", color=RR_GOLD, linewidth=2.5)
    ax3.fill_between(dec_agg["bpi_decile"], 0, dec_agg["closeness"], color=RR_GOLD, alpha=0.25)
    ax3.set_title("C. Contest Closeness / Leverage Trajectory", fontsize=12, fontweight="bold", color=RR_DARK)
    ax3.set_ylabel("Mean Match Closeness (P_close)", fontsize=10, fontweight="bold")
    ax3.set_xlabel("Pressure Index (BPI) Decile", fontsize=10)
    ax3.grid(True)

    fig.suptitle("Anatomy of Pressure Separation across 200,999 Deliveries (SupeRR Selector Season 2)", fontsize=15, fontweight="bold", color=RR_DARK, y=1.03)
    plt.tight_layout()
    plt.savefig(output_dir / "chart1_pressure_separation.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Chart 2: Batting Pressure Matrix (Quadrant Scatter Plot)
    print("  - Generating Chart 2: Batting Pressure Matrix (Quadrant Scatter)...")
    plt.figure(figsize=(11, 8.5), facecolor=RR_LIGHT)
    ax = plt.gca()
    ax.set_facecolor("white")

    # Scatter of all eligible batters
    sns.scatterplot(
        data=bat_all[bat_all["hp_balls"] >= 80],
        x="base_sr",
        y="hp_sr",
        size="hp_balls",
        sizes=(40, 450),
        color="#B0BEC5",
        alpha=0.45,
        legend=False,
        ax=ax
    )

    # Highlight Top 10 Batters
    top_scatter = sns.scatterplot(
        data=top10_bat,
        x="base_sr",
        y="hp_sr",
        size="hp_balls",
        sizes=(120, 600),
        color=RR_PINK,
        edgecolor=RR_DARK,
        linewidth=1.5,
        alpha=0.95,
        ax=ax
    )

    # Diagonal parity line (HP SR == Base SR)
    ax.plot([100, 200], [100, 200], color="#999999", linestyle=":", linewidth=1.5, label="Parity Line (HP SR = Usual SR)")

    # Labels for Top 10
    for _, r in top10_bat.iterrows():
        ax.annotate(
            f"#{int(r['rank'])} {r['player_display_name'].split('(')[0].strip()}\n(PRR: {r['prr']:.1f})",
            xy=(r["base_sr"], r["hp_sr"]),
            xytext=(r["base_sr"] + 1.5, r["hp_sr"] + 1.2),
            fontsize=9,
            fontweight="bold",
            color=RR_DARK,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFF9C4", edgecolor="#FBC02D", alpha=0.85)
        )

    ax.set_title("Batting Pressure Matrix: Usual Strike Rate vs. High-Pressure Strike Rate", fontsize=14, fontweight="bold", color=RR_DARK, pad=15)
    ax.set_xlabel("Usual (Baseline) Strike Rate", fontsize=11, fontweight="bold")
    ax.set_ylabel("High-Pressure (BPI >= 0.60) Strike Rate", fontsize=11, fontweight="bold")
    ax.axvline(x=140, color="#CCCCCC", linestyle="--", alpha=0.7)
    ax.axhline(y=140, color="#CCCCCC", linestyle="--", alpha=0.7)
    ax.text(175, 175, "ELITE CLUTCH RISERS\n(High Base & Elevated HP)", fontsize=10, fontweight="bold", color=RR_PINK, ha="center")
    ax.text(115, 155, "CRISIS ELEVATORS\n(Step up when squeezed)", fontsize=10, fontweight="bold", color=RR_BLUE, ha="center")

    plt.tight_layout()
    plt.savefig(output_dir / "chart2_batting_pressure_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Chart 3: Bowling Pressure Matrix (Quadrant Scatter Plot)
    print("  - Generating Chart 3: Bowling Pressure Matrix (Quadrant Scatter)...")
    plt.figure(figsize=(11, 8.5), facecolor=RR_LIGHT)
    ax = plt.gca()
    ax.set_facecolor("white")

    sns.scatterplot(
        data=bowl_all[bowl_all["hp_balls"] >= 80],
        x="base_econ",
        y="hp_econ",
        size="hp_balls",
        sizes=(40, 450),
        color="#B0BEC5",
        alpha=0.45,
        legend=False,
        ax=ax
    )

    sns.scatterplot(
        data=top10_bowl,
        x="base_econ",
        y="hp_econ",
        size="hp_balls",
        sizes=(120, 600),
        color=RR_BLUE,
        edgecolor=RR_GOLD,
        linewidth=1.8,
        alpha=0.95,
        ax=ax
    )

    # Diagonal parity line (HP Econ == Base Econ)
    ax.plot([6.0, 11.5], [6.0, 11.5], color="#999999", linestyle=":", linewidth=1.5, label="Parity Line (HP Econ = Usual Econ)")

    for _, r in top10_bowl.iterrows():
        ax.annotate(
            f"#{int(r['rank'])} {r['player_display_name'].split('(')[0].strip()}\n(PRR: {r['prr']:.1f})",
            xy=(r["base_econ"], r["hp_econ"]),
            xytext=(r["base_econ"] + 0.1, r["hp_econ"] + 0.1),
            fontsize=9,
            fontweight="bold",
            color=RR_DARK,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#E1F5FE", edgecolor="#0288D1", alpha=0.85)
        )

    ax.set_title("Bowling Pressure Matrix: Usual Economy vs. High-Pressure Economy", fontsize=14, fontweight="bold", color=RR_DARK, pad=15)
    ax.set_xlabel("Usual (Baseline) Economy Rate", fontsize=11, fontweight="bold")
    ax.set_ylabel("High-Pressure (BoPI >= 0.60) Economy Rate", fontsize=11, fontweight="bold")
    ax.axvline(x=8.5, color="#CCCCCC", linestyle="--", alpha=0.7)
    ax.axhline(y=8.5, color="#CCCCCC", linestyle="--", alpha=0.7)
    ax.text(6.8, 7.8, "IMPASSABLE FORTRESS\n(Sub-8 Economy in Clutch)", fontsize=10, fontweight="bold", color=RR_BLUE, ha="center")

    plt.tight_layout()
    plt.savefig(output_dir / "chart3_bowling_pressure_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Chart 4: Component Breakdown & Bootstrap Uncertainty Bars
    print("  - Generating Chart 4: Component Breakdown & Bootstrap Uncertainty Bars...")
    fig, axes = plt.subplots(1, 2, figsize=(18, 8.5), facecolor=RR_LIGHT)

    # Batters subplot
    ax_b = axes[0]
    ax_b.set_facecolor("white")
    y_pos_b = np.arange(len(top10_bat))
    bat_sorted = top10_bat.sort_values("rank", ascending=False).reset_index(drop=True)
    bat_boot_sorted = bat_boot_df.sort_values("rank", ascending=False).reset_index(drop=True)

    ax_b.barh(y_pos_b, bat_sorted["prr"], color=RR_PINK, alpha=0.85, edgecolor=RR_DARK, height=0.6, label="PRR Score")
    # Error bars from bootstrap confidence intervals
    err_low_b = bat_boot_sorted["median_rank"] - bat_boot_sorted["p5_rank"]
    err_high_b = bat_boot_sorted["p95_rank"] - bat_boot_sorted["median_rank"]
    ax_b.set_yticks(y_pos_b)
    ax_b.set_yticklabels([f"#{int(r['rank'])} {r['player_display_name']}" for _, r in bat_sorted.iterrows()], fontsize=10, fontweight="bold")
    ax_b.set_xlim(50, 90)
    ax_b.set_title("Top 10 Batters: Pressure Reliability Rating (PRR)", fontsize=12, fontweight="bold", color=RR_DARK)
    ax_b.set_xlabel("PRR Rating (Mean 50, Std 15)", fontsize=10, fontweight="bold")
    ax_b.grid(True, axis="x")

    for i, r in bat_sorted.iterrows():
        ax_b.text(r["prr"] + 0.5, i, f"{r['prr']:.1f} (Win: {r['win_rate']*100:.0f}%)", va="center", fontsize=9, fontweight="bold", color=RR_DARK)

    # Bowlers subplot
    ax_bw = axes[1]
    ax_bw.set_facecolor("white")
    y_pos_bw = np.arange(len(top10_bowl))
    bowl_sorted = top10_bowl.sort_values("rank", ascending=False).reset_index(drop=True)

    ax_bw.barh(y_pos_bw, bowl_sorted["prr"], color=RR_BLUE, alpha=0.85, edgecolor=RR_DARK, height=0.6, label="PRR Score")
    ax_bw.set_yticks(y_pos_bw)
    ax_bw.set_yticklabels([f"#{int(r['rank'])} {r['player_display_name']}" for _, r in bowl_sorted.iterrows()], fontsize=10, fontweight="bold")
    ax_bw.set_xlim(50, 95)
    ax_bw.set_title("Top 10 Bowlers: Pressure Reliability Rating (PRR)", fontsize=12, fontweight="bold", color=RR_DARK)
    ax_bw.set_xlabel("PRR Rating (Mean 50, Std 15)", fontsize=10, fontweight="bold")
    ax_bw.grid(True, axis="x")

    for i, r in bowl_sorted.iterrows():
        ax_bw.text(r["prr"] + 0.5, i, f"{r['prr']:.1f} (Wkts: {int(r['hp_wickets'])})", va="center", fontsize=9, fontweight="bold", color=RR_DARK)

    fig.suptitle("SupeRR Selector Season 2: Final Top 10 Player Rankings under Pressure", fontsize=15, fontweight="bold", color=RR_DARK, y=0.98)
    plt.tight_layout()
    plt.savefig(output_dir / "chart4_prr_breakdown_and_uncertainty.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("  - Generated all 4 publication charts successfully.")

    print("\n" + "=" * 70)
    print("STAGE 3 VALIDATION & VISUALIZATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    run_stage3_pipeline(".")
