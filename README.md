# E-Waste Collection and Recycling Credit Engine

A Python 3.10+ command-line program for an authorised recycler. It reads source, rate-card, and pickup-request CSV files, applies the capstone business rules, schedules accepted pickups into vehicle days, and prints credit notes, a pickup schedule, and a monthly summary.

The assignment explicitly calls for a command-file-driven program with no UI, so this project is a CLI application. A web front end is not needed for the required evaluation.

## Run

```powershell
python main.py --sources demo_data/sources.csv --rates demo_data/rates.csv --requests demo_data/requests.csv
```

Run `python main.py --help` for options. Input file formats and rule decisions are described in [docs/DESIGN.md](docs/DESIGN.md).

## Project layout

- `main.py` — command-line entry point
- `ewaste_engine/` — file loading, calculations, scheduling, and reports
- `demo_data/` — small sample input set
- `docs/DESIGN.md` — numbered business rules, data model, flow, and decisions
- `tests/` — automated rule-level checks

The included data is illustrative. Replace it with the instructor-provided files when they arrive, and adjust report formatting to match the visible expected output exactly.
