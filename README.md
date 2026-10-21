# Superstore Demand Forecasting

Monthly sales forecasting for a US office-supplies retailer, in total and for each product category (Furniture, Office Supplies, Technology). The aim is to tell the business which categories and months need more inventory over the next six months.

**Tools:** Python · SQL (SQLite) · Pandas · statsmodels · Matplotlib · pytest

## Results so far

The models are scored on 2017, which none of them saw during fitting. They were fitted on 2014–2016. WAPE (total error ÷ total sales) is the headline metric, because it weights each month by its sales, and the big months are where inventory money is.

| Series | Naive | Seasonal naive (benchmark) | Holt-Winters |
|---|---|---|---|
| Total | 64.6% | 25.3% | **22.5%** |
| Furniture | 104.7% | **20.9%** | 23.8% |
| Office Supplies | 85.3% | 35.9% | **29.2%** |
| Technology | 38.9% | 34.6% | **33.5%** |

*WAPE on the 12 holdout months (Jan–Dec 2017). Lower is better; bold marks the best forecast per series. MAPE is reported alongside WAPE in [notebook 03](notebooks/03_validation_baselines_holt_winters.ipynb).*

- **Holt-Winters beats the seasonal naive benchmark on 3 of 4 series.** The gain on Technology is marginal, and on Furniture the benchmark wins.
- **Every forecast is too low.** Sales grew 20.4% in 2017, and Holt-Winters under-forecast the year by 20.0%. The training years included a flat 2015, so the model selection (AICc) treated growth as noise and chose no trend. Fixing this bias is the main open problem for the next models.

![Holdout forecasts against actual 2017 sales](outputs/phase4_validation/figures/01_holdout_forecasts.png)

## What the data shows

From the exploration of the 36 training months, Jan 2014 → Dec 2016 ([notebook 02](notebooks/02_eda_trend_seasonality.ipynb)):

1. **Seasonality is the main signal.** September, November and December sell 1.6–2.1× an average month; January and February only 0.2–0.6×.
2. **The seasonal shape is the same in all three categories.** All peak in Sep / Nov / Dec and bottom out in Jan / Feb, so one model family can serve every series.
3. **Month-to-month memory is weak.** The correlation with the previous month is 0.12–0.23, within noise. That is why the naive forecast fails and the seasonal naive forecast is the benchmark to beat.
4. **The trend is weak and uneven.** Total sales fell 2.8% in 2015 and rose 29.5% in 2016, too few data points to trust a straight-line trend.
5. **Furniture is the most predictable category; Technology the least.** Residual noise is 18% of mean sales for Furniture, 34% for Office Supplies and 37% for Technology, which sets a floor on achievable error.
6. **Additive vs multiplicative seasonality is not settled by inspection.** Total behaves additively, Furniture multiplicatively; the models test both.
7. **Stationarity tests disagree on differencing** (ADF vs KPSS, with only 36 months). SARIMA orders will be chosen from a small grid by AICc rather than fixed from the tests.

![Seasonal index by series and month](outputs/phase3_eda/figures/03_seasonal_index.png)

## Approach

| Phase | What it does | Where |
|---|---|---|
| 1. ETL | Load the raw CSV, clean, validate, and load a star schema into SQLite | [01_etl_superstore.ipynb](notebooks/01_etl_superstore.ipynb) |
| 2. Data preparation | SQL queries that build the monthly series, total and by category | [scripts/phase2_data_preparation/](scripts/phase2_data_preparation/) |
| 3. Exploration | Trend, seasonality, decomposition and stationarity checks on the training months | [02_eda_trend_seasonality.ipynb](notebooks/02_eda_trend_seasonality.ipynb) |
| 4. Validation | Naive, seasonal naive and Holt-Winters scored on a 12-month holdout | [03_validation_baselines_holt_winters.ipynb](notebooks/03_validation_baselines_holt_winters.ipynb) |

**Validation design:** the last 12 months (2017) are held out. A 12-month holdout tests every calendar month once, including the year-end peak. Every modelling decision — the exploration, the choice of Holt-Winters variant — uses the 36 training months only, so the holdout error is an honest estimate of future error.

## Roadmap

- [x] Monthly series, total and by category, with trend and seasonality charts
- [x] Baselines: naive and seasonal naive
- [x] Holt-Winters, validated with MAPE and WAPE on a 12-month holdout
- [ ] SARIMA (Prophet as an option)
- [ ] Six-month forecast (Jan–Jun 2018) with confidence intervals
- [ ] Business conclusions: which categories and months need more inventory

## Project structure

```
├── data/raw/superstore.csv            Source data: 9,994 order lines, 2014–2017
├── notebooks/                         ETL, exploration and validation notebooks
├── scripts/phase2_data_preparation/   SQL queries and the script that runs them
├── src/
│   ├── config.py                      Paths and the holdout length
│   ├── db_utils.py                    SQLite connection and query helper
│   ├── series.py                      Loads the monthly series; train/holdout split
│   ├── baselines.py                   Naive and seasonal naive forecasts
│   ├── metrics.py                     MAPE and WAPE
│   └── plotting.py                    Shared chart style
├── tests/                             pytest suite
└── outputs/                           Generated tables and figures
```

## How to run

Requires Python 3.9+.

```bash
# 1. Create an environment and install the dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e .                 # add ".[prophet]" for the optional Prophet model

# 2. Build the SQLite database from the raw CSV
jupyter nbconvert --to notebook --execute --inplace notebooks/01_etl_superstore.ipynb

# 3. Build the monthly series
python -m scripts.phase2_data_preparation.run_phase

# 4. Run the tests
pytest
```

Then open notebooks 02 and 03 in Jupyter or VS Code, using the `.venv` kernel.
