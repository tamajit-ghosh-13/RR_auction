#!/usr/bin/env python3
"""
build_ball_state.py — turn the raw SupeRR ball_by_ball.csv into a delivery-level
match-state table (one row per delivery) that every other skill/agent consumes.

Usage:
    python scripts/build_ball_state.py --data data/raw --out data/interim/ball_state.csv.gz [--bye-runs 1]

Design notes (all verified against the supplied data pack):
  * `runs` is runs OFF THE BAT only. wides/byes/leg-byes carry runs == 0.
  * `extras1_runs` is an extras-TYPE CODE, not runs (6=none, 2=wide, 3=legbye,
    1=no-ball/"Overstep", 4=bye, 5=other, 7=penalty). Never sum it.
  * bye / leg-bye runs are NOT recorded anywhere -> team totals are slightly
    under-counted. We add `--bye-runs` per bye/leg-bye delivery as an ESTIMATE.
  * wide and no-ball each add 1 penalty run; `extras_2_runs` (rare) adds extra runs.
  * over_ball_num / innings_ball_num count ALL deliveries (wides/no-balls too),
    so legal-ball position must be rebuilt.
  * Super overs (innings 3,4) are excluded from the state table.
"""
import argparse, os, re
import numpy as np, pandas as pd

BALLS_PER_INNINGS = 120

def build(data_dir: str, bye_runs: float = 1.0) -> pd.DataFrame:
    b = pd.read_csv(os.path.join(data_dir, "ball_by_ball.csv"), low_memory=False)
    m = pd.read_csv(os.path.join(data_dir, "matches.csv"))
    c = pd.read_csv(os.path.join(data_dir, "competitions.csv"))

    b = b[b.innings.isin([1, 2])].copy()
    b = b.sort_values(["match_id", "innings", "innings_ball_num"]).reset_index(drop=True)

    et = b["extras_type"].fillna("none").str.lower()
    b["is_wide"] = (et == "wide").astype(int)
    b["is_noball"] = (et == "overstep").astype(int)
    b["is_bye"] = et.isin(["byes", "legbyes"]).astype(int)
    b["is_legal"] = ((b.is_wide == 0) & (b.is_noball == 0)).astype(int)   # 'other' treated as legal (flag!)

    # team runs on this delivery (estimated for byes/leg-byes)
    b["team_runs"] = b.runs + b.is_wide + b.is_noball + b.extras_2_runs + bye_runs * b.is_bye

    # bowler-charged runs: bat runs + wides + no-balls (byes/leg-byes NOT charged to bowler)
    b["bowler_runs"] = b.runs + b.is_wide + b.is_noball + b.extras_2_runs

    # wicket credit
    dt = b["dismissal_type"].fillna("").str.lower()
    b["is_wkt_team"] = b.is_wicket.astype(int)                                   # team loses a wicket
    b["is_wkt_bowler"] = (b.is_wicket & ~dt.isin(["runout", "retire out",
                          "obstracting the field", "obstructing the field"])).astype(int)

    g = b.groupby(["match_id", "innings"], sort=False)
    b["cum_runs_after"] = g.team_runs.cumsum()
    b["cum_wkts_after"] = g.is_wkt_team.cumsum()
    b["legal_after"] = g.is_legal.cumsum()
    # state BEFORE the delivery
    b["runs_before"] = b.cum_runs_after - b.team_runs
    b["wkts_before"] = b.cum_wkts_after - b.is_wkt_team
    b["legal_before"] = b.legal_after - b.is_legal
    b["balls_left"] = (BALLS_PER_INNINGS - b.legal_before).clip(lower=0)
    b["wkts_in_hand"] = 10 - b.wkts_before
    b["over_idx"] = b.overid                                   # 1..20 (1-indexed)
    b["phase"] = np.select([b.overid <= 6, b.overid <= 15], ["powerplay", "middle"], "death")
    b["crr"] = np.where(b.legal_before > 0, 6 * b.runs_before / b.legal_before.replace(0, np.nan), np.nan)

    # innings totals + chase target
    tot = b.groupby(["match_id", "innings"]).team_runs.sum().unstack().rename(columns={1: "inn1_total", 2: "inn2_total"})
    b = b.merge(tot, left_on="match_id", right_index=True, how="left")
    mm = m.merge(c[["comp_id", "comp_name", "match_format", "season"]], on="comp_id", how="left")
    keep = ["match_id", "comp_id", "comp_name", "match_format", "season", "match_date", "stage", "knock_out",
            "venue_id", "venue_country", "win_team_id", "revised_target", "first_inn_revised_overs",
            "second_inn_revised_overs", "toss_win_team_id", "toss_opted", "result"]
    b = b.merge(mm[keep], on="match_id", how="left")

    b["batting_won"] = (b.batting_team_id == b.win_team_id).astype(float)
    b.loc[b.win_team_id.isna(), "batting_won"] = np.nan          # tie / no result
    chase = b.innings == 2
    dls = b.revised_target.notna()
    b["target"] = np.where(chase, np.where(dls, b.revised_target, b.inn1_total + 1), np.nan)
    # NOTE: *_revised_overs columns are stored in BALLS (min 30, max 114), not overs.
    balls2 = np.where(b.second_inn_revised_overs.notna(), b.second_inn_revised_overs, BALLS_PER_INNINGS)
    b["balls_in_innings"] = np.where(chase, balls2.astype(float), BALLS_PER_INNINGS)
    # Repair: if the chasing side WON, its true target cannot exceed its own final total.
    # (Reconstructed totals are noisy because bye/leg-bye runs are unrecorded.)
    chaser_won = chase & (b.batting_won == 1) & ~dls
    b["target_raw"] = b["target"]
    b["target"] = np.where(chaser_won, np.minimum(b.target, b.inn2_total), b.target)
    b["target_repaired"] = (chase & (b.target != b.target_raw)).astype(int)
    b["balls_left"] = np.where(chase, (b.balls_in_innings - b.legal_before).clip(lower=0), b.balls_left)
    b["runs_needed"] = b.target - b.runs_before
    b["rrr"] = np.where(chase & (b.balls_left > 0), 6 * b.runs_needed / b.balls_left.replace(0, np.nan), np.nan)
    b["rrr_minus_crr"] = b.rrr - b.crr
    b["dls_flag"] = (dls | b.first_inn_revised_overs.notna()).astype(int)

    b["match_date"] = pd.to_datetime(b.match_date)
    return b

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw")
    ap.add_argument("--out", default="data/interim/ball_state.csv.gz")
    ap.add_argument("--bye-runs", type=float, default=1.0)
    a = ap.parse_args()
    df = build(a.data, a.bye_runs)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    df.to_csv(a.out, index=False)
    print(f"wrote {len(df):,} rows, {df.match_id.nunique()} matches -> {a.out}")
