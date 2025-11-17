"""
Reusable helper functions for Leo CM Cup rounds 1 & 2 analysis.
Pulled out of the original leoCMRoundVis notebook.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Debuffer classification mapping (edit as needed)

#  EDIT ME: Uma → Debuffer Type
DEBUFF_TYPE = {
    # Speed debuffers
    "Grass Wonder": "Speed",
    "Symboli Rudolf": "Speed",
    "Agnes Tachyon": "Speed",

    # Stamina debuffers
    "Nice Nature": "Stamina",
    "Mayano Top Gun (Wedding)": "Stamina",

    # Other debuffers
    "Air Groove": "Other",
    # Add more as needed...
}

# --- Function library ---

def normalize_role(x):
    if pd.isna(x): return np.nan
    s = str(x).strip().lower()
    if "debuffer" in s or "hybrid" in s:
        return "Debuffer"
    if "aoharu made ace" in s or "ace" in s:
        return "Ace"
    return "Other"

def normalize_style(x):
    if pd.isna(x): return np.nan
    s = str(x).strip().lower()
    if "front" in s: return "Front Runner"
    if "pace"  in s: return "Pace Chaser"
    if "late"  in s: return "Late Surger"
    if "end"   in s: return "End Closer"
    return "Unknown Style"

def has_debuffer(row, prefix):
    """Return True if team has ≥1 known debuffer Uma."""
    for i in (1, 2, 3):
        col = f"{prefix} - Uma {i}"
        if col in row and pd.notna(row[col]):
            uma = str(row[col]).strip().title()
            if uma in DEBUFF_TYPE:  # known debuffer (speed or stamina)
                return True
    return False

def build_round_team_wr_debuffer(df, prefix):
    """Compute WR for teams WITH vs WITHOUT debuffers for one round."""
    win_col  = f"{prefix} - No. of wins"
    race_col = f"{prefix} - No. of races played"
    uma_cols = [f"{prefix} - Uma {i}" for i in (1,2,3)]
    use_cols = [c for c in [win_col, race_col] + uma_cols if c in df.columns]

    if win_col not in df.columns or race_col not in df.columns:
        return pd.DataFrame(columns=["Round","HasDebuffer","Teams","Wins","Races","WinRate"])

    tmp = df[use_cols].copy()
    tmp[win_col]  = pd.to_numeric(tmp[win_col],  errors="coerce")
    tmp[race_col] = pd.to_numeric(tmp[race_col], errors="coerce")

    tmp["HasDebuffer"] = tmp.apply(lambda r: has_debuffer(r, prefix), axis=1)

    out = (tmp.groupby("HasDebuffer")
               .agg(Teams=(race_col, "count"),
                    Wins=(win_col, "sum"),
                    Races=(race_col, "sum"))
               .reset_index())
    out["Round"] = prefix
    out["WinRate"] = np.where(out["Races"] > 0, (out["Wins"]/out["Races"])*100, np.nan).round(2)
    return out[["Round","HasDebuffer","Teams","Wins","Races","WinRate"]]

def team_debuffer_type(row, prefix):
    """
    Returns one of:
    No Debuffer, Speed, Stamina, Other, or Mixed
    """
    umas = []
    for i in (1, 2, 3):
        col = f"{prefix} - Uma {i}"
        if col in row and pd.notna(row[col]):
            umas.append(str(row[col]).strip().title())

    # Identify debuffer types on team
    types = {DEBUFF_TYPE.get(u) for u in umas if u in DEBUFF_TYPE}
    types.discard(None)

    if not types:
        return "No Debuffer"
    if len(types) == 1:
        return list(types)[0]  # "Speed", "Stamina", or "Other"
    return "Mixed"

def build_round_team_wr_by_debuffer_type(df, prefix):
    win_col  = f"{prefix} - No. of wins"
    race_col = f"{prefix} - No. of races played"
    uma_cols = [f"{prefix} - Uma {i}" for i in (1,2,3)]
    use_cols = [c for c in [win_col, race_col] + uma_cols if c in df.columns]

    if win_col not in df.columns or race_col not in df.columns:
        return pd.DataFrame(columns=["Round","DebufferType","Teams","Wins","Races","WinRate"])

    tmp = df[use_cols].copy()
    tmp[win_col]  = pd.to_numeric(tmp[win_col],  errors="coerce")
    tmp[race_col] = pd.to_numeric(tmp[race_col], errors="coerce")

    tmp["DebufferType"] = tmp.apply(lambda r: team_debuffer_type(r, prefix), axis=1)

    out = (tmp.groupby("DebufferType")
               .agg(Teams=(race_col, "count"),
                    Wins=(win_col, "sum"),
                    Races=(race_col, "sum"))
               .reset_index())
    out["Round"] = prefix
    out["WinRate"] = np.where(out["Races"] > 0, (out["Wins"]/out["Races"])*100, np.nan).round(2)
    return out[["Round","DebufferType","Teams","Wins","Races","WinRate"]]

def count_debuffers_round_row(row, prefix, debuff_map):
    speed = stamina = other = 0
    for i in (1, 2, 3):
        role = row.get(f"{prefix} - Uma {i} Role", "")
        uma  = row.get(f"{prefix} - Uma {i}", "")
        if isinstance(role, str) and (("debuffer" in role.lower()) or ("hybrid" in role.lower()) or ("domin" in role.lower())):
            uma_norm = str(uma).strip().title()
            t = debuff_map.get(uma_norm)
            if t == "Speed":
                speed += 1
            elif t == "Stamina":
                stamina += 1
            else:
                # Unknown debuffer names default to Other; change to "continue" if you want to exclude unknowns
                other += 1
    return speed, stamina, other

def _per_type_long(df, type_col, label):
    out = (df.groupby(["Round", type_col], as_index=False)
             .agg(AvgWR=("WinRate","mean"),
                  Teams=("WinRate","count"),
                  TotalWins=("Wins","sum"),
                  TotalRaces=("Races","sum")))
    out.insert(1, "Type", label)
    out.rename(columns={type_col: "Count"}, inplace=True)
    out["PooledWR(%)"] = np.where(out["TotalRaces"] > 0, out["TotalWins"] / out["TotalRaces"] * 100.0, np.nan).round(2)
    return out

def _per_type_overall(df, type_col, label):
    out = (df.groupby(type_col, as_index=False)
             .agg(AvgWR=("WinRate","mean"),
                  Teams=("WinRate","count"),
                  TotalWins=("Wins","sum"),
                  TotalRaces=("Races","sum")))
    out.insert(0, "Type", label)
    out.rename(columns={type_col: "Count"}, inplace=True)
    out["PooledWR(%)"] = np.where(out["TotalRaces"] > 0, out["TotalWins"] / out["TotalRaces"] * 100.0, np.nan).round(2)
    return out

def _draw_heat(data, **kws):
    pivot = (
    data.pivot(index="Speed_Count", columns="Stamina_Count", values="PooledWR(%)")
         .sort_index(ascending=False)           # sort Speed_Count (y-axis)
         .sort_index(axis=1, ascending=True)   # also sort Stamina_Count (x-axis)
)
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="viridis", linewidths=0.3, cbar_kws={"label":"WR (%)"})
    plt.xlabel("Stamina_Count"); plt.ylabel("Speed_Count")

