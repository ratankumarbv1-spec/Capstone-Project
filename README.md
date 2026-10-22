# E-Waste Collection and Recycling Credit Engine

This repository currently contains **learning demos and design notes**, not the official capstone submission. The demos help us understand how the recycler records sources, calculates credits and charges, and schedules accepted pickups into vehicle days. The assignment calls for a command-line program driven by files, so a front end or website is not required.

## What we have understood

- A source is a registered pickup location, with a type (`HOUSEHOLD` or `BULK`) and distance from the depot.
- A pickup request has item lines with a category, item count, and total line weight.
- The engine calculates category credit, household BATTERY/CRT handling deductions, and any pickup charge.
- A household request under 5 kg is refused. A request at exactly 5 kg meets the minimum.
- Accepted requests are placed in request order on the earliest vehicle day that fits all three limits: 1,200 kg total, 8 stops, and 300 kg hazardous material.
- A shared neighborhood collection point is a proposed way to combine contributions from nearby homes into one household request. The combined request must meet 5 kg before it is sent to the engine. Separate requests below 5 kg still follow the refusal rule. Ask the instructor whether a community point can be registered as a `HOUSEHOLD` source.
- Positive net amounts are credits to the source; negative net amounts are amounts payable by the source. A source collecting 500 kg or more in the month qualifies for a recycling certificate line.

## Demo data and outputs

The data and rate values in both demo sets are illustrative. Replace them with instructor-provided data and rates when available.

### Original small demo

- `prototype.py` with `demo_data/` is the first, smaller teaching example.
- Run it with `python prototype.py`.
- See `PROTOTYPE_README.md` for its examples and code map.

### Community collection demo

`community_demo/` has 15 sources (9 shared household collection points across 3 areas and 6 bulk locations), 20 requests, and a visible expected report for the first 15 requests.

From the project root, run the readable, name-based report for the visible 15:

```powershell
python main.py --sources community_demo/sources.csv --rates community_demo/rates.csv --requests community_demo/requests_visible.csv --friendly
```

The five holdout requests are **not operating-system hidden files**. They are rows `R016` through `R020` in `community_demo/requests.csv`. Their expected answers are omitted from the visible expected-output files so you can try them. Run the full dataset to display their results:

```powershell
python main.py --sources community_demo/sources.csv --rates community_demo/rates.csv --requests community_demo/requests.csv --friendly
```

See `community_demo/README.md` for the data columns, output meaning, and compact report option. `expected_visible_output.txt` is the compact output; `friendly_expected_output.txt` shows full source names with labeled values.

## Project files

- `main.py` — CLI entry point for the CSV-based engine.
- `ewaste_engine/` — data models, input validation, rule calculations, scheduling, and reports.
- `demo_data/` — inputs for the original small demo.
- `community_demo/` — larger proposed community collection demo and visible expected output.
- `docs/DESIGN.md` — numbered business rules, data model, flow, and unresolved decisions.
- `tests/test_engine.py` — seven rule-level checks for the modular demo engine.
- `Documents and Learning/` — teammate-friendly Word learning brief and the script that builds it.

## What to confirm before building the official version

1. Ask whether residential hubs may be represented as `HOUSEHOLD` sources and how credits should be issued for pooled household contributions.
2. Confirm the instructor's source, rate-card, request files, expected output format, rounding convention, and distance-rounding interpretation.
3. Confirm how a whole request above a daily weight or hazard limit should be handled; the demos refuse such requests with explanatory reasons.
4. Continue learning the code and keep a decision log before treating any demo code as submitted work.

## Update GitHub after local changes

From PowerShell in the project folder:

```powershell
git status
git add .
git status
git commit -m "Describe the update"
git push
```

Review the second `git status` before committing. Replace the example commit message with a short description of what changed.
