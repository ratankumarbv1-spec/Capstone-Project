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
