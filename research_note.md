---
title: "Internationalization and Firm Performance among European SMEs"
subtitle: "A Panel Data Analysis of the DOI–Performance Relationship"
author: "[Student Name] | ExInt II | WU Vienna | SS 2026"
date: "May 2026"
bibliography: references/library.bib
format:
  pdf:
    toc: false
    number-sections: true
    geometry: margin=2.5cm
    fontsize: 11pt
    linestretch: 1.2
---

# Introduction

Small and medium-sized enterprises (SMEs) constitute the backbone of European economies, yet the performance consequences of their international expansion remain contested [@Lu2001]. A central question concerns the shape of the DOI–performance relationship: is more internationalization always better, or does a threshold exist beyond which costs outweigh benefits?

Building on internalization theory [@Buckley1976], the liability of foreignness [@Zaheer1995], and organizational learning [@Johanson1977], this note argues that the relationship takes an inverted U-shape. R&D intensity — as a proxy for absorptive capacity [@Cohen1990] — is expected to moderate this curve, sustaining performance gains at higher internationalization levels.

**Research question:** Does degree of internationalization exhibit an inverted U-shaped relationship with firm performance among European SMEs, and does R&D intensity moderate this relationship?

**H1:** DOI positively affects performance at low levels but the effect turns negative at high levels (inverted U-shape).

**H2:** R&D intensity positively moderates the DOI–performance relationship.

# Data and Method

## Sample

Data are drawn from WRDS Compustat Global, covering European SMEs (≤250 employees or ≤€43m total assets per EU definition) over 2005–2020. After applying cleaning filters (see `code/02_clean.py`), the sample comprises [N] firm-year observations from [N_firms] firms across [N_countries] countries.

## Variables

**Dependent variable.** Return on assets (ROA = net income / total assets) is a standard accounting-based performance measure available for private SMEs, which often lack stock market data [@Hitt1997].

**Key independent variables.** DOI is operationalized as the ratio of foreign income to total sales [@Sullivan1994]. DOI² tests the non-linear prediction in H1. R&D intensity (R&D expenditure / total assets) proxies absorptive capacity [@Cohen1990]; missing values are set to zero (the firm did not report R&D expenditure).

**Controls.** Firm size (log total assets), leverage (long-term debt / total assets), and age (years since incorporation). All continuous variables are winsorized at 1st and 99th percentiles.

## Estimation

Two-way fixed effects panel regressions using `linearmodels` [@linearmodels], with firm and year fixed effects and standard errors clustered at the firm level:

$$
\text{ROA}_{it} = \beta_1 \text{DOI}_{it} + \beta_2 \text{DOI}_{it}^2 + \beta_3 \text{R\&D}_{it} + \beta_4 (\text{DOI} \times \text{R\&D})_{it} + \gamma X_{it} + \mu_i + \lambda_t + \varepsilon_{it}
$$

where $\mu_i$ captures time-invariant firm characteristics and $\lambda_t$ common macroeconomic shocks.

# Results

## Descriptive Statistics

[Insert Table 1 — `output/tables/summary_statistics.csv`]

[Insert Figure 1 — `output/figures/doi_roa_relationship.png`]

## Regression Results

[Insert Table 2 — `output/tables/regression_results.csv`]

**H1.** Model 2 shows β(DOI) = [value] (p = [p]) and β(DOI²) = [value] (p = [p]), consistent with / inconsistent with an inverted U-shape. The estimated performance-maximizing DOI level is [inflection], which lies [above/below] the sample mean of [mean]. H1 is [supported / not supported].

**H2.** The interaction coefficient in Model 3 is β(DOI × R&D) = [value] (p = [p]), indicating that R&D-intensive SMEs [sustain / do not sustain] higher performance at greater internationalization levels. H2 is [supported / not supported].

# Discussion and Conclusion

[Summarize findings, connect to theory, note limitations.]

**Limitations.** First, the DOI proxy (foreign income share) may understate the breadth of international operations for firms with foreign assets but limited foreign income [@Sullivan1994]. Second, the panel fixed-effects estimator cannot fully address reverse causality: high-performing firms may be more likely to internationalize. Third, the sample is limited to firms with Compustat Global coverage, which may oversample larger SMEs.

# References

::: {#refs}
:::
