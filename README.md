# Environmental & Sustainability Specialist - Case Study 4

This is a runnable assessment project. The assessment package names a 2,000-row CSV but does not include it. `data/raw/synthetic_facility_logs.csv` is deliberately **synthetic** and every calculated result is a demonstration, not a company inventory, audit conclusion, certification claim, or GRI disclosure.

## Run

```powershell
python -m pip install -r requirements.txt
python generate_sample.py
python analyze.py --input data/raw/synthetic_facility_logs.csv
```

Open `notebooks/01_carbon_accounting.ipynb` in VS Code or Jupyter to run the same cleaning and analysis interactively. `analyze.py --input path/to/Case_Study_4_Environmental_Sustainability.csv` accepts a real CSV after its fields are mapped to `data_dictionary.md`. Results are written to `results/`.

## Deliverables

- Python notebook and scripts for data hygiene, Scope 1, Scope 2 and limited Scope 3 calculations
- `audit/iso_14001_2026_gap_matrix.csv` and action plan
- `reports/gri_benchmark.md` with a repeatable GRI tracker
- `presentation/environment_executive_brief.pptx`

## Accounting policy

Scope 1 uses reported direct emissions in kg CO2e. Negative or missing values are quarantined rather than silently corrected. Scope 2 location based uses gross purchased electricity multiplied by a site factor. A separate certificate adjusted sensitivity is calculated only when certificates are recorded, capped at electricity usage, and **is not a compliant market based Scope 2 inventory** without instrument quality, vintage, geography and residual mix evidence. Scope 3 here covers purchased water treatment proxy and waste generated in operations only. It is not a complete Scope 3 inventory. Waste recycling percentage affects the waste treatment mix, not gross waste mass. No avoided emissions or offsets are subtracted from Scope 1 or the location based Scope 2 figure.

`factors.csv` contains **illustrative factors only**, chosen to demonstrate the calculation and held constant across sites. Replace each factor with approved geography, year, activity and treatment specific factors, retaining source and version before external reporting. The synthetic sample is for a single illustrative period (2025); it cannot establish year over year progress or a peer benchmark.

## Controls

The pipeline retains raw input, normalizes site and audit status labels, drops duplicate record IDs after logging them, quarantines impossible measures, exports row level calculations, and reconciles accepted and rejected counts. Review `results/exceptions.csv` before using any totals. To refresh, replace the input and rerun; do not overwrite factor history without documenting changes.

## Sources

- [ISO 14001:2026 overview and standard status](https://www.iso.org/standard/14001)
- [ISO 14001:2026 publicly accessible clause outline](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A14001%3Aed-4%3Av1%3Aen)
- [GHG Protocol Scope 2 Guidance](https://ghgprotocol.org/sites/default/files/GHG%20Protocol%20Scope%202%20Guidance.pdf)
- [GRI Standards](https://www.globalreporting.org/standards/)
- [EPA Emission Factors Hub](https://www.epa.gov/climateleadership/ghg-emission-factors-hub)

The matrix uses clause headings as a planning aid. A qualified lead auditor must verify the full licensed standard, applicable obligations, site evidence, and certification readiness.
