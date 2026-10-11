"""Transparent facility data cleaning and illustrative GHG calculation."""
from pathlib import Path
import argparse
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
REQUIRED = ["record_id", "date", "site", "electricity_kwh", "renewable_certificate_kwh", "water_m3", "waste_kg", "recycle_pct", "scope1_kgco2e", "audit_status"]
NUMERIC = REQUIRED[3:9]

def process(source: Path, out: Path):
    raw = pd.read_csv(source, dtype={"record_id": "string", "site": "string", "audit_status": "string"})
    missing = sorted(set(REQUIRED) - set(raw.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}. See data_dictionary.md")
    raw = raw[REQUIRED].copy()
    raw["source_row"] = range(2, len(raw) + 2)
    df = raw.copy()
    site_names = {"paris hq": "Paris HQ", "austin plant": "Austin Plant", "bangalore office": "Bangalore Office", "singapore hub": "Singapore Hub", "frankfurt dc": "Frankfurt DC", "toronto lab": "Toronto Lab"}
    df["site"] = df["site"].str.strip().str.casefold().map(lambda x: site_names.get(x, x.title()) if isinstance(x, str) else x)
    df["audit_status"] = df["audit_status"].str.strip().str.casefold().map({
        "pending": "Pending", "pending audit": "Pending", "complete": "Complete", "completed": "Complete", "overdue": "Overdue"
    })
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    issues = []
    for i, row in df.iterrows():
        reason = []
        if pd.isna(row["record_id"]) or not str(row["record_id"]).strip(): reason.append("missing record_id")
        elif df.loc[:i-1, "record_id"].eq(row["record_id"]).any(): reason.append("duplicate record_id")
        if pd.isna(row["date"]): reason.append("invalid date")
        if pd.isna(row["site"]) or not str(row["site"]).strip(): reason.append("missing site")
        if pd.isna(row["audit_status"]): reason.append("unknown audit_status")
        for c in NUMERIC:
            if pd.isna(row[c]): reason.append(f"missing/invalid {c}")
            elif row[c] < 0: reason.append(f"negative {c}")
        if pd.notna(row["recycle_pct"]) and row["recycle_pct"] > 100: reason.append("recycle_pct > 100")
        if pd.notna(row["renewable_certificate_kwh"]) and pd.notna(row["electricity_kwh"]) and row["renewable_certificate_kwh"] > row["electricity_kwh"]: reason.append("certificates exceed electricity")
        issues.append("; ".join(reason))
    df["issue"] = issues
    out.mkdir(parents=True, exist_ok=True)
    exceptions = df[df.issue.ne("")].copy()
    exceptions.to_csv(out / "exceptions.csv", index=False)
    clean = df[df.issue.eq("")].drop(columns="issue").copy()
    factors = pd.read_csv(ROOT / "factors.csv").set_index("factor_id")["kgco2e_per_unit"]
    f = lambda name: float(factors.loc[name])
    clean["scope1_tco2e"] = clean.scope1_kgco2e / 1000
    clean["scope2_location_tco2e"] = clean.electricity_kwh * f("ELEC_DEMO") / 1000
    clean["scope2_certificate_sensitivity_tco2e"] = (clean.electricity_kwh - clean.renewable_certificate_kwh) * f("ELEC_DEMO") / 1000
    clean["scope3_water_tco2e"] = clean.water_m3 * f("WATER_DEMO") / 1000
    clean["waste_recycled_kg"] = clean.waste_kg * clean.recycle_pct / 100
    clean["waste_landfill_kg"] = clean.waste_kg - clean.waste_recycled_kg
    clean["scope3_waste_tco2e"] = (clean.waste_recycled_kg * f("RECYCLE_DEMO") + clean.waste_landfill_kg * f("LANDFILL_DEMO")) / 1000
    clean["scope3_limited_tco2e"] = clean.scope3_water_tco2e + clean.scope3_waste_tco2e
    clean["total_limited_tco2e"] = clean.scope1_tco2e + clean.scope2_location_tco2e + clean.scope3_limited_tco2e
    clean.to_csv(out / "clean_calculations.csv", index=False)
    columns = ["electricity_kwh", "renewable_certificate_kwh", "water_m3", "waste_kg", "waste_recycled_kg", "scope1_tco2e", "scope2_location_tco2e", "scope2_certificate_sensitivity_tco2e", "scope3_water_tco2e", "scope3_waste_tco2e", "scope3_limited_tco2e", "total_limited_tco2e"]
    by_site = clean.groupby("site", as_index=False)[columns].sum()
    by_site["recycling_rate_pct"] = 100 * by_site.waste_recycled_kg / by_site.waste_kg
    by_site.to_csv(out / "site_summary.csv", index=False)
    status = clean.groupby(["site", "audit_status"], as_index=False).size().rename(columns={"size":"records"})
    status.to_csv(out / "audit_status_tracker.csv", index=False)
    control = {"source_rows": len(raw), "accepted_rows": len(clean), "rejected_rows": len(exceptions), "reconciles": len(raw) == len(clean) + len(exceptions), "factor_status": "illustrative", "inventory_status": "demonstration only", "source_file": source.name}
    (out / "run_control.json").write_text(json.dumps(control, indent=2), encoding="utf-8")
    print(json.dumps(control, indent=2))
    print(by_site[["site", "scope1_tco2e", "scope2_location_tco2e", "scope3_limited_tco2e", "total_limited_tco2e"]].round(2).to_string(index=False))
    return control

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=ROOT / "data/raw/synthetic_facility_logs.csv")
    p.add_argument("--output", type=Path, default=ROOT / "results")
    a = p.parse_args()
    process(a.input, a.output)
