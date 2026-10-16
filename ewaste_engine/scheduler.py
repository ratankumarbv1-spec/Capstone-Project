from .models import PickupRequest, VehicleDay
from .rules import hazardous_weight


MAX_WEIGHT_KG = 1200.0
MAX_STOPS = 8
MAX_HAZARDOUS_KG = 300.0


def assign(request: PickupRequest, rates, days: list[VehicleDay]) -> tuple[int | None, str | None]:
    hazard = hazardous_weight(request, rates)
    # These requests cannot ever fit an empty day if requests remain indivisible.
    if request.total_weight_kg > MAX_WEIGHT_KG:
        return None, "EXCEEDS_DAILY_WEIGHT_LIMIT"
    if hazard > MAX_HAZARDOUS_KG:
        return None, "EXCEEDS_DAILY_HAZARD_LIMIT"

    for day in days:
        fits = (
            len(day.requests) < MAX_STOPS
            and day.total_weight_kg + request.total_weight_kg <= MAX_WEIGHT_KG
            and day.hazardous_weight_kg + hazard <= MAX_HAZARDOUS_KG
        )
        if fits:
            return day.day_number, None

    next_day = VehicleDay(len(days) + 1)
    days.append(next_day)
    return next_day.day_number, None


def record(day: VehicleDay, request: PickupRequest, rates) -> None:
    day.requests.append(request)
    day.total_weight_kg += request.total_weight_kg
    day.hazardous_weight_kg += hazardous_weight(request, rates)
