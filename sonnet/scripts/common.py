"""Shared domain constants and helper functions for the SupeRR Selector pipeline."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42

# Competition groupings verified from competitions.csv
IPL_COMP_IDS = {1358, 1715, 2193, 2725, 3298}
EMERGING_COMP_IDS = {2670, 3289}

# Opposition Strength-of-Schedule Tier Weights (Explicit User Specifications)
# IPL: Tier 1 (1.20x) RCB, GT, PBKS | Tier 2 (1.05x) CSK, MI, KKR, SRH | Tier 3 (0.90x) RR, DC, LSG
IPL_TIER_1_TEAMS = {5, 3508, 4}        # RCB, GT, PBKS
IPL_TIER_2_TEAMS = {1, 2, 8, 242}      # CSK, MI, KKR, SRH
IPL_TIER_3_TEAMS = {3, 7, 3509}        # RR, DC, LSG

# T20I: Tier 1 (1.25x) IND, AUS | Tier 2 (1.10x) ENG, SA, NZ | Tier 3 (0.95x) PAK, WI, SL, AFG | Tier 4 (0.75x) BAN, IRE, ZIM, Associates
T20I_TIER_1_TEAMS = {18, 20}           # IND, AUS
T20I_TIER_2_TEAMS = {22, 19, 17}       # ENG, SA, NZ
T20I_TIER_3_TEAMS = {25, 28, 27, 78}   # PAK, WI, SL, AFG
T20I_TIER_4_TEAMS = {21, 23, 72}       # BAN, IRE, ZIM

# Approved Marquee Rivalry Pairs (4 IPL Derbies + 7 T20I Derbies)
MARQUEE_RIVALRY_PAIRS = [
    {1, 2},    # MI vs CSK (El Clasico of IPL)
    {1, 5},    # CSK vs RCB (Southern Derby)
    {5, 8},    # RCB vs KKR (Original Rivalry)
    {4, 3},    # PBKS vs RR (Northern Thriller)
    {18, 25},  # IND vs PAK (The Mother of All Rivalries)
    {20, 22},  # AUS vs ENG (T20 Ashes)
    {18, 20},  # IND vs AUS (Modern Heavyweights)
    {20, 17},  # AUS vs NZ (Trans-Tasman Clash)
    {25, 78},  # PAK vs AFG (Asian Border Derby)
    {21, 27},  # BAN vs SL (Naagin Derby)
]


def get_team_tier_weight(team_id: int, fmt: str) -> float:
    """Return opposition quality weight based on verified team pedigree tiers."""
    tid = int(team_id)
    if fmt == "IPL":
        if tid in IPL_TIER_1_TEAMS:
            return 1.20
        elif tid in IPL_TIER_2_TEAMS:
            return 1.05
        elif tid in IPL_TIER_3_TEAMS:
            return 0.90
        return 1.00
    elif fmt == "T20I":
        if tid in T20I_TIER_1_TEAMS:
            return 1.25
        elif tid in T20I_TIER_2_TEAMS:
            return 1.10
        elif tid in T20I_TIER_3_TEAMS:
            return 0.95
        return 0.75  # Tier 4 & Associates
    return 1.00


def is_marquee_rivalry(team1_id: int, team2_id: int) -> bool:
    """Return True if matchup is one of the 11 verified marquee derbies."""
    s = {int(team1_id), int(team2_id)}
    return any(s == rp for rp in MARQUEE_RIVALRY_PAIRS)


# Duplicate player IDs representing the exact same cricketer across seasons/teams
SPLIT_PLAYER_ID_MAP = {
    39444: 8638,   # Basil Hameed
    20229: 3083,   # Mohammad Ali
    28978: 27373,  # Muhammad Farooq
    39479: 29833,  # Bashir Ahmad
}

BOWLER_WICKET_TYPES = {"caught", "bowled", "lbw", "stump", "hit wicket"}
NON_BOWLER_WICKET_TYPES = {
    "runout",
    "retire out",
    "obstracting the field",
    "obstructing the field",
}


def balls_faced(df: pd.DataFrame) -> pd.Series:
    """Boolean Series marking deliveries counted as a ball faced by the batter.

    Wides are excluded; no-balls (Overstep) and legal deliveries are counted.
    """
    if "is_wide" in df.columns:
        return ~df["is_wide"].astype(bool)
    ext = df["extras_type"].fillna("").astype(str).str.lower()
    return ext.ne("wide") & ext.ne("penalty")


def legal_balls(df: pd.DataFrame) -> pd.Series:
    """Boolean Series marking legal deliveries (consistent with build_ball_state.py)."""
    if "is_legal" in df.columns:
        return df["is_legal"].astype(bool)
    ext = df["extras_type"].fillna("").astype(str).str.lower()
    return ~ext.isin(["wide", "overstep", "penalty"])


def bowler_runs(df: pd.DataFrame) -> pd.Series:
    """Runs charged to the bowler on each delivery (bat + wide + no-ball + extras_2_runs)."""
    if "bowler_runs" in df.columns:
        return df["bowler_runs"].astype(float)
    ext = df["extras_type"].fillna("").astype(str).str.lower()
    is_w = ext.eq("wide").astype(float)
    is_nb = ext.eq("overstep").astype(float)
    return df["runs"].fillna(0).astype(float) + is_w + is_nb + df["extras_2_runs"].fillna(0).astype(float)


def batter_runs(df: pd.DataFrame) -> pd.Series:
    """Runs credited to the striker off the bat on each delivery."""
    ext = df["extras_type"].fillna("").astype(str).str.lower()
    non_bat = ext.isin(["wide", "byes", "legbyes", "penalty"])
    return pd.Series(
        np.where(non_bat, 0.0, df["runs"].fillna(0).astype(float)),
        index=df.index,
    )


def is_striker_dismissed(df: pd.DataFrame) -> pd.Series:
    """Boolean Series marking whether the striker (not non-striker) was dismissed."""
    return (df["is_wicket"].fillna(0).astype(int) == 1) & (
        df["dismissed_player_id"].fillna(-1).astype(np.int64)
        == df["striker_id"].fillna(-2).astype(np.int64)
    )


def is_any_dismissal_of_batter(df: pd.DataFrame) -> pd.Series:
    """Boolean Series marking any team wicket (used when attributing dismissals via dismissed_player_id)."""
    return (df["is_wicket"].fillna(0).astype(int) == 1) & df["dismissed_player_id"].notna()


def canon_player_ids(
    df: pd.DataFrame,
    cols: tuple[str, ...] = ("striker_id", "non_striker_id", "bowler_id", "dismissed_player_id"),
    merge_split_ids: bool = True,
) -> pd.DataFrame:
    """Canonicalize player IDs in place on a copy, optionally merging confirmed split IDs."""
    out = df.copy()
    if not merge_split_ids:
        return out
    for col in cols:
        if col in out.columns:
            out[col] = out[col].replace(SPLIT_PLAYER_ID_MAP)
    return out


def assign_format_bucket(df: pd.DataFrame) -> pd.Series:
    """Classify each row into 'IPL', 'T20I', or 'Emerging_T20'."""
    cid = df["comp_id"].astype(int)
    is_ipl = cid.isin(IPL_COMP_IDS)
    is_emerging = cid.isin(EMERGING_COMP_IDS)
    return pd.Series(
        np.where(is_ipl, "IPL", np.where(is_emerging, "Emerging_T20", "T20I")),
        index=df.index,
    )


def load_raw_tables(data_dir: str | Path = "data/raw") -> dict[str, pd.DataFrame]:
    """Load all six raw CSV tables into a dictionary."""
    d = Path(data_dir)
    return {
        "competitions": pd.read_csv(d / "competitions.csv"),
        "teams": pd.read_csv(d / "teams.csv"),
        "matches": pd.read_csv(d / "matches.csv"),
        "playing_eleven": pd.read_csv(d / "playing_eleven.csv"),
        "mapping": pd.read_csv(d / "competition_team_player_mapping.csv"),
        "ball_by_ball": pd.read_csv(d / "ball_by_ball.csv", low_memory=False),
    }


def load_ball_state(path: str | Path = "data/interim/ball_state.csv.gz") -> pd.DataFrame:
    """Load the engineered ball_state table."""
    return pd.read_csv(path, low_memory=False)
