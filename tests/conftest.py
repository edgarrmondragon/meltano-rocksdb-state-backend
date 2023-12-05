from __future__ import annotations

from importlib.metadata import version


def pytest_report_header() -> list[str]:
    """Return a list of strings to be displayed in the header of the report."""
    return [
        f"meltano: {version('meltano')}",
        f"rocksdb: {version('rocksdict')}",
    ]
