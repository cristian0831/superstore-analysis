# Superstore Analysis

End-to-end analysis of four years of orders (2014–2017) from a US office-supplies retailer: what drives profit, how demand will move over the next six months, and what the business should do about both.

**Tools:** SQL (SQLite) · Python · Pandas · statsmodels · scikit-learn · Matplotlib · Power BI · pytest

One ETL builds a SQLite star schema that every analysis reads from. The analysis is split into three independent tracks:

| Track | Question | Status | Details |
|---|---|---|---|
| **Business diagnostics** | Which products, regions and customer segments make or lose money? | Done | [reports/diagnostics.md](reports/diagnostics.md) |
| **Demand forecasting** | How much will each category sell in the next six months? | Holt-Winters validated; SARIMA next | [reports/forecasting.md](reports/forecasting.md) |
| **Regression** | Which factors drive profit on an order line? | Planned | — |

## Headline results

### Business diagnostics

- **Discounts above ~20% destroy margin.** Furniture turns loss-making from the 21–30% discount band; no category is profitable above 40%.
- **Furniture sells but barely profits:** its margin fell to 1.4% in 2017 while sales kept growing.
- **Five states offset profit made elsewhere.** Texas alone lost \$25.7K; Ohio, Pennsylvania, Illinois and North Carolina are also net-negative.

### Demand forecasting

WAPE on the 12 holdout months (Jan–Dec 2017), lower is better:

| Series | Seasonal naive (benchmark) | Holt-Winters |
|---|---|---|
| Total | 25.3% | **22.5%** |
| Furniture | **20.9%** | 23.8% |
| Office Supplies | 35.9% | **29.2%** |
| Technology | 34.6% | **33.5%** |

- **Holt-Winters beats the benchmark on 3 of 4 series.**
- **All forecasts are too low.** Sales grew 20.4% in 2017 and Holt-Winters under-forecast the year by 20.0%, which is the main problem for the next models to solve.

![Holdout forecasts against actual 2017 sales](outputs/forecasting/figures/06_holdout_forecasts.png)

## Roadmap

- [x] ETL: raw CSV → cleaned, validated SQLite star schema
- [x] Business diagnostics: growth, category, segment, discount and regional profitability
- [x] Forecasting: monthly series, trend and seasonality analysis, baselines, Holt-Winters
- [ ] Forecasting: SARIMA (Prophet as an option), six-month forecast with confidence intervals
- [ ] Regression: profit drivers (discount vs profit, category margins, shipping patterns), model, feature importance and interpretation
- [ ] Power BI dashboard: KPI overview, regional map, category drill-down
- [ ] Business recommendations combining all three tracks

## Project structure

```
├── data/raw/superstore.csv      Source data (see docs/dataset.md)
├── db/                          SQLite database, built by the ETL (git-ignored)
├── sql/
│   ├── etl/                     Star schema
│   ├── diagnostics/             Business diagnostics queries
│   └── forecasting/             Monthly sales series
├── src/
│   ├── config.py                Paths, tracks and the forecast holdout length
│   ├── etl.py                   Extract → clean → enrich → validate → load
│   ├── db_utils.py              SQLite connection and query helper
│   ├── sql_runner.py            Runs a track's queries and saves the results as CSV
│   ├── plotting.py              Shared chart style
│   └── forecasting/             Series loading, baselines, MAPE and WAPE
├── notebooks/
│   ├── 01_etl_superstore.ipynb  The ETL step by step
│   ├── forecasting/             Exploration and holdout validation
│   └── regression/
├── outputs/                     Generated tables and figures, one folder per track
├── reports/                     Conclusions, one document per track
├── dashboards/                  Power BI
├── docs/                        Dataset description, ER diagram
└── tests/                       pytest suite, run in CI on every push
```

## How to run

Requires Python 3.9+.

```bash
# 1. Create an environment and install the dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e .                       # add ".[prophet]" for the optional Prophet model

# 2. Build the SQLite database from the raw CSV
python -m src.etl

# 3. Run the SQL queries of every track (or name one: diagnostics, forecasting)
python -m src.sql_runner

# 4. Run the tests
pytest
```

Then open the notebooks in Jupyter or VS Code with the `.venv` kernel.
