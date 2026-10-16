"""Small teaching prototype for the E-waste Collection and Credit Engine.

Run from this folder with: python prototype.py
The demo reads CSV files from demo_data/ and prints three reports.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path


DATA_DIR = Path(__file__).parent / "demo_data"


@dataclass
class Source:
    source_id: str
    source_type: str
    distance_km: float


@dataclass
class Pickup:
    request_id: str
    source_id: str
    items: list[tuple[str, int, float]]  # category, count, total line weight

    @property
    def total_weight(self) -> float:
        return sum(weight for _, _, weight in self.items)


@dataclass
class VehicleDay:
    day_number: int
    pickups: list[Pickup] = field(default_factory=list)
    total_weight: float = 0
    hazardous_weight: float = 0


def load_sources() -> dict[str, Source]:
    with (DATA_DIR / "sources.csv").open(newline="", encoding="utf-8") as f:
        return {
            row["source_id"]: Source(row["source_id"], row["type"], float(row["distance_km"]))
            for row in csv.DictReader(f)
        }


def load_rates() -> dict[str, tuple[float, bool]]:
    with (DATA_DIR / "rates.csv").open(newline="", encoding="utf-8") as f:
        return {
            row["category"]: (float(row["credit_per_kg"]), row["hazardous"].lower() == "true")
            for row in csv.DictReader(f)
        }


def load_pickups() -> list[Pickup]:
    pickups = []
    with (DATA_DIR / "requests.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            items = []
            for token in row["items"].split(";"):
                category, count, weight = token.split(":")
                items.append((category, int(count), float(weight)))
            pickups.append(Pickup(row["request_id"], row["source_id"], items))
    return pickups


def calculate(pickup: Pickup, source: Source, rates: dict[str, tuple[float, bool]]) -> tuple[float, float, float, float]:
    credits = deductions = hazard_weight = 0.0
    for category, _count, weight in pickup.items:
        rate, hazardous = rates[category]
        if hazardous:
            hazard_weight += weight
        if source.source_type == "HOUSEHOLD" and category in {"BATTERY", "CRT"}:
            deductions += weight * 15
        else:
            credits += weight * rate

    # Charge Rs 12 per whole km beyond the free first 10 km.
    extra_km = max(0, math.ceil(source.distance_km) - 10)
    charge = 0 if pickup.total_weight >= 200 else extra_km * 12
    net = round(credits - deductions - charge)
    return credits, deductions, charge, net


def schedule_pickup(pickup: Pickup, hazard_weight: float, days: list[VehicleDay]) -> VehicleDay | None:
    # Find earliest day where stop, total-weight AND hazard limits all fit.
    # If a single request is too hazardous to fit on an empty day, this demo
    # explicitly refuses it instead of searching forever.
    if hazard_weight > 300:
        return None
    for day in days:
        if (len(day.pickups) < 8
                and day.total_weight + pickup.total_weight <= 1200
                and day.hazardous_weight + hazard_weight <= 300):
            return day
    day = VehicleDay(len(days) + 1)
    days.append(day)
    return day


def main() -> None:
    sources, rates, pickups = load_sources(), load_rates(), load_pickups()
    days: list[VehicleDay] = []
    notes = []
    collected_by_source: dict[str, float] = {source_id: 0 for source_id in sources}
    schedule_rows = []

    for pickup in pickups:
        source = sources[pickup.source_id]
        if source.source_type == "HOUSEHOLD" and pickup.total_weight < 5:
            notes.append((pickup, "REFUSED: BELOW_MINIMUM", 0))
            schedule_rows.append((pickup.request_id, pickup.source_id, "REFUSED", "BELOW_MINIMUM"))
            continue

        credits, deductions, charge, net = calculate(pickup, source, rates)
        hazard_weight = sum(weight for category, _, weight in pickup.items if rates[category][1])
        day = schedule_pickup(pickup, hazard_weight, days)
        if day is None:
            notes.append((pickup, "REFUSED: EXCEEDS_DAILY_HAZARD_LIMIT", net))
            schedule_rows.append((pickup.request_id, pickup.source_id, "REFUSED", "EXCEEDS_DAILY_HAZARD_LIMIT"))
            continue

        day.pickups.append(pickup)
        day.total_weight += pickup.total_weight
        day.hazardous_weight += hazard_weight
        collected_by_source[pickup.source_id] += pickup.total_weight
        status = f"AMOUNT_PAYABLE Rs {abs(net)}" if net < 0 else f"CREDIT Rs {net}"
        notes.append((pickup, status, net, credits, deductions, charge, day.day_number))
        schedule_rows.append((pickup.request_id, pickup.source_id, f"DAY {day.day_number}", "ACCEPTED"))

    print("CREDIT NOTES")
    for note in notes:
        pickup, status, _ = note[:3]
        if status.startswith("REFUSED"):
            print(f"{pickup.request_id} | {pickup.source_id} | {status}")
        else:
            _, _, _, credits, deductions, charge, day_number = note
            print(f"{pickup.request_id} | {pickup.source_id} | {pickup.total_weight:g} kg | "
                  f"credits Rs {credits:.2f} - deductions Rs {deductions:.2f} "
                  f"- pickup Rs {charge:.2f} = {status} | DAY {day_number}")

    print("\nPICKUP SCHEDULE")
    for request_id, source_id, day, status in schedule_rows:
        print(f"{request_id} | {source_id} | {day} | {status}")
    print("\nVEHICLE DAYS")
    for day in days:
        print(f"DAY {day.day_number} | {len(day.pickups)} stops | {day.total_weight:g}/1200 kg | "
              f"{day.hazardous_weight:g}/300 kg hazardous")

    print("\nMONTHLY SUMMARY")
    print(f"Accepted pickups: {sum(len(day.pickups) for day in days)}")
    print(f"Refused pickups: {sum(1 for row in schedule_rows if row[2] == 'REFUSED')}")
    for source_id, weight in collected_by_source.items():
        if weight >= 500:
            print(f"{source_id} | {weight:g} kg | RECYCLING_CERTIFICATE")


if __name__ == "__main__":
    main()
