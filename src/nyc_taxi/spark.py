"""Spark session shared by the whole project."""

from pyspark.sql import SparkSession


def get_spark(app_name: str = "nyc-taxi-demand", driver_memory: str = "8g") -> SparkSession:
    """Return a local Spark session that uses every core on the machine.

    The session time zone is UTC so Spark never shifts trip timestamps: TLC stores
    them as New York wall-clock time with no time zone attached.
    """
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
