from datetime import datetime
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

from nyc_taxi.ingest import YearMonth, trip_file_path
from nyc_taxi.raw import YELLOW_SCHEMA, conform, load_raw_yellow

PICKUP = datetime(2023, 1, 15, 8, 30)


def _write_month(
    spark: SparkSession, raw_dir: Path, month: YearMonth, row: dict[str, object]
) -> None:
    path = trip_file_path("yellow", month, raw_dir)
    spark.createDataFrame([row]).write.parquet(str(path))


def test_conform_casts_renames_and_fills_missing_columns(spark: SparkSession) -> None:
    df = spark.createDataFrame([{"passenger_count": 2.0, "Airport_fee": 1.75, "PULocationID": 132}])

    row = conform(df).collect()[0]

    assert conform(df).schema == YELLOW_SCHEMA
    assert row["passenger_count"] == 2
    assert row["airport_fee"] == 1.75
    assert row["PULocationID"] == 132
    assert row["cbd_congestion_fee"] is None


def test_conform_rejects_unknown_columns(spark: SparkSession) -> None:
    df = spark.createDataFrame([{"PULocationID": 1, "surprise": "x"}])

    with pytest.raises(ValueError, match="surprise"):
        conform(df)


def test_load_raw_yellow_stacks_months_with_different_types(
    spark: SparkSession, tmp_path: Path
) -> None:
    _write_month(
        spark,
        tmp_path,
        YearMonth(2023, 1),
        {"tpep_pickup_datetime": PICKUP, "passenger_count": 1.0, "airport_fee": 0.0},
    )
    _write_month(
        spark,
        tmp_path,
        YearMonth(2023, 2),
        {"tpep_pickup_datetime": PICKUP, "passenger_count": 3, "Airport_fee": 1.75},
    )

    df = load_raw_yellow(spark, YearMonth(2023, 1), YearMonth(2023, 2), tmp_path)
    rows = sorted(df.collect(), key=lambda r: r["source_month"])

    assert [r["source_month"] for r in rows] == ["2023-01", "2023-02"]
    assert [r["passenger_count"] for r in rows] == [1, 3]
    assert [r["airport_fee"] for r in rows] == [0.0, 1.75]
    assert rows[0]["tpep_pickup_datetime"] == PICKUP
