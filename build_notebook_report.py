"""Build a portable notebook and illustrative GRI report from current outputs."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent

def md(source): return {"cell_type":"markdown","metadata":{},"source":source.splitlines(True)}
def code(source): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":source.splitlines(True)}

cells = [
 md("# Case Study 4: Environmental accounting\n\nThis notebook demonstrates a reproducible calculation using **synthetic records and illustrative factors**. It is not a verified emissions inventory or certification assessment. Run from the project root."),
 md("## 1. Generate and inspect the sample\n\nThe sample contains 2,000 records and injected site, percentage, Scope 1, audit status, and duplicate-ID defects."),
 code("from pathlib import Path\nimport sys\nimport pandas as pd\nROOT = Path.cwd()\nif not (ROOT / 'analyze.py').exists():\n    ROOT = ROOT.parent\nsys.path.insert(0, str(ROOT))\nfrom generate_sample import main as generate_sample\nfrom analyze import process\ngenerate_sample()\nraw = pd.read_csv(ROOT / 'data/raw/synthetic_facility_logs.csv')\nprint(raw.shape)\nprint(raw.head().to_string(index=False))"),
 md("## 2. Clean and calculate\n\n`process` writes every rejected record and its reason. It uses four separately versioned assumptions in `factors.csv`. Scope 1 is provided as a direct-emission source field; Scope 2 and the limited Scope 3 categories are calculated from activity data. No invalid value is silently capped or made positive."),
 code("control = process(ROOT / 'data/raw/synthetic_facility_logs.csv', ROOT / 'results')\nassert control['reconciles']\nexceptions = pd.read_csv(ROOT / 'results/exceptions.csv')\nprint(exceptions['issue'].value_counts().to_string())"),
 md("## 3. Inspect the equations\n\nAll results are metric tons CO2e. Scope 2 location based = gross electricity kWh × electricity factor ÷ 1,000. Limited Scope 3 = water m3 × water factor ÷ 1,000 + recycled waste kg × recycled factor ÷ 1,000 + landfill waste kg × landfill factor ÷ 1,000. The certificate adjusted number is a sensitivity only and cannot be used as a GHG Protocol market based total without quality evidence."),
 code("calc = pd.read_csv(ROOT / 'results/clean_calculations.csv')\nf = pd.read_csv(ROOT / 'factors.csv').set_index('factor_id')['kgco2e_per_unit']\nr = calc.iloc[0]\nassert abs(r.scope2_location_tco2e - r.electricity_kwh * f['ELEC_DEMO'] / 1000) < 1e-9\nassert abs(r.scope3_limited_tco2e - (r.water_m3*f['WATER_DEMO'] + r.waste_recycled_kg*f['RECYCLE_DEMO'] + r.waste_landfill_kg*f['LANDFILL_DEMO'])/1000) < 1e-9\nprint(calc[['record_id','site','scope1_tco2e','scope2_location_tco2e','scope3_limited_tco2e','total_limited_tco2e']].head().to_string(index=False))"),
 md("## 4. Site tracker and quality gate\n\nThe sum of accepted row emissions must match the site summary. Report status remains illustrative until source records, boundaries, site factors, instrument evidence, and Scope 3 completeness are reviewed."),
 code("site = pd.read_csv(ROOT / 'results/site_summary.csv')\nassert abs(calc.total_limited_tco2e.sum() - site.total_limited_tco2e.sum()) < 1e-8\nprint(site[['site','electricity_kwh','water_m3','waste_kg','recycling_rate_pct','scope1_tco2e','scope2_location_tco2e','scope3_limited_tco2e','total_limited_tco2e']].round(2).to_string(index=False))\nprint('Rejected rows:', len(exceptions))"),
]
nb = {"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3"}},"nbformat":4,"nbformat_minor":5}
(ROOT / "notebooks").mkdir(exist_ok=True)
(ROOT / "notebooks/01_carbon_accounting.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")

site = pd.read_csv(ROOT / "results/site_summary.csv")
control = json.loads((ROOT / "results/run_control.json").read_text(encoding="utf-8"))
tot = site.select_dtypes("number").sum()
rows = [
 ("GRI 302-1", "Energy consumption", "Electricity kWh", f"{tot.electricity_kwh:,.0f} kWh", "Partial: fuel, heat and other energy absent"),
 ("GRI 303-3", "Water withdrawal", "Water m3", f"{tot.water_m3:,.0f} m3", "Proxy: source and stress area absent"),
 ("GRI 305-1", "Direct GHG emissions", "Scope 1", f"{tot.scope1_tco2e:,.1f} tCO2e", "Source direct-emission field not independently recalculated"),
 ("GRI 305-2", "Energy indirect GHG emissions", "Scope 2 location", f"{tot.scope2_location_tco2e:,.1f} tCO2e", "Illustrative generic factor; market based total unavailable"),
 ("GRI 305-3", "Other indirect GHG emissions", "Limited Scope 3", f"{tot.scope3_limited_tco2e:,.1f} tCO2e", "Only water proxy and waste generated in operations"),
 ("GRI 306-3", "Waste generated", "Waste kg", f"{tot.waste_kg:,.0f} kg", "Hazardous split and treatment evidence absent"),
 ("GRI 306-4", "Waste diverted from disposal", "Recycled waste kg", f"{tot.waste_recycled_kg:,.0f} kg", "Destination evidence absent"),
]
table = "| GRI mapping | Measure | Tracker field | Synthetic result | Readiness |\n| --- | --- | --- | ---: | --- |\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows)
site_table = "| Site | Scope 1 | Scope 2 location | Limited Scope 3 | Total limited | Recycling rate |\n| --- | ---: | ---: | ---: | ---: | ---: |\n" + "\n".join(f"| {r.site} | {r.scope1_tco2e:,.1f} | {r.scope2_location_tco2e:,.1f} | {r.scope3_limited_tco2e:,.1f} | {r.total_limited_tco2e:,.1f} | {r.recycling_rate_pct:.1f}% |" for r in site.itertuples())
report = f"""# GRI sustainability benchmarking and data tracker

