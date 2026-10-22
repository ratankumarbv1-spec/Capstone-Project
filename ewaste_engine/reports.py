from .models import PickupResult, VehicleDay


def render(results: list[PickupResult], days: list[VehicleDay]) -> str:
    lines = ["CREDIT NOTES"]
    for result in results:
        request = result.request
        if not result.accepted:
            lines.append(f"{request.request_id} | {request.source_id} | REFUSED: {result.reason}")
            continue
        calc = result.calculation
        status = f"AMOUNT_PAYABLE Rs {abs(calc.net_rupees)}" if calc.net_rupees < 0 else f"CREDIT Rs {calc.net_rupees}"
        lines.append(
            f"{request.request_id} | {request.source_id} | {request.total_weight_kg:g} kg | "
            f"credits Rs {calc.category_credit:.2f} - deductions Rs {calc.handling_deduction:.2f} "
            f"- pickup Rs {calc.pickup_charge:.2f} = {status} | DAY {result.day_number}"
        )

    lines.extend(["", "PICKUP SCHEDULE"])
    for result in results:
        state = f"DAY {result.day_number} | ACCEPTED" if result.accepted else f"REFUSED | {result.reason}"
        lines.append(f"{result.request.request_id} | {result.request.source_id} | {state}")

    lines.extend(["", "VEHICLE DAYS"])
    for day in days:
        lines.append(
            f"DAY {day.day_number} | {len(day.requests)} stops | {day.total_weight_kg:g}/1200 kg | "
            f"{day.hazardous_weight_kg:g}/300 kg hazardous"
        )

    collected: dict[str, float] = {}
    for result in results:
        if result.accepted:
            sid = result.request.source_id
            collected[sid] = collected.get(sid, 0) + result.request.total_weight_kg
    lines.extend(["", "MONTHLY SUMMARY"])
    lines.append(f"Accepted pickups: {sum(r.accepted for r in results)}")
    lines.append(f"Refused pickups: {sum(not r.accepted for r in results)}")
    for source_id in sorted(collected):
        if collected[source_id] >= 500:
            lines.append(f"{source_id} | {collected[source_id]:g} kg | RECYCLING_CERTIFICATE")
    return "\n".join(lines)


def render_friendly(results: list[PickupResult], days: list[VehicleDay], sources) -> str:
    """Expanded report for learners: full source names and one labeled value per line."""
    def point_name(source_id: str) -> str:
        source = sources[source_id]
        area = f" ({source.area_id.replace('_', ' ').replace('-', ' ').title()})" if source.area_id else ""
        name = source.source_name or source_id
        return f"{name}{area} [{source_id}]"

    lines = ["CREDIT NOTES", "=" * 72]
    for result in results:
        request = result.request
        lines.extend([f"Request number: {request.request_id}", f"Pickup point: {point_name(request.source_id)}"])
        if not result.accepted:
            lines.append(f"Result: REFUSED - {result.reason.replace('_', ' ').lower()}")
        else:
            calc = result.calculation
            if calc.net_rupees < 0:
                net_text = f"Rs {abs(calc.net_rupees)} payable by the source"
            else:
                net_text = f"Rs {calc.net_rupees} credit to the source"
            lines.extend([
                f"Total collected weight: {request.total_weight_kg:g} kg",
                f"Category credit: Rs {calc.category_credit:.2f}",
                f"Household hazardous-item deduction: Rs {calc.handling_deduction:.2f}",
                f"Pickup charge: Rs {calc.pickup_charge:.2f}",
                f"Net result: {net_text}",
                f"Scheduled vehicle day: Day {result.day_number}",
            ])
        lines.append("-" * 72)

    lines.extend(["", "PICKUP SCHEDULE", "=" * 72])
    for result in results:
        state = f"Day {result.day_number}" if result.accepted else f"Refused - {result.reason.replace('_', ' ').lower()}"
        lines.append(f"Request {result.request.request_id} | {point_name(result.request.source_id)} | {state}")

    lines.extend(["", "VEHICLE DAY TOTALS", "=" * 72])
    for day in days:
        stop_word = "stop" if len(day.requests) == 1 else "stops"
        lines.append(
            f"Day {day.day_number}: {len(day.requests)} {stop_word}; "
            f"{day.total_weight_kg:g} of 1,200 kg total capacity; "
            f"{day.hazardous_weight_kg:g} of 300 kg hazardous capacity"
        )

    collected: dict[str, float] = {}
    for result in results:
        if result.accepted:
            sid = result.request.source_id
            collected[sid] = collected.get(sid, 0) + result.request.total_weight_kg
    lines.extend(["", "MONTHLY SUMMARY", "=" * 72])
    lines.append(f"Accepted requests: {sum(r.accepted for r in results)}")
    lines.append(f"Refused requests: {sum(not r.accepted for r in results)}")
    for source_id in sorted(collected):
        if collected[source_id] >= 500:
            lines.append(f"RECYCLING_CERTIFICATE: {point_name(source_id)} collected {collected[source_id]:g} kg")
    return "\n".join(lines)
