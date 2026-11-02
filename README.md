# NYC Taxi Demand Forecasting

[![CI](https://github.com/ccccarloswd/nyc-taxi-demand/actions/workflows/ci.yml/badge.svg)](https://github.com/ccccarloswd/nyc-taxi-demand/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

How many trips will start in Midtown at 6 pm next Friday? And in JFK on a rainy Sunday
morning? This project is about answering that kind of question: forecasting hourly trip
demand for each taxi zone in New York City.

The data comes from the [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page),
which publishes every yellow taxi, green taxi and Uber/Lyft trip in the city, month by month.
Put together it's well over a billion rows, which is the main reason I picked it: it's a
dataset where you actually need tools like Spark, instead of loading everything into pandas
and hoping it fits in memory.

I'm building it as a personal project to get better at data engineering and machine learning,
and I'm trying to do it the way it would be done in a real team, with tests, CI and decisions
written down, rather than as a single notebook.

## Where it stands

It's early days. For now the repository has the project setup: the Python package, tooling,
tests and a CI pipeline that runs on every push. The data work comes next.

## The plan

The first part is the data pipeline: downloading the raw monthly files, cleaning them (there
are trips with negative fares, dates in the wrong year and other surprises) and turning them
into a table of demand per zone and hour.

With that in place, I'll start from simple baselines and see how much a gradient boosting
model can improve on them. The tricky part with time series is validating honestly, without
letting the model peek at the future, so I'll spend some time on that.

If the results are good, I'd like to serve the forecasts through a small API and a dashboard.
There are also a couple of side questions I find interesting, like whether weather helps the
forecasts, or how congestion pricing in Manhattan changed taxi and ride-hailing demand after
January 2025. I'll see where those fit once the core is working.

## Running it

You'll need Linux, macOS or WSL2, [uv](https://docs.astral.sh/uv/) and Java 17 (for Spark).

```bash
git clone https://github.com/ccccarloswd/nyc-taxi-demand.git
cd nyc-taxi-demand
make install
make check
```

`make help` shows the other commands. Raw data is never committed to the repo; the pipeline
will download it into `data/`.

## Notes

I keep a short record of the main technical decisions and why I made them in
[`docs/decisions`](docs/decisions/).

Trip data © NYC Taxi & Limousine Commission. Code under the [MIT license](LICENSE).
