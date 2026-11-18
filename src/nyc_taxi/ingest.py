"""Download raw TLC trip record files into data/raw.

Usage:
    uv run python -m nyc_taxi.ingest --start 2023-01 --end 2023-02
"""

from __future__ import annotations

import argparse
import logging
import shutil
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from nyc_taxi.paths import RAW_DIR

BASE_URL = "https://d37ci6vzurychx.cloudfront.net"
ZONE_LOOKUP_URL = f"{BASE_URL}/misc/taxi_zone_lookup.csv"
SERVICES = ("yellow", "green", "fhvhv")

log = logging.getLogger(__name__)


@dataclass(frozen=True, order=True)
class YearMonth:
    year: int
    month: int

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError(f"month must be between 1 and 12, got {self.month}")

    @classmethod
    def parse(cls, text: str) -> YearMonth:
        """Parse a 'YYYY-MM' string."""
        year, month = text.split("-")
        return cls(int(year), int(month))

    def next(self) -> YearMonth:
        if self.month == 12:
            return YearMonth(self.year + 1, 1)
        return YearMonth(self.year, self.month + 1)

    def __str__(self) -> str:
        return f"{self.year}-{self.month:02d}"


def month_range(start: YearMonth, end: YearMonth) -> Iterator[YearMonth]:
    """Yield every month from start to end, both included."""
    if start > end:
        raise ValueError(f"start ({start}) is after end ({end})")
    current = start
    while current <= end:
        yield current
        current = current.next()


def trip_file_url(service: str, month: YearMonth) -> str:
    return f"{BASE_URL}/trip-data/{service}_tripdata_{month}.parquet"


def trip_file_path(service: str, month: YearMonth, raw_dir: Path = RAW_DIR) -> Path:
    return raw_dir / service / f"{service}_tripdata_{month}.parquet"


def download(url: str, dest: Path, *, timeout: float = 60) -> bool:
    """Download url to dest unless dest already exists. Return True if it downloaded.

    The file is written to a '.part' file first and renamed at the end, so an
    interrupted download never leaves a truncated file that looks complete.
    """
    if dest.exists():
        log.info("skip %s (already downloaded)", dest.name)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    log.info("download %s", url)
    with urllib.request.urlopen(url, timeout=timeout) as response, tmp.open("wb") as out:
        shutil.copyfileobj(response, out)
    tmp.replace(dest)
    return True


def ingest(service: str, start: YearMonth, end: YearMonth, raw_dir: Path = RAW_DIR) -> None:
    """Download the zone lookup table and every monthly trip file in the range."""
    download(ZONE_LOOKUP_URL, raw_dir / "taxi_zone_lookup.csv")
    for month in month_range(start, end):
        download(trip_file_url(service, month), trip_file_path(service, month, raw_dir))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Download TLC trip record files.")
    parser.add_argument("--start", type=YearMonth.parse, required=True, help="YYYY-MM")
    parser.add_argument("--end", type=YearMonth.parse, required=True, help="YYYY-MM")
    parser.add_argument("--service", choices=SERVICES, default="yellow")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ingest(args.service, args.start, args.end, args.raw_dir)


if __name__ == "__main__":
    main()
