"""Stage 5: Publication-Quality Report Figures for Methodology Report."""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"figure.dpi": 150, "axes.spines.top": False, "axes.spines.right": False})


def main() -> None:
    bat = pd.read_csv("outputs/batting_ratings.csv")
    bwl = pd.read_csv("outputs/bowling_ratings.csv")
    fig_dir = Path("outputs/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Shrinkage before vs after (Batters & Bowlers)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    b_sub = bat[bat["hp_bf"] >= 30].copy()
    sc1 = axes[0].scatter(b_sub["hp_rae100_raw"], b_sub["hp_rae100_eb"], c=b_sub["hp_bf"].clip(upper=500), cmap="viridis", alpha=0.75, s=28)
    lims = [min(b_sub["hp_rae100_raw"].min(), -80), max(b_sub["hp_rae100_raw"].max(), 80)]
    axes[0].plot(lims, lims, "r--", lw=1, label="No shrinkage (y=x)")
    top5b = bat[bat["eligible"]].head(5)
    for _, r in top5b.iterrows():
        axes[0].annotate(r["player_name"], (r["hp_rae100_raw"], r["hp_rae100_eb"]), fontsize=7.5, xytext=(4, 2), textcoords="offset points")
    axes[0].set_title("Batters: Raw vs EB-Shrunk HP RAE100 (hp_bf >= 30)")
    axes[0].set_xlabel("Raw HP RAE100")
    axes[0].set_ylabel("EB-Shrunk HP RAE100")
    fig.colorbar(sc1, ax=axes[0], label="HP Balls Faced")
    axes[0].legend(fontsize=8)

    w_sub = bwl[bwl["hp_legal"] >= 30].copy()
    sc2 = axes[1].scatter(w_sub["hp_total_rsae24_raw"], w_sub["hp_total_rsae24_eb"], c=w_sub["hp_legal"].clip(upper=500), cmap="plasma", alpha=0.75, s=28)
    lims2 = [min(w_sub["hp_total_rsae24_raw"].min(), -20), max(w_sub["hp_total_rsae24_raw"].max(), 25)]
    axes[1].plot(lims2, lims2, "r--", lw=1, label="No shrinkage (y=x)")
    top5w = bwl[bwl["eligible"]].head(5)
    for _, r in top5w.iterrows():
        axes[1].annotate(r["player_name"], (r["hp_total_rsae24_raw"], r["hp_total_rsae24_eb"]), fontsize=7.5, xytext=(4, 2), textcoords="offset points")
    axes[1].set_title("Bowlers: Raw vs EB-Shrunk Total RSAE24 (hp_legal >= 30)")
    axes[1].set_xlabel("Raw HP Total RSAE24")
    axes[1].set_ylabel("EB-Shrunk HP Total RSAE24")
    fig.colorbar(sc2, ax=axes[1], label="HP Legal Balls")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "shrinkage_before_after.png", bbox_inches="tight")
    plt.close(fig)

    # 2. Component contributions for Top 10 Batters & Top 10 Bowlers
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    tb10 = bat[bat["eligible"]].head(10).iloc[::-1]
    y = np.arange(len(tb10))
    c1 = 0.50 * tb10["z_rae100"]
    c2 = 0.15 * tb10["z_delta"]
    c3 = 0.25 * tb10["z_consistency"]
    c4 = 0.10 * tb10["z_wpa100"]
    axes[0].barh(y - 0.18, c1, height=0.22, label="50% EB RAE100", color="#2b6cb0")
    axes[0].barh(y, c3, height=0.22, label="25% Consistency", color="#2f855a")
    axes[0].barh(y + 0.18, c2 + c4, height=0.22, label="15% Delta + 10% WPA", color="#dd6b20")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([f"#{int(r.rank_eb)} {r.player_name}" for _, r in tb10.iterrows()], fontsize=8.5)
    axes[0].set_xlabel("Weighted Z-Score Contribution")
    axes[0].set_title("Top 10 Batters — Composite Component Breakdown")
    axes[0].axvline(0, color="k", lw=0.7)
    axes[0].legend(fontsize=8)

    tw10 = bwl[bwl["eligible"]].head(10).iloc[::-1]
    y2 = np.arange(len(tw10))
    w1 = 0.50 * tw10["z_rsae24"]
    w2 = 0.15 * tw10["z_delta"]
    w3 = 0.25 * tw10["z_consistency"]
    w4 = 0.10 * tw10["z_disc_wpa"]
    axes[1].barh(y2 - 0.18, w1, height=0.22, label="50% EB Total RSAE24", color="#2b6cb0")
    axes[1].barh(y2, w3, height=0.22, label="25% Consistency", color="#2f855a")
    axes[1].barh(y2 + 0.18, w2 + w4, height=0.22, label="15% Delta + 10% Disc/WPA", color="#dd6b20")
    axes[1].set_yticks(y2)
    axes[1].set_yticklabels([f"#{int(r.rank_eb)} {r.player_name}" for _, r in tw10.iterrows()], fontsize=8.5)
    axes[1].set_xlabel("Weighted Z-Score Contribution")
    axes[1].set_title("Top 10 Bowlers — Composite Component Breakdown")
    axes[1].axvline(0, color="k", lw=0.7)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "component_bars_top10.png", bbox_inches="tight")
    plt.close(fig)

    # 3. IPL vs T20I contribution share for Top 10
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    for t10, ipl_c, t20_c, ax, title in [
        (tb10, "hp_ipl_bf", "hp_t20i_bf", axes[0], "Top 10 Batters — HP Balls by Format"),
        (tw10, "hp_ipl_legal", "hp_t20i_legal", axes[1], "Top 10 Bowlers — HP Legal Balls by Format"),
    ]:
        y = np.arange(len(t10))
        ax.barh(y, t10[ipl_c], label="IPL", color="#e53e3e", alpha=0.85)
        ax.barh(y, t10[t20_c], left=t10[ipl_c], label="T20I", color="#3182ce", alpha=0.85)
        ax.set_yticks(y)
        ax.set_yticklabels([f"#{int(r.rank_eb)} {r.player_name}" for _, r in t10.iterrows()], fontsize=8.5)
        ax.set_xlabel("High-Pressure Balls")
        ax.set_title(title)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "ipl_vs_t20i_contrib.png", bbox_inches="tight")
    plt.close(fig)
    print("Saved Stage 5 figures (shrinkage_before_after, component_bars_top10, ipl_vs_t20i_contrib).")


if __name__ == "__main__":
    main()
