# Design: E-Waste Collection and Recycling Credit Engine

## Purpose

The engine records electronic waste pickup requests, calculates the credit or amount payable for each accepted pickup, assigns accepted pickups to vehicle days, and reports monthly collection totals. It is a command-line program driven by CSV files, as required by the brief.

## Business rules

- **BR-01 — Category credit:** For each item line, credit is line weight multiplied by the category rate.
- **BR-02 — Household hazardous handling:** For HOUSEHOLD sources, BATTERY and CRT receive a handling deduction of Rs 15 per kg instead of rate-card credit. BULK sources receive the rate-card credit for those categories.
- **BR-03 — Pickup charge:** Distance through 10 km is free. Beyond 10 km, charge Rs 12 per kilometre, rounding the source distance up to a whole kilometre before subtracting the free 10 km. Waive the charge when total pickup weight is at least 200 kg.
- **BR-04 — Household minimum:** Refuse HOUSEHOLD requests below 5 kg with `BELOW_MINIMUM`. Exactly 5 kg is accepted for scheduling. BULK requests have no minimum.
- **BR-05 — Vehicle day limits:** Each vehicle day holds at most 1,200 kg and 8 accepted pickup stops. Process in request-file order and choose the earliest day that fits.
- **BR-06 — Hazard limit:** Each vehicle day holds at most 300 kg of hazardous items, as defined by the rate card. A request must fit this limit as well as the total-weight and stop limits.
- **BR-07 — Net credit and payable:** Net = category credits - handling deductions - pickup charge. Round the final net to whole rupees. A negative net is reported as `AMOUNT_PAYABLE` by the source.
- **BR-08 — Monthly certificate:** A source with at least 500 kg collected during the month receives a `RECYCLING_CERTIFICATE` line.

## Data model

- `Source`: ID, type (`BULK` or `HOUSEHOLD`), and depot distance.
- `Rate`: category, credit per kg, and hazardous flag.
- `ItemLine`: category, count, and total line weight in kg.
- `PickupRequest`: request ID, source ID, and item lines; derived total and hazardous weights.
- `VehicleDay`: ordered accepted requests and accumulated total/hazardous weights.
- `PickupResult`: accepted/refused outcome, calculation breakdown, and assigned day when accepted.

Relationships: one source may have many pickup requests; each pickup has one source and one or more item lines; each accepted pickup belongs to exactly one vehicle day.

## Processing flow

1. Read and validate the three CSV files.
2. Process pickup requests in file order.
3. Calculate each request's total and hazardous weight.
4. Apply household minimum; refuse if below 5 kg.
5. Calculate category credit, deductions, pickup charge, and rounded net.
6. Scan vehicle days from earliest to latest. A day is eligible only if **all** limits fit after adding the whole request: stops <= 8, total kg <= 1,200, hazardous kg <= 300.
7. If none fits, create the next day if the request can fit an empty day. Otherwise refuse it as `EXCEEDS_DAILY_HAZARD_LIMIT` or `EXCEEDS_DAILY_WEIGHT_LIMIT`.
8. Print credit notes, schedule, vehicle-day totals, and monthly certificate lines.

## Decision log and assumptions

| Decision | Current choice | Reason / follow-up |
| --- | --- | --- |
| Interface | CLI, no UI | Explicitly required by the brief. |
| Input format | CSV | Easy to inspect, edit, and generate for command-file processing. Confirm instructor format when supplied. |
| Item weight | Weight is total for that category line | Brief says category, count, weight; this interpretation should be checked against Week 2 sample files. |
| Distance rounding | Round total distance up, then subtract 10 km | Example: 13.2 km becomes 14 km, so 4 chargeable km. Confirm if expected output interprets rounding differently. |
| Oversized request | Whole requests are not split; refuse if they cannot fit an empty day | 350 kg of batteries exceeds the daily 300 kg hazard cap, so advancing to another day cannot solve it. Confirm refusal behavior with instructor. |
| Monthly period | All requests in the supplied request file form one month | The current brief describes one month's input; add a date field if instructor data requires multiple months. |
| Output formatting | Human-readable deterministic text | Match the instructor's exact expected output once it is provided. |

## State flow

`RECEIVED -> REFUSED (BELOW_MINIMUM | CAPACITY_REASON)` or `RECEIVED -> ACCEPTED -> SCHEDULED(day)`.

Only accepted and scheduled pickups contribute to collected monthly weight and certificate eligibility.

## Shared neighborhood collection point proposal

Nearby households may contribute small amounts to a shared collection point. The point is registered as the household-type source and the pooled material becomes one pickup request. The engine applies the 5 kg minimum to that combined request; contributions are not submitted as separate sub-5 kg pickup requests. One shared point counts as one stop. Pickup distance is measured from the depot to the registered point, while the vehicle-day total and hazard limits are checked against the pooled load.

This is a proposed operating model for the learning demo, not a change to BR-04. Ask the instructor whether a shared point may be registered as a HOUSEHOLD source, and whether credit notes should go to the registered point or be divided among participating homes. Individual credit allocation is outside the current demo requirements.

## Learning status and holdout data

Files in this repository are practice materials, not the official submission. The community demo has 15 sources and 20 requests. Its five holdout requests are R016-R020 in `community_demo/requests.csv`; neither Windows hidden attributes nor Git ignore rules are used. The visible expected output covers R001-R015. Running the full request file displays all 20 calculated results, including the five practice cases.
