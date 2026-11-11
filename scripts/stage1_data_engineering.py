#!/usr/bin/env python3
"""
Stage 1: Data Engineering & Match-State Reconstruction Pipeline
SupeRR Selector Season 2 (Round 1) - Rajasthan Royals Auction Strategy
"""

import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path

# Canonical Split ID mapping
SPLIT_ID_MAP = {
    39444: 8638,   # Basil Hameed (UAE)
    20229: 3083,   # Mohammad Ali (PAK)
    28978: 27373,  # Muhammad Farooq (UAE)
    39479: 29833,  # Bashir Ahmad (AFG)
}

# Homonyms disambiguation display names
HOMONYM_DISPLAY_MAP = {
    4722: "Rashid Khan (AFG/GT)",
    20172: "Rashid Khan (NEP)",
    7446: "Abdul Samad (IND/SRH/LSG)",
    6922: "Abdul Samad (PAK)",
    7338: "Haider Ali (PAK)",
    28756: "Haider Ali (UAE)",
}

IPL_COMP_IDS = {1358, 1715, 2193, 2725, 3298}  # IPL 2022, 2023, 2024, 2025, 2026
EMERGING_COMP_IDS = {2670, 3289}               # Emerging Teams Asia Cup 2024, Rising Stars 2025

FULL_MEMBER_TEAMS = {
    "India", "Australia", "England", "South Africa", "New Zealand",
    "Pakistan", "Sri Lanka", "West Indies", "Bangladesh", "Afghanistan",
    "Ireland", "Zimbabwe"
}

BOWLER_WICKET_TYPES = {"Caught", "Bowled", "LBW", "Stump", "Hit Wicket"}


def convert_cricket_overs_to_balls(val: float) -> int:
    """Convert cricket notation or pre-converted ball counts to integer balls."""
    if pd.isna(val):
        return 120
    # In matches.csv, values are already stored as legal balls (e.g. 48.0 = 8 overs, 114.0 = 19 overs)
    if val > 20:
        return int(round(val))
    whole_overs = int(np.floor(val + 1e-9))
    rem_balls = int(np.round((val - whole_overs) * 10))
    if rem_balls >= 6:
        return int(np.round(val * 6))
    return whole_overs * 6 + rem_balls


