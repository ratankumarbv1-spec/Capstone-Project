import unittest

from ewaste_engine.engine import process
from ewaste_engine.models import ItemLine, PickupRequest, Rate, Source, VehicleDay
from ewaste_engine.rules import calculate
from ewaste_engine.scheduler import assign, record


RATES = {
    "IT": Rate("IT", 100, False),
    "BATTERY": Rate("BATTERY", 20, True),
    "CRT": Rate("CRT", 10, True),
}


def pickup(request_id, source_id, category, weight, count=1):
    return PickupRequest(request_id, source_id, (ItemLine(category, count, weight),))


class BusinessRuleTests(unittest.TestCase):
    def test_household_hazard_is_deducted_but_bulk_gets_rate_credit(self):
        request = pickup("R1", "H", "BATTERY", 2)
        household = calculate(request, Source("H", "HOUSEHOLD", 0), RATES)
        bulk = calculate(request, Source("B", "BULK", 0), RATES)
        self.assertEqual((household.category_credit, household.handling_deduction), (0, 30))
        self.assertEqual((bulk.category_credit, bulk.handling_deduction), (40, 0))

    def test_exactly_10_km_is_free_and_beyond_rounds_distance_up(self):
        request = pickup("R1", "B", "IT", 1)
        self.assertEqual(calculate(request, Source("B", "BULK", 10), RATES).pickup_charge, 0)
        self.assertEqual(calculate(request, Source("B", "BULK", 10.1), RATES).pickup_charge, 12)

    def test_200_kg_pickup_charge_is_waived(self):
        request = pickup("R1", "B", "IT", 200)
        result = calculate(request, Source("B", "BULK", 100), RATES)
        self.assertEqual(result.pickup_charge, 0)

    def test_household_five_kg_meets_minimum_and_four_is_refused(self):
        sources = {"H": Source("H", "HOUSEHOLD", 0)}
        requests = [pickup("R4", "H", "IT", 4), pickup("R5", "H", "IT", 5)]
        results, _ = process(requests, sources, RATES)
        self.assertEqual([r.reason for r in results], ["BELOW_MINIMUM", None])
        self.assertEqual([r.accepted for r in results], [False, True])

    def test_day_checks_stop_weight_and_hazard_limits_together(self):
        requests = [pickup(f"R{i}", "B", "IT", 1) for i in range(7)]
        day = VehicleDay(1, requests, total_weight_kg=1150, hazardous_weight_kg=0)
        too_heavy = pickup("R8", "B", "IT", 51)
        self.assertEqual(assign(too_heavy, RATES, [day]), (2, None))
        day2 = VehicleDay(1, requests[:7], total_weight_kg=1, hazardous_weight_kg=290)
        hazardous = pickup("RH", "B", "BATTERY", 11)
        self.assertEqual(assign(hazardous, RATES, [day2]), (2, None))

    def test_350_kg_battery_request_cannot_fit_any_day(self):
        request = pickup("R1", "B", "BATTERY", 350)
        self.assertEqual(assign(request, RATES, []), (None, "EXCEEDS_DAILY_HAZARD_LIMIT"))

    def test_certificate_uses_monthly_accepted_weight(self):
        from ewaste_engine.reports import render
        requests = [pickup("R1", "B", "IT", 250), pickup("R2", "B", "IT", 250)]
        results, days = process(requests, {"B": Source("B", "BULK", 0)}, RATES)
        self.assertIn("B | 500 kg | RECYCLING_CERTIFICATE", render(results, days))


if __name__ == "__main__":
    unittest.main()
