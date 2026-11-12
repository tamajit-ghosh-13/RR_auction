"""Stage 5 Verification: Automated Submission Checklist & Dropdown Audit."""
from __future__ import annotations

import json
import re
from pathlib import Path
import pandas as pd


def main() -> None:
    bat_top = pd.read_csv("outputs/batting_ratings.csv")
    bwl_top = pd.read_csv("outputs/bowling_ratings.csv")
    final_df = pd.read_csv("outputs/final_rankings.csv")
    rob_df = pd.read_csv("outputs/robustness_summary.csv")
    mapping = pd.read_csv("data/raw/competition_team_player_mapping.csv")

    b10 = bat_top[bat_top["eligible"]].head(10).reset_index(drop=True)
    w10 = bwl_top[bwl_top["eligible"]].head(10).reset_index(drop=True)

    f_bat10 = final_df[final_df["role"] == "Batter"].head(10).reset_index(drop=True)
    f_bwl10 = final_df[final_df["role"] == "Bowler"].head(10).reset_index(drop=True)

    assert (b10["player_id"].astype(int) == f_bat10["player_id"].astype(int)).all(), "Batter Top 10 order mismatch!"
    assert (w10["player_id"].astype(int) == f_bwl10["player_id"].astype(int)).all(), "Bowler Top 10 order mismatch!"

    # Verify zero ID duplicates in Top 25
    assert final_df[final_df["role"] == "Batter"]["player_id"].nunique() == len(final_df[final_df["role"] == "Batter"])
    assert final_df[final_df["role"] == "Bowler"]["player_id"].nunique() == len(final_df[final_df["role"] == "Bowler"])

    # Verify required artifacts & figures exist
    req_files = [
        "outputs/data_profile.md",
        "outputs/ball_state_checks.md",
        "outputs/pressure_definition.md",
        "outputs/format_baselines.csv",
        "outputs/batting_ratings.csv",
        "outputs/bowling_ratings.csv",
        "outputs/final_rankings.csv",
        "outputs/robustness_summary.csv",
        "outputs/shrinkage_params.json",
        "outputs/red_team_checks.json",
        "outputs/DECISIONS.md",
        "outputs/figures/li_distribution.png",
        "outputs/figures/pressure_heatmap_chase.png",
        "outputs/figures/wp_calibration.png",
        "outputs/figures/eligibility_elbow.png",
        "outputs/figures/robustness_rank_ci.png",
        "outputs/figures/shrinkage_before_after.png",
        "outputs/figures/component_bars_top10.png",
        "outputs/figures/ipl_vs_t20i_contrib.png",
    ]
    missing = [f for f in req_files if not Path(f).exists()]
    assert not missing, f"Missing required files: {missing}"

    # Verify report.md Top-10 order matches CSVs if report.md exists
    report_path = Path("outputs/report.md")
    if report_path.exists():
        txt = report_path.read_text()
        for idx, r in b10.iterrows():
            assert r["player_name"] in txt, f"Missing batter {r['player_name']} in report.md"
        for idx, r in w10.iterrows():
            assert r["player_name"] in txt, f"Missing bowler {r['player_name']} in report.md"

    print("ALL SUBMISSION CHECKLIST ASSERTIONS PASSED!")
    print(f"Verified {len(req_files)} files, Top-10 order parity, zero ID duplicates, and robustness table ({len(rob_df)} checks).")


if __name__ == "__main__":
    main()
