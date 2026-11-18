import io
from pathlib import Path

import pytest

from nyc_taxi import ingest
from nyc_taxi.ingest import YearMonth, month_range, trip_file_path, trip_file_url


def test_year_month_parses_and_prints_with_leading_zero() -> None:
    month = YearMonth.parse("2023-01")
    assert month == YearMonth(2023, 1)
    assert str(month) == "2023-01"


def test_year_month_rejects_invalid_month() -> None:
    with pytest.raises(ValueError):
        YearMonth(2023, 13)


def test_month_range_crosses_year_boundary() -> None:
    months = [str(m) for m in month_range(YearMonth(2023, 11), YearMonth(2024, 2))]
    assert months == ["2023-11", "2023-12", "2024-01", "2024-02"]


def test_month_range_rejects_reversed_range() -> None:
    with pytest.raises(ValueError):
        list(month_range(YearMonth(2024, 2), YearMonth(2023, 11)))


def test_trip_file_url_and_path() -> None:
    month = YearMonth(2023, 1)
    assert trip_file_url("yellow", month).endswith("/trip-data/yellow_tripdata_2023-01.parquet")
    assert trip_file_path("yellow", month, Path("raw")) == Path(
        "raw/yellow/yellow_tripdata_2023-01.parquet"
    )


def test_download_skips_existing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = tmp_path / "file.parquet"
    dest.write_bytes(b"already here")

    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("must not hit the network")

    monkeypatch.setattr(ingest.urllib.request, "urlopen", fail)

    assert ingest.download("https://example.com/file.parquet", dest) is False
    assert dest.read_bytes() == b"already here"


def test_download_writes_file_without_leftovers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "nested" / "file.parquet"
    monkeypatch.setattr(ingest.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"data"))

    assert ingest.download("https://example.com/file.parquet", dest) is True
    assert dest.read_bytes() == b"data"
    assert list(dest.parent.iterdir()) == [dest]
