"""
02_clean.py
-----------
Clean raw Compustat data and construct the difference-in-differences panel
for the US-China trade war design.

Input:  data/raw/compustat_global_raw.parquet
Output: data/processed/panel_clean.parquet      (filtered, pre-variable construction)
        data/processed/panel_with_vars.parquet  (final panel with all constructed variables)

Variable construction
---------------------
ROA                  = ib / at                  (return on assets; performance, Y)
Treated              = 1 if loc == 'CHN'        (firm headquartered in the
                       tariff-targeted country)
Post                 = 1 if fyear >= 2018        (US Section 301 tariff escalation)
Treated x Post       = treated * post           (DiD term, H1)
R&D intensity        = xrd / at                 (dynamic capabilities proxy, 0 if missing)
Treated x Post x R&D = treated_x_post * rd_intensity (moderation term, H2)
Firm size            = log(at)
Leverage             = dltt / at
CAPX intensity       = capx / at
Cash ratio           = che / at

All continuous ratio variables are winsorized at 1%-99%. Because firms
report in local currency (CNY, JPY, KRW, TWD), all key variables used here
are ratios (numerator and denominator in the same currency), which are
currency-invariant. Firm size (log assets) is not cross-country comparable
in levels, but enters the fixed-effects models only through within-firm
variation, which is currency-invariant within a firm.
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths — always relative ────────────────────────────────────────────────────
RAW_PATH       = Path("data/raw/compustat_global_raw.parquet")
CLEAN_PATH     = Path("data/processed/panel_clean.parquet")
WITH_VARS_PATH = Path("data/processed/panel_with_vars.parquet")
CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading raw data...")
df = pd.read_parquet(RAW_PATH)
n_raw = len(df)
print(f"  Raw observations: {n_raw:,} | firms: {df['gvkey'].nunique():,}")


# ── Data Quality Filter ────────────────────────────────────────────────────────
quality_mask = (df["at"] > 0.1) & (df["sale"] > 0) & (df["seq"] > 0) & (df["at"] >= 1)
df = df[quality_mask].copy()
print(f"  After data quality filter: {len(df):,} (removed {n_raw - len(df):,})")

# Save the filtered-but-pre-construction panel
df.to_parquet(CLEAN_PATH, index=False)
print(f"  Saved filtered panel to {CLEAN_PATH}")


# ── Construct Variables ───────────────────────────────────────────────────────
# Performance
df["roa"] = df["ib"] / df["at"]

# Treatment indicators
df["treated"] = (df["loc"] == "CHN").astype(int)
df["post"] = (df["fyear"] >= 2018).astype(int)
df["treated_x_post"] = df["treated"] * df["post"]

# R&D intensity — treat missing xrd as zero (firm did not report R&D expenditure)
df["rd_intensity"] = df["xrd"].fillna(0) / df["at"]

# Triple interaction for H2 (dynamic capabilities moderation)
df["treated_x_post_x_rd"] = df["treated_x_post"] * df["rd_intensity"]

# Controls
df["ln_at"] = np.log(df["at"])
df["leverage"] = df["dltt"] / df["at"]
df["capx_intensity"] = df["capx"] / df["at"]
df["cash_ratio"] = df["che"] / df["at"]


# ── Winsorize at 1%-99% ───────────────────────────────────────────────────────
def winsorize(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    """Clip series at given quantiles."""
    lo = series.quantile(lower)
    hi = series.quantile(upper)
    return series.clip(lo, hi)


for col in ["roa", "rd_intensity", "leverage", "capx_intensity", "cash_ratio"]:
    df[col] = winsorize(df[col])

# Recompute derived variables after winsorizing inputs
df["treated_x_post_x_rd"] = df["treated_x_post"] * df["rd_intensity"]


# ── Drop Observations with Missing Core Variables ─────────────────────────────
core_vars = [
    "roa", "treated", "post", "treated_x_post", "rd_intensity",
    "treated_x_post_x_rd", "ln_at", "leverage", "capx_intensity", "cash_ratio",
]
n_before = len(df)
df = df.dropna(subset=core_vars).copy()
print(f"  After dropping missing core vars: {len(df):,} (removed {n_before - len(df):,})")


# ── Require >= 3 Observations per Firm (within-firm identification) ──────────
obs_per_firm = df.groupby("gvkey")["fyear"].count()
valid_firms = obs_per_firm[obs_per_firm >= 3].index
n_before = len(df)
df = df[df["gvkey"].isin(valid_firms)].copy()
print(f"  After min-obs filter (>=3 per firm): {len(df):,} (removed {n_before - len(df):,})")
print(f"  Final: {len(df):,} obs | {df['gvkey'].nunique():,} firms | {df['loc'].nunique()} countries")
print(f"  Years: {df['fyear'].min()}-{df['fyear'].max()}")
print(f"  Treated (CHN) firm-years: {df['treated'].sum():,} ({df['treated'].mean()*100:.1f}%)")


# ── Save ──────────────────────────────────────────────────────────────────────
df.to_parquet(WITH_VARS_PATH, index=False)
print(f"\nSaved final panel with constructed variables to {WITH_VARS_PATH}")
