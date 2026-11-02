import nyc_taxi


def test_package_exposes_version() -> None:
    assert isinstance(nyc_taxi.__version__, str)
    assert nyc_taxi.__version__.count(".") == 2
