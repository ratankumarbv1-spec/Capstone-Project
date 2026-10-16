from .models import PickupResult, VehicleDay
from .rules import calculate
from .scheduler import assign, record


MIN_HOUSEHOLD_KG = 5.0


def process(requests, sources, rates) -> tuple[list[PickupResult], list[VehicleDay]]:
    results = []
    days: list[VehicleDay] = []
    for request in requests:
        source = sources[request.source_id]
        if source.source_type == "HOUSEHOLD" and request.total_weight_kg < MIN_HOUSEHOLD_KG:
            results.append(PickupResult(request, False, "BELOW_MINIMUM"))
            continue
        calculation = calculate(request, source, rates)
        day_number, reason = assign(request, rates, days)
        if reason:
            results.append(PickupResult(request, False, reason, calculation))
            continue
        day = days[day_number - 1]
        record(day, request, rates)
        results.append(PickupResult(request, True, calculation=calculation, day_number=day_number))
    return results, days