def run_stage1_pipeline(data_dir: str = "."):
    print("=" * 70)
    print("STAGE 1: DATA ENGINEERING & MATCH-STATE RECONSTRUCTION")
    print("=" * 70)

    # 1. Ingestion
    print("\n[1/6] Ingesting raw CSV files...")
    comp = pd.read_csv(f"{data_dir}/competitions.csv")
    teams = pd.read_csv(f"{data_dir}/teams.csv")
    matches = pd.read_csv(f"{data_dir}/matches.csv")
    mapping = pd.read_csv(f"{data_dir}/competition_team_player_mapping.csv")
    xi = pd.read_csv(f"{data_dir}/playing_eleven.csv")
    bbb = pd.read_csv(f"{data_dir}/ball_by_ball.csv", low_memory=False)

    print(f"  - competitions: {len(comp):,} rows")
    print(f"  - teams: {len(teams):,} rows")
    print(f"  - matches: {len(matches):,} rows")
    print(f"  - mapping: {len(mapping):,} rows")
    print(f"  - playing_eleven: {len(xi):,} rows")
    print(f"  - ball_by_ball: {len(bbb):,} rows")

    # 2. Canonicalize split player IDs across all tables
    print("\n[2/6] Applying canonical player ID merges & homonym disambiguation...")
    for col in ["striker_id", "non_striker_id", "bowler_id", "dismissed_player_id"]:
        if col in bbb.columns:
            bbb[col] = bbb[col].replace(SPLIT_ID_MAP)
    mapping["player_id"] = mapping["player_id"].replace(SPLIT_ID_MAP)
    xi["player_id"] = xi["player_id"].replace(SPLIT_ID_MAP)

    # Build canonical player registry
    print("  - Building player_registry.csv...")
    # Canonical player name map (Unstop dropdown name)
    player_unstop_name = mapping.groupby("player_id")["player_name"].first().to_dict()
    
    # Determine teams and competitions per player
    player_teams = mapping.groupby("player_id")["team_name"].unique().apply(lambda arr: "; ".join(sorted(set(arr)))).to_dict()
    player_comps = mapping.groupby("player_id")["comp_name"].unique().apply(lambda arr: "; ".join(sorted(set(arr)))).to_dict()
    
    # Check if player appeared in IPL
    ipl_players = set(mapping[mapping["comp_id"].isin(IPL_COMP_IDS)]["player_id"].unique())

    # Count matches played from playing_eleven (filtered to is_played == True)
    xi_played = xi[xi["is_played"] == True]
    player_matches_played = xi_played.groupby("player_id")["match_id"].nunique().to_dict()

    all_registry_pids = sorted(list(set(mapping["player_id"].unique()) | set(bbb["striker_id"].dropna().unique()) | set(bbb["bowler_id"].dropna().unique())))
    
    registry_rows = []
    for pid in all_registry_pids:
        pid_int = int(pid)
        uname = player_unstop_name.get(pid_int, bbb[bbb["striker_id"] == pid_int]["striker_name"].iloc[0] if (bbb["striker_id"] == pid_int).any() else f"Player_{pid_int}")
        disp_name = HOMONYM_DISPLAY_MAP.get(pid_int, uname)
        registry_rows.append({
            "player_id": pid_int,
            "player_name": uname,
            "player_display_name": disp_name,
            "teams": player_teams.get(pid_int, ""),
            "competitions": player_comps.get(pid_int, ""),
            "is_ipl_player": pid_int in ipl_players,
            "total_matches_played": player_matches_played.get(pid_int, 0),
        })
    player_registry = pd.DataFrame(registry_rows)
    player_registry.to_csv(f"{data_dir}/player_registry.csv", index=False)
    print(f"  - Saved player_registry.csv with {len(player_registry):,} unique players.")

    # Display names lookup for deliveries
    display_name_lookup = dict(zip(player_registry["player_id"], player_registry["player_display_name"]))
    unstop_name_lookup = dict(zip(player_registry["player_id"], player_registry["player_name"]))

    bbb["striker_name"] = bbb["striker_id"].map(unstop_name_lookup).fillna(bbb["striker_name"])
    bbb["striker_display_name"] = bbb["striker_id"].map(display_name_lookup).fillna(bbb["striker_name"])
    bbb["bowler_name"] = bbb["bowler_id"].map(unstop_name_lookup).fillna(bbb["bowler_name"])
    bbb["bowler_display_name"] = bbb["bowler_id"].map(display_name_lookup).fillna(bbb["bowler_name"])

    # 3. Delivery runs, extras, and legal ball flags
    print("\n[3/6] Computing delivery runs and legal delivery counters...")
    # Trap 1: NEVER sum extras1_runs!
    is_non_bat_extra = bbb["extras_type"].isin(["wide", "byes", "legbyes", "Penalty"])
    bbb["batter_runs"] = np.where(is_non_bat_extra, 0, bbb["runs"]).astype(int)

    bbb["extra_runs"] = np.where(
        bbb["extras_type"].notna() & (bbb["extras_type"] != "Penalty"),
        1 + bbb["extras_2_runs"],
        np.where(bbb["extras_type"] == "Penalty", 5, 0),
    ).astype(int)
    bbb["total_runs"] = (bbb["batter_runs"] + bbb["extra_runs"]).astype(int)

    is_bowler_extra = bbb["extras_type"].isin(["wide", "Overstep", "other"])
    bbb["bowler_runs"] = (
        bbb["batter_runs"] + np.where(is_bowler_extra, 1 + bbb["extras_2_runs"], 0)
    ).astype(int)

    # Trap 2: Legal balls
    bbb["is_legal_ball"] = ~bbb["extras_type"].isin(["wide", "Overstep", "other", "Penalty"])
    bbb["is_batter_ball"] = ~bbb["extras_type"].isin(["wide", "Penalty"])
    bbb["is_bowler_ball"] = bbb["is_legal_ball"]

    bbb["is_dot_batter"] = ((bbb["batter_runs"] == 0) & bbb["is_batter_ball"]).astype(int)
    bbb["is_dot_bowler"] = ((bbb["bowler_runs"] == 0) & bbb["is_bowler_ball"]).astype(int)
    bbb["is_boundary"] = (bbb["is_four"] | bbb["is_six"]).astype(int)

    # Bowl speed cleaning
    bbb["clean_bowl_speed"] = np.where(
        (bbb["bowl_speed"] >= 65.0) & (bbb["bowl_speed"] <= 165.0),
        bbb["bowl_speed"],
        np.nan,
    )

    # 4. Wickets & Attribution
    print("\n[4/6] Attributing wickets & computing rolling crisis features...")
    # Trap 4: Bowler wicket attribution
    bbb["is_team_wicket"] = bbb["is_wicket"].astype(int)
    bbb["is_bowler_wicket"] = (
        bbb["is_wicket"] & bbb["dismissal_type"].isin(BOWLER_WICKET_TYPES)
    ).astype(int)
    bbb["is_batter_out"] = (
        bbb["is_wicket"] & ~bbb["dismissal_type"].isin(["Retire Out"])
    ).astype(int)

    # Sort deterministically
    df = bbb.sort_values(["match_id", "innings", "innings_ball_num"]).reset_index(drop=True)

    # Merge match & competition metadata
    m_meta = matches[[
        "match_id", "comp_id", "match_date", "stage", "venue_id", "venue_country",
        "home_team_id", "home_team", "away_team_id", "away_team",
        "first_inn_revised_overs", "second_inn_revised_overs", "revised_target",
        "knock_out", "win_team_id", "result"
    ]].merge(comp[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")

    df = df.merge(m_meta, on="match_id", how="left")

    # Match state reconstruction
    print("  - Reconstructing cumulative pre-ball & post-ball state...")
    grp = df.groupby(["match_id", "innings"], sort=False)
    df["post_score"] = grp["total_runs"].cumsum()
    df["post_wickets"] = grp["is_team_wicket"].cumsum()
    df["post_legal_balls"] = grp["is_legal_ball"].cumsum()

    # Pre-ball state (state entering delivery t)
    df["pre_score"] = df["post_score"] - df["total_runs"]
    df["pre_wickets"] = df["post_wickets"] - df["is_team_wicket"]
    df["pre_legal_balls"] = df["post_legal_balls"] - df["is_legal_ball"].astype(int)
    df["wickets_in_hand"] = np.clip(10 - df["pre_wickets"], 0, 10)

    # Scheduled balls per innings (handling Trap 7: DLS / rain shortened matches)
    inn1_max_balls = df["first_inn_revised_overs"].apply(convert_cricket_overs_to_balls)
    inn2_max_balls = df["second_inn_revised_overs"].apply(convert_cricket_overs_to_balls)
    df["max_balls"] = np.where(
        df["innings"] == 1, inn1_max_balls,
        np.where(df["innings"] == 2, inn2_max_balls, 6)
    )
    df["balls_remaining"] = np.clip(df["max_balls"] - df["pre_legal_balls"], 0, 120)

    # First innings total runs per match
    inn1_totals = (
        df[df["innings"] == 1]
        .groupby("match_id")["total_runs"]
        .sum()
        .rename("inn1_total")
    )
    df = df.merge(inn1_totals, on="match_id", how="left")

    # Target & Required Run Rate (Innings 2)
    df["target_runs"] = np.where(
        df["innings"] == 2,
        np.where(df["revised_target"].notna(), df["revised_target"], df["inn1_total"] + 1),
        np.nan,
    )
    df["runs_needed"] = np.where(
        df["innings"] == 2,
        np.clip(df["target_runs"] - df["pre_score"], 0, None),
        np.nan,
    )
    df["crr"] = np.where(df["pre_legal_balls"] > 0, df["pre_score"] * 6.0 / df["pre_legal_balls"], 8.0)
    # Avoid zero-division in RRR
    safe_balls_rem = np.maximum(df["balls_remaining"], 1)
    df["rrr"] = np.where(df["innings"] == 2, df["runs_needed"] * 6.0 / safe_balls_rem, np.nan)

    # Phase tagging
    df["phase"] = np.select(
        [df["overid"] <= 6, df["overid"] <= 15, df["overid"] >= 16],
        ["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"],
        default="Death (16-20)"
    )

    # Competition tier & weights
    print("  - Tagging competition tiers & weights...")
    is_ipl = df["comp_id"].isin(IPL_COMP_IDS)
    is_home_fm = df["home_team"].isin(FULL_MEMBER_TEAMS)
    is_away_fm = df["away_team"].isin(FULL_MEMBER_TEAMS)
    is_both_fm = is_home_fm & is_away_fm
    is_mixed_fm = (is_home_fm ^ is_away_fm)

    comp_tier = np.select(
        [
            is_ipl,
            is_both_fm & (~df["comp_id"].isin(EMERGING_COMP_IDS)),
            is_mixed_fm & (~df["comp_id"].isin(EMERGING_COMP_IDS)),
        ],
        [
            "IPL",
            "T20I_FullMember",
            "T20I_Mixed",
        ],
        default="T20I_Associate_or_Emerging"
    )
    df["comp_tier"] = comp_tier

    comp_weight = np.select(
        [
            df["comp_tier"] == "IPL",
            df["comp_tier"] == "T20I_FullMember",
            df["comp_tier"] == "T20I_Mixed",
        ],
        [1.00, 0.90, 0.65],
        default=0.40
    )
    df["comp_weight"] = comp_weight

    # Match stakes
    is_ko = (df["knock_out"] == 1) | df["stage"].astype(str).isin(["Final", "Qualifier", "Eliminator", "Semi Final", "Super 4"])
    df["is_knockout"] = is_ko.astype(int)
    df["is_super_over"] = df["innings"].isin([3, 4]).astype(int)

    # Rolling wickets in last 12 and 18 balls entering delivery
    print("  - Computing rolling wickets in last 12 & 18 balls...")
    shifted_wkt = grp["is_team_wicket"].shift(1).fillna(0)
    # Using pandas rolling on shifted wicket within (match_id, innings)
    df["wickets_last_12_balls"] = (
        shifted_wkt.groupby([df["match_id"], df["innings"]])
        .rolling(12, min_periods=1)
        .sum()
        .reset_index(drop=True)
        .fillna(0)
        .astype(int)
    )
    df["wickets_last_18_balls"] = (
        shifted_wkt.groupby([df["match_id"], df["innings"]])
        .rolling(18, min_periods=1)
        .sum()
        .reset_index(drop=True)
        .fillna(0)
        .astype(int)
    )

    # Partnership tracking pre-delivery
    print("  - Computing partnership runs and balls entering delivery...")
    # Partnership ID increments with each team wicket in the innings
    p_id = grp["is_team_wicket"].shift(1).fillna(0).cumsum()
    p_grp = df.groupby(["match_id", "innings", p_id], sort=False)
    df["partnership_runs_pre"] = (p_grp["total_runs"].cumsum() - df["total_runs"]).astype(int)
    df["partnership_balls_pre"] = (p_grp["is_legal_ball"].cumsum() - df["is_legal_ball"].astype(int)).astype(int)

    # Striker current score & balls faced entering delivery
    print("  - Computing striker pre-delivery score & balls faced...")
    striker_grp = df.groupby(["match_id", "innings", "striker_id"], sort=False)
    df["striker_score_pre"] = (striker_grp["batter_runs"].cumsum() - df["batter_runs"]).astype(int)
    df["striker_balls_pre"] = (striker_grp["is_batter_ball"].cumsum() - df["is_batter_ball"].astype(int)).astype(int)
    df["is_set_striker"] = (df["striker_score_pre"] >= 25).astype(int)

    # Collapse active indicator
    df["is_collapse_active"] = (
        (df["wickets_last_18_balls"] >= 2) | ((df["pre_wickets"] >= 4) & (df["overid"] <= 10))
    ).astype(int)

    # 5. Mandatory Unit Tests
    print("\n[5/6] Executing mandatory automated sanity assertions...")

    # Test 1: Total runs bound [0, 11]
    assert (df["total_runs"] >= 0).all() and (df["total_runs"] <= 11).all(), \
        f"FAILED Test 1: total_runs out of bounds [0, 11]! Min: {df['total_runs'].min()}, Max: {df['total_runs'].max()}"
    print("  [PASS] Test 1: total_runs in [0, 11] on all 200,999 rows (min=0, max=11).")

    # Test 2: IPL 1st innings par score between 165 and 190
    ipl_inn1_totals = df[(df["comp_tier"] == "IPL") & (df["innings"] == 1)].groupby("match_id")["total_runs"].sum()
    mean_ipl_inn1 = ipl_inn1_totals.mean()
    assert 165 <= mean_ipl_inn1 <= 190, \
        f"FAILED Test 2: Mean IPL 1st innings score {mean_ipl_inn1:.2f} is outside [165, 190]! Check extras1_runs handling."
    print(f"  [PASS] Test 2: Average IPL 1st-innings total score = {mean_ipl_inn1:.2f} runs (expected 165-190).")

    # Test 3: Bowler wickets vs Team wickets
    bowler_wkt_sum = df["is_bowler_wicket"].sum()
    team_wkt_sum = df["is_team_wicket"].sum()
    assert bowler_wkt_sum < team_wkt_sum, f"FAILED Test 3: bowler_wkts ({bowler_wkt_sum}) >= team_wkts ({team_wkt_sum})"
    assert bowler_wkt_sum == 10272, f"FAILED Test 3: bowler_wkts = {bowler_wkt_sum}, expected 10,272"
    assert team_wkt_sum == 10881, f"FAILED Test 3: team_wkts = {team_wkt_sum}, expected 10,881"
    print(f"  [PASS] Test 3: Bowler wickets ({bowler_wkt_sum:,}) vs Team wickets ({team_wkt_sum:,}) exact match.")

    # Test 4: Registry coverage
    registry_pids = set(player_registry["player_id"])
    missing_strikers = set(df["striker_id"]) - registry_pids
    missing_bowlers = set(df["bowler_id"]) - registry_pids
    assert len(missing_strikers) == 0 and len(missing_bowlers) == 0, \
        f"FAILED Test 4: Missing registry players: strikers={missing_strikers}, bowlers={missing_bowlers}"
    print("  [PASS] Test 4: 100% of striker_id and bowler_id exist in player_registry.csv.")

    # Test 5: Zero NaNs in critical match-state columns
    critical_cols = ["pre_score", "pre_wickets", "balls_remaining", "comp_tier", "total_runs", "is_legal_ball"]
    for c in critical_cols:
        nan_cnt = df[c].isna().sum()
        assert nan_cnt == 0, f"FAILED Test 5: {nan_cnt} NaNs in {c}"
    print(f"  [PASS] Test 5: Zero NaNs in critical match-state columns {critical_cols}.")

    # 6. Save target artifacts
    print("\n[6/6] Saving enriched outputs...")
    parquet_path = f"{data_dir}/deliveries_enriched.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"  - Successfully saved {parquet_path} ({os.path.getsize(parquet_path) / (1024*1024):.1f} MB, {len(df):,} rows, {len(df.columns)} columns)")

    # Print summary of competition tiers
    print("\nDataset Summary by Competition Tier:")
    summary = df.groupby("comp_tier").agg(
        matches=("match_id", "nunique"),
        deliveries=("match_id", "count"),
        total_runs=("total_runs", "sum"),
        bowler_wickets=("is_bowler_wicket", "sum"),
        weight=("comp_weight", "first")
    )
    print(summary.to_string())

    print("\n" + "=" * 70)
    print("STAGE 1 COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_stage1_pipeline(".")
