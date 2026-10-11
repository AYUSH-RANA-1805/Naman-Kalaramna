"""Deterministic synthetic assessment data with injected quality defects."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data/raw/synthetic_facility_logs.csv"
SITES = ["Paris HQ", "Austin Plant", "Bangalore Office", "Singapore Hub", "Frankfurt DC", "Toronto Lab"]

def main():
    rng = np.random.default_rng(14001)
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    n = 2000
    df = pd.DataFrame({
        "record_id": [f"LOG-{i:05d}" for i in range(n)],
        "date": rng.choice(dates, n),
        "site": rng.choice(SITES, n),
        "electricity_kwh": rng.uniform(250, 4200, n).round(2),
        "renewable_certificate_kwh": rng.uniform(0, 220, n).round(2),
        "water_m3": rng.uniform(2, 70, n).round(2),
        "waste_kg": rng.uniform(15, 500, n).round(2),
        "recycle_pct": rng.uniform(25, 85, n).round(2),
        "scope1_kgco2e": rng.uniform(30, 900, n).round(2),
        "audit_status": rng.choice(["Pending Audit", "Complete", "Overdue"], n, p=[.3,.55,.15]),
    })
    df.loc[0:19, "site"] = "Paris HQ "
    df.loc[20:29, "site"] = "paris hq"
    df.loc[30:39, "recycle_pct"] = 105
    df.loc[40:49, "scope1_kgco2e"] = -125
    df.loc[50:59, "audit_status"] = "PENDING"
    df.loc[60:64, "record_id"] = df.loc[0:4, "record_id"].to_numpy()
    df.loc[65:69, "electricity_kwh"] = -1
    df.loc[70:74, "renewable_certificate_kwh"] = df.loc[70:74, "electricity_kwh"] + 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, date_format="%Y-%m-%d")
    print(f"Wrote {len(df)} synthetic rows to {OUT}")

if __name__ == "__main__":
    main()
