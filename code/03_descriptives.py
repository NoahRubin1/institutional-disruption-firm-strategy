"""
03_descriptives.py
------------------
Summary statistics and exploratory figures for the US-China trade war
difference-in-differences design.

Input:  data/processed/panel_clean.parquet
Output: output/tables/summary_statistics.csv
        output/figures/correlation_matrix.png
        output/figures/dv_distribution.png
        output/figures/main_relationship.png
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150, "font.family": "sans-serif"})
WU_BLUE = "#002f5f"
WU_RED = "#c8102e"

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path("data/processed/panel_with_vars.parquet")
TABLE_PATH = Path("output/tables")
FIGURE_PATH = Path("output/figures")
TABLE_PATH.mkdir(parents=True, exist_ok=True)
FIGURE_PATH.mkdir(parents=True, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_parquet(DATA_PATH)
print(f"Loaded {len(df):,} observations | {df['gvkey'].nunique():,} firms")

# ── 1. Summary Statistics ─────────────────────────────────────────────────────
VAR_LABELS = {
    "roa": "RoA (ib/at)",
    "treated_x_post": "Treated x Post (DiD)",
    "rd_intensity": "R&D Intensity (xrd/at)",
    "ln_at": "Firm Size (log assets)",
    "leverage": "Leverage (dltt/at)",
    "capx_intensity": "CAPX Intensity (capx/at)",
    "cash_ratio": "Cash Ratio (che/at)",
}

summary = (
    df[list(VAR_LABELS.keys())]
    .rename(columns=VAR_LABELS)
    .describe(percentiles=[0.25, 0.5, 0.75])
    .T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    .round(3)
)
print("\n=== Summary Statistics ===")
print(summary.to_string())
summary.to_csv(TABLE_PATH / "summary_statistics.csv")
print("Saved summary_statistics.csv")

# ── 2. Correlation Matrix ─────────────────────────────────────────────────────
corr_vars = list(VAR_LABELS.keys())
corr = df[corr_vars].rename(columns=VAR_LABELS).corr().round(2)

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f",
    cmap="RdYlBu_r", center=0, vmin=-1, vmax=1,
    linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8},
)
ax.set_title("Correlation Matrix — Key Variables", fontsize=13, pad=12, color=WU_BLUE)
fig.tight_layout()
fig.savefig(FIGURE_PATH / "correlation_matrix.png", dpi=150)
plt.close()
print("Saved correlation_matrix.png")

# ── 3. Dependent Variable Distribution ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df["roa"], bins=60, color=WU_BLUE, ax=ax, kde=True)
ax.axvline(df["roa"].median(), color=WU_RED, linestyle="--", lw=2, label="Median")
ax.set_xlabel("RoA (Return on Assets)")
ax.set_ylabel("Firm-Year Observations")
ax.set_title("Distribution of Return on Assets (RoA)", color=WU_BLUE)
ax.legend()
fig.tight_layout()
fig.savefig(FIGURE_PATH / "dv_distribution.png", dpi=150)
plt.close()
print("Saved dv_distribution.png")

# ── 4. Main Relationship — Treated vs. Control RoA Around the 2018 Shock ─────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: mean RoA by year, treated vs. control, with 2018 shock line
yearly = df.groupby(["fyear", "treated"], observed=True)["roa"].mean().unstack()
yearly.columns = ["Control (JPN/KOR/TWN)", "Treated (CHN)"]
axes[0].plot(yearly.index, yearly["Control (JPN/KOR/TWN)"], color=WU_BLUE, lw=2, marker="o", label="Control (JPN/KOR/TWN)")
axes[0].plot(yearly.index, yearly["Treated (CHN)"], color=WU_RED, lw=2, marker="o", label="Treated (CHN)")
axes[0].axvline(2018, color="gray", linestyle="--", lw=1.5, label="2018 tariff shock")
axes[0].set_xlabel("Fiscal Year")
axes[0].set_ylabel("Mean RoA")
axes[0].set_title("RoA Over Time — Treated vs. Control", color=WU_BLUE)
axes[0].legend(fontsize=8)

# Right: post-shock RoA gap by R&D tercile (H2 preview)
df_plot = df.copy()
df_plot.reset_index(drop=True, inplace=True)
df_plot["rd_tercile"] = pd.qcut(
    df_plot["rd_intensity"], q=3, labels=["Low R&D", "Mid R&D", "High R&D"], duplicates="drop"
)

palette = {"Low R&D": "#2166ac", "Mid R&D": "#f4a582", "High R&D": WU_RED}
gap_by_tercile = (
    df_plot[df_plot["post"] == 1]
    .groupby(["rd_tercile", "treated"], observed=True)["roa"]
    .mean()
    .unstack()
)
gap_by_tercile["gap"] = gap_by_tercile[1] - gap_by_tercile[0]
axes[1].bar(gap_by_tercile.index.astype(str), gap_by_tercile["gap"],
            color=[palette.get(t, WU_BLUE) for t in gap_by_tercile.index])
axes[1].axhline(0, color="black", lw=1)
axes[1].set_xlabel("R&D Intensity Tercile")
axes[1].set_ylabel("Treated − Control RoA Gap (post-2018)")
axes[1].set_title("Post-Shock Performance Gap by R&D Tercile (H2 preview)", color=WU_BLUE)

fig.suptitle(
    "Institutional Disruption and Firm Performance — US-China Trade War",
    fontsize=13, y=1.02, color=WU_BLUE,
)
fig.tight_layout()
fig.savefig(FIGURE_PATH / "main_relationship.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved main_relationship.png")

print("\nDescriptives complete. Check output/tables/ and output/figures/")
