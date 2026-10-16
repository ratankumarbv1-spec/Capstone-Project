import argparse
from pathlib import Path

from ewaste_engine.engine import process
from ewaste_engine.inputs import InputError, load_rates, load_requests, load_sources
from ewaste_engine.reports import render


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process e-waste pickup requests and print recycler reports.")
    parser.add_argument("--sources", type=Path, required=True, help="CSV containing source_id,type,distance_km")
    parser.add_argument("--rates", type=Path, required=True, help="CSV containing category,credit_per_kg,hazardous")
    parser.add_argument("--requests", type=Path, required=True, help="CSV containing request_id,source_id,items")
    parser.add_argument("--output", type=Path, help="Optional path to save the report (also prints it)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        sources = load_sources(args.sources)
        rates = load_rates(args.rates)
        requests = load_requests(args.requests, rates, sources)
        results, days = process(requests, sources, rates)
        report = render(results, days)
        print(report)
        if args.output:
            args.output.write_text(report + "\n", encoding="utf-8")
    except (InputError, OSError) as exc:
        print(f"Input/output error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
