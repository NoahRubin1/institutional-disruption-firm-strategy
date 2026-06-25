# institutional-disruption-firm-strategy

**Author:** Noah Rubin
**Master's Thesis Repository**
Quantitative Research on Institutional Disruption (Tariffs, Sanctions, Wars etc.)
and Firm-Level Effects and Strategies

---

## Research Overview

This project investigates how exogenous institutional disruptions — defined as
politically-induced shocks to the formal rules governing international economic
exchange — affect firm-level financial performance and strategic adaptation.
Drawing on Institutional Theory (North, 1990) and the Dynamic Capabilities
framework (Teece et al., 1997), the thesis argues that firms are not passive
recipients of institutional shocks but actively reconfigure their resource bases
and supply-chain structures in response.

---

## Theoretical Background

### 1. Institutional Theory (North, 1990; Acemoglu & Robinson, 2012)
Institutions are the "rules of the game" that structure economic incentives.
Tariffs, sanctions, and armed conflict represent abrupt, exogenous changes to
these rules — creating uncertainty, raising transaction costs, and altering
comparative advantages across firms and industries.

### 2. Dynamic Capabilities Framework (Teece et al., 1997; Teece, 2007)
Firms differ in their capacity to sense environmental change, seize new
opportunities, and transform their resource base. Firms with stronger dynamic
capabilities are hypothesised to absorb institutional shocks at lower cost and
to adapt more rapidly than their peers.

### 3. Resource Dependence & Transaction Cost Economics (Peteraf, 1993; Williamson, 1979)
Supply-chain concentration creates resource dependencies that amplify exposure
to institutional disruptions. Transaction cost logic predicts that firms will
re-internalize or re-diversify sourcing when external institutional uncertainty
rises above a threshold.

---

## Hypotheses

**H1 (Performance Effect):**
Firms with higher pre-shock exposure to the disrupted institutional environment
(measured by revenue share, import/export dependence, or geographic concentration)
experience significantly larger declines in Return on Assets (ROA) and Tobin's Q
following institutional disruption events.

**H2 (Heterogeneous Resilience — Dynamic Capabilities):**
The adverse performance effect is attenuated for firms with higher proxies for
dynamic capabilities (e.g., R&D intensity, capability reconfiguration index,
managerial flexibility scores), consistent with Teece (2007).

**H3 (Strategic Adaptation — Supply-Chain Diversification):**
Following institutional disruptions, treated firms significantly increase
geographic diversification of their supply chains, substituting away from
disrupted regions toward third-country partners — consistent with the
"diversification rather than reshoring" pattern documented in recent literature
(Hayakawa & Matsuura, 2025; Fajgelbaum et al., 2021).

---

## Empirical Strategy

### Identification
Institutional disruption events (tariff announcements, sanction impositions,
conflict escalations) are treated as quasi-natural experiments — exogenous shocks
to a subset of firms based on pre-determined geographic and sectoral exposure.

### Primary Method: Staggered Difference-in-Differences (DiD)
- **Treated group:** Firms with above-median exposure to disrupted markets
  (measured in the three years prior to the shock)
- **Control group:** Firms with below-median or no exposure
- **Estimator:** Callaway & Sant'Anna (2021) or Sun & Abraham (2021) to address
  heterogeneous treatment timing and avoid forbidden comparisons in staggered DiD

### Secondary Method: Panel Event Study
- ±12 quarter event window around each disruption date
- Abnormal stock returns and accounting performance metrics as outcomes
- Firm and time fixed effects; standard errors clustered at the firm level

### Key Variables
| Variable | Proxy | Source |
|---|---|---|
| Financial performance | ROA, Tobin's Q, stock return | Compustat / Worldscope |
| Institutional exposure | Revenue share in sanctioned/tariffed country | Worldscope Segments |
| Dynamic capabilities | R&D intensity, patent stock, CapEx/Sales | Compustat |
| Supply chain diversification | Herfindahl index of supplier geography | FactSet Revere / Orbis |
| Geopolitical risk | GPR Index | Caldara & Iacoviello (2022) |
| Tariff shocks | Product-level tariff rates | UN TRAINS / USITC |
| Sanctions | Sanction onset dates & type | TIES Database v4.0 |

---

## Repository Structure

```
institutional-disruption-firm-strategy/
├── data/
│   ├── raw/          # Raw datasets (not tracked in Git — regenerate with `task pull`)
│   └── processed/    # Cleaned datasets (not tracked in Git — regenerate with `task clean`)
├── code/
│   ├── 01_pull_data.py
│   ├── 02_clean.py
│   ├── 03_descriptives.py
│   └── 04_regression.py
├── output/
│   ├── tables/
│   └── figures/
├── references/
│   ├── library.bib   # Full bibliography (BibTeX, auto-exported from Zotero)
│   └── apa.csl       # Citation style
├── research_note.qmd # Quarto research note (renders to PDF via `task render`)
├── Taskfile.yml       # Pipeline orchestration (`task all` runs everything)
├── requirements.txt
└── .env.example       # Copy to .env and fill in your own WRDS credentials
```

## Reproducing the Analysis

```bash
git clone https://github.com/NoahRubin1/institutional-disruption-firm-strategy
cd institutional-disruption-firm-strategy
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your own WRDS_USERNAME
task all                # pull -> clean -> descriptives -> regression -> render
```

`task all` produces `research_note.pdf` (not tracked in Git — render it
locally). `data/` is also excluded from version control; both are
regenerated from scratch by the pipeline above.

---

## Literature
See `references/library.bib` for the full bibliography.
Key references: North (1990), Teece et al. (1997), Acemoglu & Robinson (2012),
Fajgelbaum et al. (2021), Caldara & Iacoviello (2022),
Callaway & Sant'Anna (2021), Baker et al. (2022).
