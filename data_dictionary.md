# Input schema and units

One record is an operational log entry. For the supplied assessment CSV, map its columns to these canonical names before running `analyze.py`.

| Column | Type | Meaning |
| --- | --- | --- |
| record_id | text | Unique source entry ID; duplicate IDs are logged and first record retained |
| date | ISO date | Activity date |
| site | text | Facility name |
| electricity_kwh | number | Purchased grid electricity, kWh; must be nonnegative |
| renewable_certificate_kwh | number | Claimed energy attributes, kWh; must be between zero and electricity_kwh |
| water_m3 | number | Purchased/treated water volume, cubic meters |
| waste_kg | number | Total waste generated, kilograms |
| recycle_pct | number | Share of waste sent to recycling, 0 to 100 |
| scope1_kgco2e | number | Direct emissions activity total, kg CO2e, already calculated by source |
| audit_status | text | Operational audit label, normalized to Pending, Complete, or Overdue |

All negative activity amounts and percentages outside 0-100 are rejected. Missing required values are rejected. Other categories of Scope 3, fuel calculation detail, location-specific energy factors and legal obligation evidence are outside this sample schema.
