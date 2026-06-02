from pathlib import Path

import pytest
from sqlalchemy import inspect, text

import dawacotools as dt
from dawacotools import io as dawaco_io
from tests.mock_dawaco import MOCK_DATABASE_SCHEMA_VERSION, build_mock_dawaco_database, main


def test_default_tests_use_synthetic_sqlite_database():
    engine = dawaco_io.get_engine()

    assert not dawaco_io.dbname
    assert engine.dialect.name == "sqlite"
    assert "mp" in inspect(engine).get_table_names()


def test_mock_database_contains_only_synthetic_metadata(mock_dawaco_engine):
    with mock_dawaco_engine.connect() as connection:
        metadata = dict(connection.execute(text("select key, value from dawacotools_mock_metadata")).all())

    assert metadata == {
        "schema_version": MOCK_DATABASE_SCHEMA_VERSION,
        "source": "synthetic",
    }


def test_mock_database_builder_can_create_persistent_sqlite_file(tmp_path: Path):
    database_path = tmp_path / "ci_mock_dawaco.sqlite"

    engine = build_mock_dawaco_database(database_path)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    assert database_path.exists()
    assert {
        "HydStrat",
        "MpMv",
        "NenLaag",
        "NenNorm",
        "NenToev",
        "Stijghgt",
        "dawacotools_mock_metadata",
        "filters",
        "gwkmon",
        "metwaar",
        "mp",
    } <= tables


def test_mock_database_module_cli_builds_database(tmp_path: Path):
    database_path = tmp_path / "cli_mock_dawaco.sqlite"

    main([str(database_path)])

    assert database_path.exists()


def test_create_dawaco_engine_uses_database_url_environment(monkeypatch, tmp_path: Path):
    database_path = tmp_path / "env_configured.sqlite"
    monkeypatch.setenv(dawaco_io.DATABASE_URL_ENV_VAR, f"sqlite:///{database_path}")

    engine = dawaco_io.create_dawaco_engine()
    try:
        assert engine.dialect.name == "sqlite"
    finally:
        engine.dispose()


def test_reset_database_engine_restores_schema_from_environment(monkeypatch):
    monkeypatch.setenv(dawaco_io.SCHEMA_ENV_VAR, "guest")

    dawaco_io.reset_database_engine()

    assert dawaco_io.dbname == "guest"


@pytest.mark.private_db
def test_private_database_smoke_returns_monitoring_points():
    mps = dt.get_daw_mps()

    assert not mps.empty
    assert {"Soort", "Xcoor", "Ycoor", "geometry"} <= set(mps.columns)
