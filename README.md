# NYC Taxi Demand Forecasting

[![CI](https://github.com/ccccarloswd/nyc-taxi-demand/actions/workflows/ci.yml/badge.svg)](https://github.com/ccccarloswd/nyc-taxi-demand/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Status](https://img.shields.io/badge/status-in%20progress-orange)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> 🚧 **Work in progress.** This project is being built in public, phase by phase.
> The roadmap below shows what is done and what comes next.

End-to-end pipeline that forecasts **hourly trip demand for each of NYC's 263 taxi zones**,
using several years of public [NYC TLC trip records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
(yellow taxis and Uber/Lyft, hundreds of millions of trips).

The goal is not only a good model, but a project built the way production data teams work:
a layered data lake, data-quality checks, leakage-free time-series validation, tracked
experiments, tests, CI and a deployed API and dashboard.

## Roadmap

- [x] **Phase 0 – Foundations:** project layout, tooling (uv, ruff, mypy, pytest), pre-commit, CI
- [ ] **Phase 1 – Ingestion (bronze):** incremental, idempotent download of raw TLC Parquet files
- [ ] **Phase 2 – Cleaning & data quality (silver):** validation rules, quality report, tests
- [ ] **Phase 3 – Aggregation & EDA (gold):** zone × hour demand table, exploratory analysis, Spark vs DuckDB benchmark
- [ ] **Phase 4 – Baselines & validation:** seasonal baselines, rolling-origin backtesting, WAPE / MASE
- [ ] **Phase 5 – Modelling:** LightGBM global model, weather & calendar features, MLflow, error analysis, prediction intervals
- [ ] **Phase 6 – Serving:** FastAPI service, Streamlit dashboard, Docker, public demo
- [ ] **Phase 7 – Extension:** causal impact of NYC congestion pricing (Jan 2025) on taxi vs ride-hailing demand

## Planned architecture

```text
TLC Parquet files ──► bronze (raw, as downloaded)
                        │  PySpark: schema enforcement, quality rules
                        ▼
                      silver (clean trips)
                        │  PySpark: zone × hour aggregation
                        ▼
                      gold (demand table) + weather + holidays
                        │
                        ▼
              features ──► models (baselines, LightGBM) ──► MLflow
                                       │
                                       ▼
                              FastAPI  +  Streamlit
```

## Tech stack

| Area | Tools |
|---|---|
| Processing | PySpark, DuckDB (benchmark) |
| Modelling | LightGBM, scikit-learn, MLflow |
| Serving | FastAPI, Streamlit, Docker |
| Quality | pytest, ruff, mypy, pre-commit, GitHub Actions |
| Environment | uv, Python 3.12, Java 17 |

## Getting started

Requirements: Linux, macOS or WSL2, [uv](https://docs.astral.sh/uv/) and Java 17.

```bash
git clone https://github.com/ccccarloswd/nyc-taxi-demand.git
cd nyc-taxi-demand
make install   # create the virtual env and install git hooks
make check     # lint + type check + tests
```

Run `make help` to see every available command.

## Project structure

```text
├── src/nyc_taxi/        # installable Python package (pipeline + models)
├── tests/               # unit tests
├── docs/decisions/      # architecture decision records (ADRs)
├── .github/workflows/   # CI pipeline
├── pyproject.toml       # dependencies and tool configuration
└── Makefile             # common commands
```

`data/` is created locally by the pipeline and is never committed.

## Design decisions

Key technical choices and their trade-offs are documented in [`docs/decisions/`](docs/decisions/).

## License

[MIT](LICENSE)
