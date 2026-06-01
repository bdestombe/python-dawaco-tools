"""Pytest configuration for DAWACO database tests."""

import os

import pytest

from dawacotools import io as dawaco_io
from tests.mock_dawaco import build_mock_dawaco_database


def pytest_addoption(parser):
    parser.addoption(
        "--run-live-db",
        action="store_true",
        default=False,
        help="Run tests marked live_db against the configured DAWACO database.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "live_db: tests that require access to the real DAWACO database")


def pytest_collection_modifyitems(config, items):
    run_live = config.getoption("--run-live-db") or os.environ.get("DAWACOTOOLS_RUN_LIVE_DB") == "1"
    if run_live:
        return

    skip_live = pytest.mark.skip(reason="live DAWACO database tests need --run-live-db")
    for item in items:
        if "live_db" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(scope="session")
def mock_dawaco_engine(tmp_path_factory):
    database_path = tmp_path_factory.mktemp("dawaco") / "mock_dawaco.sqlite"
    return build_mock_dawaco_database(database_path)


@pytest.fixture(autouse=True)
def configure_dawaco_database(request, mock_dawaco_engine):
    previous_engine = dawaco_io.engine
    previous_schema = dawaco_io.dbname

    if request.node.get_closest_marker("live_db"):
        dawaco_io.reset_database_engine()
    else:
        dawaco_io.set_database_engine(mock_dawaco_engine, schema="")

    yield

    dawaco_io.set_database_engine(previous_engine, schema=previous_schema)
