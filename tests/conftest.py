"""Pytest configuration for DAWACO database tests."""

import os

import pytest

from dawacotools import io as dawaco_io
from tests.mock_dawaco import build_mock_dawaco_database

PRIVATE_DATABASE_URL_ENV_VAR = "DAWACOTOOLS_PRIVATE_DATABASE_URL"
PRIVATE_DATABASE_SCHEMA_ENV_VAR = "DAWACOTOOLS_PRIVATE_DB_SCHEMA"
RUN_PRIVATE_DATABASE_ENV_VAR = "DAWACOTOOLS_RUN_PRIVATE_DB"


def pytest_addoption(parser):
    parser.addoption(
        "--run-live-db",
        action="store_true",
        default=False,
        help="Run tests marked live_db against the configured DAWACO database.",
    )
    parser.addoption(
        "--run-private-db",
        action="store_true",
        default=False,
        help="Run tests marked private_db against DAWACOTOOLS_PRIVATE_DATABASE_URL or DAWACOTOOLS_DATABASE_URL.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "live_db: tests that require access to the real DAWACO database")
    config.addinivalue_line("markers", "private_db: tests that require an opt-in private local mock database")


def pytest_collection_modifyitems(config, items):
    run_live = config.getoption("--run-live-db") or os.environ.get("DAWACOTOOLS_RUN_LIVE_DB") == "1"
    run_private = config.getoption("--run-private-db") or os.environ.get(RUN_PRIVATE_DATABASE_ENV_VAR) == "1"
    private_url = _private_database_url()

    if run_private and private_url is None:
        msg = f"--run-private-db requires {PRIVATE_DATABASE_URL_ENV_VAR} or {dawaco_io.DATABASE_URL_ENV_VAR}"
        raise pytest.UsageError(msg)

    skip_live = pytest.mark.skip(reason="live DAWACO database tests need --run-live-db")
    skip_private = pytest.mark.skip(reason="private DAWACO mock database tests need --run-private-db")
    for item in items:
        if "live_db" in item.keywords and not run_live:
            item.add_marker(skip_live)
        if "private_db" in item.keywords and not run_private:
            item.add_marker(skip_private)


def _private_database_url():
    return os.environ.get(PRIVATE_DATABASE_URL_ENV_VAR) or os.environ.get(dawaco_io.DATABASE_URL_ENV_VAR)


@pytest.fixture(scope="session")
def mock_dawaco_engine(tmp_path_factory):
    database_path = tmp_path_factory.mktemp("dawaco") / "mock_dawaco.sqlite"
    engine = build_mock_dawaco_database(database_path)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def configure_dawaco_database(request, mock_dawaco_engine):
    previous_engine = dawaco_io.engine
    previous_schema = dawaco_io.dbname
    private_engine = None

    if request.node.get_closest_marker("live_db"):
        dawaco_io.reset_database_engine()
    elif request.node.get_closest_marker("private_db"):
        private_url = _private_database_url()
        if private_url is None:
            pytest.skip(f"set {PRIVATE_DATABASE_URL_ENV_VAR} or {dawaco_io.DATABASE_URL_ENV_VAR}")

        private_schema = os.environ.get(
            PRIVATE_DATABASE_SCHEMA_ENV_VAR,
            os.environ.get(dawaco_io.SCHEMA_ENV_VAR, ""),
        )
        private_engine = dawaco_io.create_dawaco_engine(database_url=private_url)
        dawaco_io.set_database_engine(private_engine, schema=private_schema)
    else:
        dawaco_io.set_database_engine(mock_dawaco_engine, schema="")

    yield

    dawaco_io.set_database_engine(previous_engine, schema=previous_schema)
    if private_engine is not None:
        private_engine.dispose()