**Assessment demonstration | 2025 synthetic activity | Generated 11 October 2026**

## Executive readout

The source CSV contains {control['source_rows']:,} synthetic logs. The pipeline accepted {control['accepted_rows']:,} and quarantined {control['rejected_rows']:,}; counts reconcile. Accepted records produce **{tot.total_limited_tco2e:,.1f} tCO2e** across Scope 1, location based Scope 2, and **only two illustrative Scope 3 components**. This is a model demonstration, not an actual organizational footprint. No real company, industry peer, prior-year baseline, or intensity denominator was supplied, so no defensible performance ranking or change claim is possible.

## Site comparison

All carbon values are tCO2e. The total combines only the categories listed above. Site differences reflect synthetic activity volumes and a common illustrative factor, not operating efficiency.

{site_table}

## GRI disclosure mapping and refresh tracker

{table}

### Reporting gate

1. Confirm organizational and operational boundaries, reporting period, facilities, and meter completeness.
2. Resolve all exceptions with source evidence. Preserve original and corrected values plus approver.
3. Approve site/year specific electricity and treatment factors with source, unit, version, and calculation method.
4. Verify energy attribute certificates against GHG Protocol Scope 2 quality criteria and obtain residual mix factors before a market based claim.
5. Complete material Scope 3 category screening and obtain vendor treatment evidence.
6. Add comparable prior periods and appropriate activity denominators before calling this a benchmark.
7. Conduct GRI material topic assessment and review each disclosure's full requirements and omissions before publication.

## Standards timing

For material issued in 2026, this tracker maps to GRI 302: Energy 2016, GRI 303: Water and Effluents 2018, GRI 305: Emissions 2016, and GRI 306: Waste 2020. GRI 102: Climate Change 2025 and GRI 103: Energy 2025 become effective for reports published from 1 January 2027; plan a crosswalk before the next cycle. A GRI disclosure mapping does not itself mean reporting in accordance with GRI.

## Method limits

The model treats water as an illustrative purchased-service Scope 3 proxy and waste as Category 5 treatment emissions. Scope 1 is accepted from the source as kg CO2e; fuel or refrigerant subcomponents and GWP basis are unknown. Scope 2 certificate adjusted sensitivity is excluded from the inventory total. No recycling credit, avoided emission, or offset is netted against gross emissions.

## Primary references

- [ISO 14001:2026](https://www.iso.org/standard/14001)
- [GRI standards collection](https://www.globalreporting.org/standards/)
- [GRI 302: Energy 2016](https://globalreporting.org/publications/documents/english/gri-302-energy-2016/)
- [GRI 303: Water and Effluents 2018](https://www.globalreporting.org/publications/documents/english/gri-303-water-and-effluents-2018)
- [GRI 305: Emissions 2016](https://globalreporting.org/publications/documents/english/gri-305-emissions-2016/)
- [GRI 306: Waste 2020](https://www.globalreporting.org/standards/standards-development/topic-standard-for-waste-gri-306/)
- [GRI 102/103 timing](https://www.globalreporting.org/standards/standards-development/topic-standard-for-climate-change-and-energy/)
- [GHG Protocol Scope 2 Guidance](https://ghgprotocol.org/sites/default/files/GHG%20Protocol%20Scope%202%20Guidance.pdf)
"""
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports/gri_benchmark.md").write_text(report, encoding="utf-8")
print("Wrote notebook and GRI report")
