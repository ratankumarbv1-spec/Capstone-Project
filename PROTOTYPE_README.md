# E-waste Credit Engine: first prototype

This is a small learning demo, not yet the final submission. It shows the shape of the program: CSV inputs go in, the rules are applied, and readable reports come out.

The newer, larger community collection-point example is in `community_demo/`. This original demo remains unchanged as the smallest example to study first.

## Run it

From the project folder:

```powershell
python prototype.py
```

The sample input files are in `demo_data/`.

## Understand the sample

- `sources.csv` gives each source its ID, type, and distance from the depot.
- `rates.csv` gives each category's rupees-per-kg credit and whether the category is hazardous.
- `requests.csv` gives each pickup's source and its item lines. An item is written `CATEGORY:COUNT:TOTAL_WEIGHT_KG`; for example `IT:2:10` means two IT items weighing 10 kg total.
- `prototype.py` loads those files, calculates amounts, places accepted pickups on vehicle days, then prints reports.

## What the examples demonstrate

- `R001` is a 5 kg household pickup exactly at the minimum. The household BATTERY line is deducted at Rs 15/kg, and the source is exactly 10 km away, so the pickup charge is zero.
- `R002` is 13.2 km away. The distance is rounded up to 14 km, so 4 km beyond the free 10 km is charged: Rs 48.
- `R003` weighs exactly 200 kg, so its pickup charge is waived. It also shows that a large request is one stop.
- `R004` is a 4 kg household request and is refused as `BELOW_MINIMUM`.
- `R005` is a 5 kg household request, so it meets the minimum.

## Reading the code

`Source`, `Pickup`, and `VehicleDay` hold the basic data. `calculate()` applies rates, household battery/CRT deductions, and pickup charges. `schedule_pickup()` checks the stop, total-weight, and hazardous-weight limits together, then selects the earliest day that fits. `main()` connects the steps and prints the reports.

For this demo, a request above 300 kg of hazardous material is refused as `EXCEEDS_DAILY_HAZARD_LIMIT`, because it cannot fit on any day if requests must remain whole. The brief does not specify that refusal reason, so this is a prototype decision that needs instructor confirmation before the final version.

Money is rounded to whole rupees for net credit. Displayed subtotals retain two decimals to make the arithmetic easy to follow. The report format and validation will be refined when the instructor's sample files and expected outputs arrive.
