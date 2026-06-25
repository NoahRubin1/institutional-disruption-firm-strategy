"""
01_pull_data.py
---------------
Pull firm-level annual data from WRDS Compustat Global for the
US-China trade war difference-in-differences design.

Treated group : firms domiciled in China (CHN) — directly targeted by the
                2018 US Section 301 tariffs.
Control group : firms domiciled in Japan (JPN), South Korea (KOR), and
                Taiwan (TWN) — comparable East Asian export economies not
                subject to the 2018 US-China tariff escalation.

Output: data/raw/compustat_global_raw.parquet

Notes
-----
- Uses python-dotenv to load WRDS credentials from .env (never hardcoded).
- Saves as Parquet (columnar, compressed) rather than CSV for faster downstream reads.
- All paths are relative — do not use absolute paths.
"""

import os
from pathlib import Path

import pandas as pd
import wrds
from dotenv import load_dotenv

# ── Credentials ───────────────────────────────────────────────────────────────
load_dotenv()  # reads WRDS_USERNAME / WRDS_PASSWORD from .env
WRDS_USER = os.getenv("WRDS_USERNAME")
WRDS_PASS = os.getenv("WRDS_PASSWORD")
if not WRDS_USER:
    raise EnvironmentError(
        "WRDS_USERNAME not set.\n" "Copy .env.example → .env and fill in your username."
    )

# ── Output path — relative, never absolute ────────────────────────────────────
OUT_PATH = Path("data/raw/compustat_global_raw.parquet")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Treated (China) and control (Japan, South Korea, Taiwan) countries ───────
TREATED_CONTROL_COUNTRIES = "'CHN','JPN','KOR','TWN'"

# ── WRDS query ────────────────────────────────────────────────────────────────
QUERY = f"""
    SELECT
        gvkey,          -- firm identifier
        conm,           -- company name
        fyear,          -- fiscal year
        loc,            -- country of incorporation (ISO 3)
        sich,           -- historical industry code (SIC)
        curcd,          -- reporting currency code
        at,             -- total assets
        sale,           -- net sales
        ib,             -- income before extraordinary items (net income proxy)
        xrd,            -- R&D expenditure
        dltt,           -- long-term debt total
        capx,           -- capital expenditure
        che,            -- cash and short-term investments
        seq,            -- stockholders' equity
        emp             -- employees (thousands)
    FROM
        comp_global_daily.g_funda
    WHERE
        loc IN ({TREATED_CONTROL_COUNTRIES})
        AND fyear BETWEEN 2010 AND 2022
        AND indfmt = 'INDL'
        AND datafmt = 'HIST_STD'
        AND popsrc = 'I'
        AND consol = 'C'
        AND at > 0
        AND sale > 0
"""

print("Connecting to WRDS...")
db = wrds.Connection(wrds_username=WRDS_USER, wrds_password=WRDS_PASS)

print("Pulling Compustat Global (this may take a minute)...")
df = db.raw_sql(QUERY)
db.close()

print(f"  Raw observations: {len(df):,}")
print(f"  Unique firms:     {df['gvkey'].nunique():,}")
print(f"  Years covered:    {df['fyear'].min()}–{df['fyear'].max()}")
print(f"  Countries:        {sorted(df['loc'].unique())}")

# ── Save as Parquet ───────────────────────────────────────────────────────────
# Parquet is columnar + compressed → much faster than CSV for repeated reads.
df.to_parquet(OUT_PATH, index=False)
print(f"\nSaved to {OUT_PATH}")

# Document download metadata (source, date, license)
meta = OUT_PATH.with_suffix(".meta.txt")
from datetime import date

meta.write_text(
    f"Source: WRDS Compustat Global (comp_global_daily.g_funda)\n"
    f"Downloaded: {date.today().isoformat()}\n"
    f"License: WRDS subscriber agreement\n"
    f"Query: Treated (CHN) and control (JPN, KOR, TWN) firms, fiscal years 2010-2022\n"
    f"Rows: {len(df):,} | Firms: {df['gvkey'].nunique():,}\n"
)
print(f"Download metadata saved to {meta}")
