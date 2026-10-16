import math

from .models import Calculation, PickupRequest, Rate, Source


HOUSEHOLD_HAZARDOUS_CATEGORIES = {"BATTERY", "CRT"}


def hazardous_weight(request: PickupRequest, rates: dict[str, Rate]) -> float:
    return sum(item.weight_kg for item in request.items if rates[item.category].hazardous)


def calculate(request: PickupRequest, source: Source, rates: dict[str, Rate]) -> Calculation:
    credits = 0.0
    deductions = 0.0
    for item in request.items:
        if source.source_type == "HOUSEHOLD" and item.category in HOUSEHOLD_HAZARDOUS_CATEGORIES:
            deductions += item.weight_kg * 15
        else:
            credits += item.weight_kg * rates[item.category].credit_per_kg

    chargeable_km = max(0, math.ceil(source.distance_km) - 10)
    charge = 0 if request.total_weight_kg >= 200 else chargeable_km * 12
    # Python's round uses ties-to-even, while business invoices normally use half-up.
    net = math.floor(credits - deductions - charge + 0.5)
    return Calculation(credits, deductions, charge, net)
