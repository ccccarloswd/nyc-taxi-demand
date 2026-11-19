"""Read raw TLC trip files into one DataFrame with a consistent schema.

The monthly files are not consistent with each other: 2023-01 stores
passenger_count, RatecodeID and the zone ids with different types than later
months, airport_fee is spelled Airport_fee from 2023-02 on, and new columns
appear over time (cbd_congestion_fee in 2025, request_source in 2026). Spark
cannot read them together as they are, so each file is read on its own, cast
to YELLOW_SCHEMA and then stacked.
"""

from pathlib import Path

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

from nyc_taxi.ingest import YearMonth, month_range, trip_file_path
from nyc_taxi.paths import RAW_DIR

YELLOW_SCHEMA = T.StructType(
    [
        T.StructField("VendorID", T.LongType()),
        T.StructField("tpep_pickup_datetime", T.TimestampType()),
        T.StructField("tpep_dropoff_datetime", T.TimestampType()),
        T.StructField("passenger_count", T.LongType()),
        T.StructField("trip_distance", T.DoubleType()),
        T.StructField("RatecodeID", T.LongType()),
        T.StructField("store_and_fwd_flag", T.StringType()),
        T.StructField("PULocationID", T.LongType()),
        T.StructField("DOLocationID", T.LongType()),
        T.StructField("payment_type", T.LongType()),
        T.StructField("fare_amount", T.DoubleType()),
        T.StructField("extra", T.DoubleType()),
        T.StructField("mta_tax", T.DoubleType()),
        T.StructField("tip_amount", T.DoubleType()),
        T.StructField("tolls_amount", T.DoubleType()),
        T.StructField("improvement_surcharge", T.DoubleType()),
        T.StructField("total_amount", T.DoubleType()),
        T.StructField("congestion_surcharge", T.DoubleType()),
        T.StructField("airport_fee", T.DoubleType()),
        T.StructField("cbd_congestion_fee", T.DoubleType()),
        T.StructField("request_source", T.StringType()),
    ]
)


def conform(df: DataFrame, schema: T.StructType = YELLOW_SCHEMA) -> DataFrame:
    """Return df with exactly the columns of schema, in order and with its types.

    Column names are matched ignoring case. Columns missing from df come back as
    nulls; a column that the schema doesn't know raises, so a new column in a
    future file is noticed instead of silently dropped.
    """
    by_lower = {name.lower(): name for name in df.columns}
    known = {field.name.lower() for field in schema.fields}
    unknown = sorted(set(by_lower) - known)
    if unknown:
        raise ValueError(f"columns not in the schema: {unknown}")

    columns: list[Column] = []
    for field in schema.fields:
        source = by_lower.get(field.name.lower())
        column = F.col(f"`{source}`") if source else F.lit(None)
        columns.append(column.cast(field.dataType).alias(field.name))
    return df.select(columns)


def load_raw_yellow(
    spark: SparkSession, start: YearMonth, end: YearMonth, raw_dir: Path = RAW_DIR
) -> DataFrame:
    """Read the raw yellow taxi files from start to end, both included.

    Adds a source_month column ('YYYY-MM') with the file each row came from.
    """
    result: DataFrame | None = None
    for month in month_range(start, end):
        path = trip_file_path("yellow", month, raw_dir)
        frame = conform(spark.read.parquet(str(path))).withColumn("source_month", F.lit(str(month)))
        result = frame if result is None else result.unionByName(frame)
    assert result is not None  # month_range always yields at least one month
    return result
