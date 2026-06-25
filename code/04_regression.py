"""
04_regression.py
----------------
Panel difference-in-differences regressions testing H1 and H2.

Input:  data/processed/panel_clean.parquet
Output: output/tables/regression_results.csv

Models
------
(1) OLS:        RoA ~ Treated + Post + Treated x Post + controls   (no FE)
(2) TWFE:       RoA ~ Treated x Post + controls                    (firm + year FE)
(3) TWFE + H2:  RoA ~ Treated x Post + Treated x Post x R&D + R&D
                + controls                                         (firm + year FE)

Estimator: linearmodels PanelOLS with two-way fixed effects and firm-clustered SEs
           (OLS uses pooled PanelOLS with no entity/time effects, clustered SEs).

Reading results
---------------
H1 supported if: beta(Treated x Post) < 0 and statistically significant
H2 supported if: beta(Treated x Post x R&D) > 0 and statistically significant
Stars: *** p<0.01, ** p<0.05, * p<0.10
"""

import warnings
from pathlib import Path

import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path("data/processed/panel_with_vars.parquet")
TABLE_PATH = Path("output/tables")
TABLE_PATH.mkdir(parents=True, exist_ok=True)

# ── Load & Set Panel Index ────────────────────────────────────────────────────
# linearmodels requires a MultiIndex: (entity, time)
df = pd.read_parquet(DATA_PATH)
df = df.set_index(["gvkey", "fyear"])

print(f"Panel: {len(df):,} obs | {df.index.get_level_values('gvkey').nunique():,} firms")

CONTROLS = ["ln_at", "leverage", "capx_intensity", "cash_ratio"]


def run_panel(dep: str, indep: list[str], entity_effects: bool, time_effects: bool) -> object:
    """Estimate a PanelOLS model with firm-clustered standard errors."""
    formula_vars = indep + CONTROLS
    sub = df[[dep, *formula_vars]].dropna()
    fe_terms = []
    if entity_effects:
        fe_terms.append("EntityEffects")
    if time_effects:
        fe_terms.append("TimeEffects")
    formula = f"{dep} ~ {' + '.join(formula_vars)}"
    if fe_terms:
        formula += " + " + " + ".join(fe_terms)
    else:
        formula += " + 1"  # pooled model needs explicit intercept
    mod = PanelOLS.from_formula(formula, data=sub)
    return mod.fit(cov_type="clustered", cluster_entity=True)


# ── Estimate three models ─────────────────────────────────────────────────────
print("\nEstimating models...")
res1 = run_panel("roa", ["treated", "post", "treated_x_post"], entity_effects=False, time_effects=False)
print("  Model 1 (OLS) done")

res2 = run_panel("roa", ["treated_x_post"], entity_effects=True, time_effects=True)
print("  Model 2 (TWFE, H1) done")

res3 = run_panel(
    "roa", ["treated_x_post", "rd_intensity", "treated_x_post_x_rd"],
    entity_effects=True, time_effects=True,
)
print("  Model 3 (TWFE + H2) done")


# ── Build Results Table ───────────────────────────────────────────────────────
KEY_VARS = [
    "treated", "post", "treated_x_post", "rd_intensity", "treated_x_post_x_rd",
] + CONTROLS

model_labels = ["(1) OLS", "(2) TWFE", "(3) TWFE+H2"]
models = [res1, res2, res3]

rows = []
for label, res in zip(model_labels, models):
    col: dict = {"Model": label}
    for var in KEY_VARS:
        if var in res.params.index:
            coef = res.params[var]
            se = res.std_errors[var]
            pval = res.pvalues[var]
            stars = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
            col[var] = f"{coef:.4f}{stars}"
            col[f"{var}_se"] = f"({se:.4f})"
        else:
            col[var] = ""
            col[f"{var}_se"] = ""
    col["Firm FE"] = "Yes" if res is not res1 else "No"
    col["Year FE"] = "Yes" if res is not res1 else "No"
    col["Clustered SE"] = "Yes"
    col["N"] = f"{int(res.nobs):,}"
    col["R2"] = f"{res.rsquared:.3f}"
    rows.append(col)

results_df = pd.DataFrame(rows).set_index("Model").T
print("\n=== Regression Results ===")
print(results_df.to_string())
results_df.to_csv(TABLE_PATH / "regression_results.csv")
print("\nSaved regression_results.csv")


# ── H1: DiD Effect ─────────────────────────────────────────────────────────────
print("\n--- H1 Diagnostic ---")
b1 = res2.params["treated_x_post"]
p1 = res2.pvalues["treated_x_post"]
print(f"  beta(Treated x Post) = {b1:.4f}  (p = {p1:.3f})")
if b1 < 0 and p1 < 0.1:
    print("  -> H1 supported: tariff-targeted firms show a significant RoA decline post-2018")
else:
    print("  -> H1 not supported at conventional significance levels")

# ── H2: Moderation by R&D Intensity ───────────────────────────────────────────
print("\n--- H2 Diagnostic ---")
b2 = res3.params["treated_x_post_x_rd"]
p2 = res3.pvalues["treated_x_post_x_rd"]
stars = "***" if p2 < 0.01 else "**" if p2 < 0.05 else "*" if p2 < 0.1 else "(n.s.)"
print(f"  beta(Treated x Post x R&D) = {b2:.4f} {stars}  (p = {p2:.3f})")
if b2 > 0 and p2 < 0.1:
    print("  -> H2 supported: R&D intensity attenuates the negative shock effect")
else:
    print("  -> H2 not supported at conventional significance levels")

# ── OLS vs TWFE bias comparison ───────────────────────────────────────────────
b_ols = res1.params["treated_x_post"]
bias_pct = abs((b_ols - b1) / b_ols) * 100 if b_ols != 0 else float("nan")
print(f"\n--- OLS vs. TWFE ---")
print(f"  beta_OLS(Treated x Post)  = {b_ols:.4f}")
print(f"  beta_TWFE(Treated x Post) = {b1:.4f}")
print(f"  Absolute bias             = {bias_pct:.1f}%")

print("""
-----------------------------------------------------------
Interpretation guide:
  Stars: *** p<0.01, ** p<0.05, * p<0.10
  SEs in parentheses, clustered at firm level
  Models (2)-(3): firm FE + year FE (two-way fixed effects)
-----------------------------------------------------------
""")
