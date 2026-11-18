# Project brief

I wrote this before touching the data, so the goal and the way I judge results are fixed
upfront and don't drift as the project goes on.

**Objective.** Every day at midnight, forecast how many trips will start in each NYC taxi
zone during each hour of the next day (24-hour horizon, hourly granularity). The use case is
planning: how many drivers a fleet needs tomorrow, where and when. Hourly buckets matter
because demand moves a lot within the day (lunch in office areas, nightlife at night).

**Scope.** Yellow taxis only. Uber/Lyft (high-volume FHV) is a different market and would
need its own model; it's out of scope for now, but the code is written so that adding it
later is a configuration change.
All 263 zones, except 264 (Unknown) and 265 (Outside of NYC), which aren't real places to
send a car. Data from January 2023 to the latest published month. Earlier years are left
out because demand was still recovering from COVID; whether adding 2019–2022 helps is
tested later as an experiment.

**Metric.** WAPE (total absolute error divided by total demand), so zones with one or two
trips an hour don't dominate the score the way they would with MAPE. I also report the bias
(do we over- or under-forecast?) and WAPE by zone group (high, medium and low demand), since
the overall WAPE is driven by the busiest zones.

**Evaluation.** Rolling-origin backtesting over the most recent months, one fold per month,
never using data from after the moment of the forecast. The exact design is part of the
evaluation phase.

**Baselines.** A model has to beat both:

1. Seasonal naive: same weekday and hour, one week earlier.
2. Seasonal average: mean of the same weekday and hour over the previous 4 weeks.

**Decision rule.** A change is accepted only if it:

1. improves WAPE in every backtesting fold,
2. improves the mean WAPE by at least 3% relative (e.g. from 20.0% to 19.4% or lower), and
3. when it adds significant complexity (a new data source, much longer training), improves
   it clearly beyond that threshold.

When in doubt, I keep the simpler version.

**Timeline.** Six focused weeks rather than three months at half speed. Freeze date:
31 December 2026, with 20 January 2027 as the hard limit if something slips. After the
freeze, only bug fixes and the write-up.

| Week | Goal |
|---|---|
| 17–23 Nov | Data: download, cleaning rules, hourly demand table |
| 24–30 Nov | Exploration: five findings with numbers |
| 1–7 Dec | Evaluation: backtesting, metrics, both baselines scored |
| 8–14 Dec | Features (calendar, lags) and a first LightGBM model |
| 15–21 Dec | Experiments and error analysis |
| 22–31 Dec | README, cleanup, mock interview |
