# Community Collection Demo

This is a learning-only example of the proposed shared neighborhood collection-point idea. It is separate from the earlier demo and is not the official capstone dataset or submission.

## What is in this demo

- 15 sources: 9 household-type shared collection points across 3 residential areas, plus 6 BULK sources (school, college, factory, office, and 2 repair shops).
- 20 pickup requests in one illustrative month. `requests_visible.csv` contains R001-R015 with a visible expected report. `requests.csv` contains all 20; R016-R020 are holdout practice requests whose expected results are omitted from both visible expected-output files.
- A 5-category rate card using the same placeholder values as the original demo. These are not verified real rates.
- Several boundary examples: household exactly 5 kg, exactly 10 km, exactly 200 kg, a day at 7 stops and 1,150 kg before the next request, below-minimum household request, a 350 kg all-battery request, and a request above the 1,200 kg limit.

The household collection points aggregate contributions from several nearby homes before they become a pickup request. Their combined weight is what the engine checks against the 5 kg household minimum. A shared point counts as one source and one vehicle stop. This demonstrates a possible operating model; confirm with the instructor that a neighborhood collection point can be registered as a HOUSEHOLD source.

`homes_in_area` and `homes_covered` are descriptive columns added to `sources.csv`; `month` and `contributing_homes` are descriptive columns added to the requests. The existing loader ignores these extra columns and processes the required fields. Item lines use `CATEGORY:COUNT:TOTAL_WEIGHT_KG`.

## Run the visible 15-request report

From the project root:

```powershell
python main.py --sources community_demo/sources.csv --rates community_demo/rates.csv --requests community_demo/requests_visible.csv
```

Compare the output with `expected_visible_output.txt`.

To show full pickup-point names, add the `--friendly` option:

```powershell
python main.py --sources community_demo/sources.csv --rates community_demo/rates.csv --requests community_demo/requests_visible.csv --friendly
```

Command parts:

- `python` starts the Python interpreter.
- `main.py` is the program's command-line entry point.
- `--sources` tells it where the source-list CSV is.
- `--rates` tells it where the category rate-card CSV is.
- `--requests` tells it which pickup-request CSV to process.
- `--friendly` displays full collection-point names and labels each amount.

The pipe characters in the compact report separate fields. In friendly mode, each field is written on its own labeled line. “Vehicle day” means the numbered scheduling day, not a calendar date. “Category credit” is the rate-card amount; the household handling deduction and pickup charge are subtracted to get the net result. A positive net is a credit to the source; a negative net is an amount payable by the source.

## Run all 20 requests

```powershell
python main.py --sources community_demo/sources.csv --rates community_demo/rates.csv --requests community_demo/requests.csv
```

The full run prints results for the five holdout requests so you can try them yourself. Their expected results are intentionally omitted from the visible expected-output file.

### What “hidden” means here

The holdout requests are not hidden from Windows, the file explorer, or GitHub. They are the last five rows (`R016`-`R020`) of `requests.csv`. Only their expected answers are withheld from the visible answer file. To see the calculated results, run the full 20-request command above. `requests_visible.csv` is a convenience file containing only the first 15 requests, so you can compare that run with the answer key without the holdout rows appearing in the report.

For a more readable console report with actual pickup-point names and one labeled value per line, use the same visible command with `--friendly`. `friendly_expected_output.txt` contains that expanded report. The default compact report uses pipe separators (`|`) to separate fields; the friendly report spells out labels such as “Category credit,” “Pickup charge,” and “Scheduled vehicle day.”

## Assumptions to verify

- All weights and rates are synthetic for demonstrating program behavior; they are not measured local data.
- The sample assumes a number of nearby homes contribute a combined 5 kg or more at a shared point. The per-home 1-3 kg idea is not treated as a validated generation rate.
- Pickup charge is still based on distance from depot to the registered pickup point, not distance between the contributing homes.
- Whole requests are not split across days. Requests above 1,200 kg or above 300 kg hazardous are refused by the demo with an explanatory reason.
- The rule that requests are processed in file order is preserved. The first seven visible requests total exactly 1,150 kg across 7 stops; the next 60 kg request must move to the next day because it would exceed 1,200 kg.
