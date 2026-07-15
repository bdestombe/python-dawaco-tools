"""Synthetic DAWACO test database used by CI.

All rows in this module are fabricated for tests. Do not replace them with
exports from the production DAWACO database.
"""

import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine

MOCK_DATABASE_SCHEMA_VERSION = "2026.06"


def build_mock_dawaco_database(database_path: Path) -> Engine:
    """Create a SQLite database with the DAWACO tables used by tests."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{database_path}")

    with engine.begin() as connection:
        _write_metadata(connection)
        _write_monitoring_points(connection)
        _write_filters(connection)
        _write_groundwater_levels(connection)
        _write_validated_hand_measurements(connection)
        _write_sensor_changes(connection)
        _write_refpunt_adjustments(connection)
        _write_monitoring_dates(connection)
        _write_meteo(connection)
        _write_boring(connection)
        _write_triwaco(connection)

    return engine


def _write_metadata(connection: Connection) -> None:
    pd.DataFrame([
        {"key": "source", "value": "synthetic"},
        {"key": "schema_version", "value": MOCK_DATABASE_SCHEMA_VERSION},
    ]).to_sql("dawacotools_mock_metadata", connection, index=False, if_exists="replace")


def _write_monitoring_points(connection: Connection) -> None:
    pd.DataFrame([
        {
            "RECNUM": 1,
            "MpCode": "MOCK001",
            "Xcoor": 100000.0,
            "Ycoor": 500000.0,
            "Soort": 1,
            "Aant_Fil": 2,
            "Refpunt": 2.0,
            "Maaiveld": 1.25,
        },
        {
            "RECNUM": 2,
            "MpCode": "MOCK002",
            "Xcoor": 100003.0,
            "Ycoor": 500004.0,
            "Soort": 2,
            "Aant_Fil": 1,
            "Refpunt": 2.5,
            "Maaiveld": 1.5,
        },
        {
            "RECNUM": 3,
            "MpCode": "MOCK010",
            "Xcoor": 100100.0,
            "Ycoor": 500000.0,
            "Soort": 1,
            "Aant_Fil": 1,
            "Refpunt": 3.0,
            "Maaiveld": 2.0,
        },
    ]).to_sql("mp", connection, index=False, if_exists="replace")


def _write_filters(connection: Connection) -> None:
    pd.DataFrame([
        {
            "RECNUM": 101,
            "MpCode": "MOCK001",
            "Filtnr": 1,
            "Verval_datum": None,
            "Bk_filt": 4.0,
            "Ok_filt": 6.0,
            "Wvp": "WVP1",
        },
        {
            "RECNUM": 102,
            "MpCode": "MOCK001",
            "Filtnr": 2,
            "Verval_datum": None,
            "Bk_filt": 8.0,
            "Ok_filt": 10.0,
            "Wvp": "WVP2",
        },
        {
            "RECNUM": 103,
            "MpCode": "MOCK002",
            "Filtnr": 1,
            "Verval_datum": None,
            "Bk_filt": 5.0,
            "Ok_filt": 7.0,
            "Wvp": "WVP1",
        },
        {
            "RECNUM": 104,
            "MpCode": "MOCK010",
            "Filtnr": 1,
            "Verval_datum": "2020-01-01",
            "Bk_filt": 3.0,
            "Ok_filt": 4.0,
            "Wvp": "WVP0",
        },
    ]).to_sql("filters", connection, index=False, if_exists="replace")


def _write_groundwater_levels(connection: Connection) -> None:
    pd.DataFrame([
        {"filtrec": 101, "datum": "2020-01-01", "tijd": "00:00", "meting_nap": 1.00, "Temp": 8.0, "Bron": "A"},
        {"filtrec": 101, "datum": "2020-01-02", "tijd": "00:00", "meting_nap": 1.10, "Temp": 0.0, "Bron": "V"},
        {"filtrec": 101, "datum": "2020-01-05", "tijd": "00:00", "meting_nap": -999.0, "Temp": -99.0, "Bron": "A"},
        {"filtrec": 101, "datum": "2020-01-06", "tijd": "00:00", "meting_nap": 1.40, "Temp": 9.0, "Bron": "A"},
        {"filtrec": 102, "datum": "2020-01-01", "tijd": "00:00", "meting_nap": 0.50, "Temp": 7.5, "Bron": "A"},
        {"filtrec": 103, "datum": "2020-01-01", "tijd": "00:00", "meting_nap": 0.75, "Temp": 7.0, "Bron": "A"},
        {"filtrec": 103, "datum": "2020-01-03", "tijd": "00:00", "meting_nap": 0.95, "Temp": 7.2, "Bron": "V"},
        {"filtrec": 103, "datum": "2020-01-06", "tijd": "00:00", "meting_nap": 1.35, "Temp": 7.4, "Bron": "A"},
    ]).to_sql("Stijghgt", connection, index=False, if_exists="replace")


def _write_validated_hand_measurements(connection: Connection) -> None:
    pd.DataFrame([
        {"Filtrec": 101, "Cont_Dat": "2020-01-02", "Cont_Tijd": "07:30"},
        {"Filtrec": 103, "Cont_Dat": "2020-01-04", "Cont_Tijd": "12:00"},
        {"Filtrec": 104, "Cont_Dat": "2020-01-05", "Cont_Tijd": "13:00"},
    ]).to_sql("StygCont", connection, index=False, if_exists="replace")


def _write_sensor_changes(connection: Connection) -> None:
    pd.DataFrame([
        {
            "Recnum": 401,
            "Dm_Rec": 101,
            "Datum": "2020-01-03",
            "Tijd": "08:00",
            "Type_Wijz": "O",
            "MpCode": "MOCK001",
            "Filtnr": 1,
            "Opmerking": "Synthetic sensor removed",
        },
        {
            "Recnum": 402,
            "Dm_Rec": 101,
            "Datum": "2020-01-01",
            "Tijd": "09:00",
            "Type_Wijz": "I",
            "MpCode": "MOCK001",
            "Filtnr": 1,
            "Opmerking": "Synthetic sensor placed",
        },
        {
            "Recnum": 403,
            "Dm_Rec": 102,
            "Datum": "2020-01-01",
            "Tijd": "10:00",
            "Type_Wijz": "I",
            "MpCode": "MOCK001",
            "Filtnr": 2,
            "Opmerking": "Synthetic sensor placed",
        },
        {
            "Recnum": 404,
            "Dm_Rec": 103,
            "Datum": "2020-01-04",
            "Tijd": "11:00",
            "Type_Wijz": "O",
            "MpCode": "MOCK002",
            "Filtnr": 1,
            "Opmerking": "Synthetic sensor removed",
        },
        {
            "Recnum": 405,
            "Dm_Rec": 104,
            "Datum": "2020-01-05",
            "Tijd": "12:00",
            "Type_Wijz": "I",
            "MpCode": "MOCK010",
            "Filtnr": 1,
            "Opmerking": "Synthetic sensor placed",
        },
    ]).to_sql("DrukmetW", connection, index=False, if_exists="replace")


def _write_refpunt_adjustments(connection: Connection) -> None:
    pd.DataFrame([
        {"Filtrec": 101, "Datum": "2020-01-02", "Tijd": "06:00", "Type": "A"},
        {"Filtrec": 102, "Datum": "2020-01-02", "Tijd": "06:00", "Type": "A"},
        {"Filtrec": 103, "Datum": "2020-01-04", "Tijd": "10:30", "Type": "A"},
        {"Filtrec": 104, "Datum": "2020-01-05", "Tijd": "14:00", "Type": "B"},
    ]).to_sql("Refpunt", connection, index=False, if_exists="replace")


def _write_monitoring_dates(connection: Connection) -> None:
    pd.DataFrame([
        {"filtrec": 101, "datum": "2021-01-01"},
        {"filtrec": 101, "datum": "2021-01-15"},
        {"filtrec": 102, "datum": "2021-02-01"},
        {"filtrec": 103, "datum": "2021-03-01"},
    ]).to_sql("gwkmon", connection, index=False, if_exists="replace")


def _write_meteo(connection: Connection) -> None:
    row: dict[str, str | int | float] = {"code": "235W", "code_par": "N", "Jaar": 2020, "Maand": 1}
    row.update({f"W_d{day}": -99.0 for day in range(1, 32)})
    row["W_d1"] = 1.0
    row["W_d3"] = 3.0
    pd.DataFrame([row]).to_sql("metwaar", connection, index=False, if_exists="replace")


def _write_boring(connection: Connection) -> None:
    pd.DataFrame([
        {"Recnum": 201, "MpCode": "MOCK001", "Nencode": "SAND", "Laag_boven": 0.0, "Laag_onder": 1.0},
        {"Recnum": 202, "MpCode": "MOCK001", "Nencode": "CLAY", "Laag_boven": 1.0, "Laag_onder": 2.0},
    ]).to_sql("NenLaag", connection, index=False, if_exists="replace")
    pd.DataFrame([
        {"Code": "SAND", "Omschrijving": "Synthetic sand"},
        {"Code": "CLAY", "Omschrijving": "Synthetic clay"},
    ]).to_sql("NenNorm", connection, index=False, if_exists="replace")
    pd.DataFrame([
        {"Nenlaagrec": 201, "Toevoeging": "fine"},
        {"Nenlaagrec": 202, "Toevoeging": "silty"},
    ]).to_sql("NenToev", connection, index=False, if_exists="replace")


def _write_triwaco(connection: Connection) -> None:
    pd.DataFrame([
        {"MpCode": "MOCK001", "Bk_pak": 15.0, "Type_pak": "C", "Num_pak": 3},
        {"MpCode": "MOCK001", "Bk_pak": 0.0, "Type_pak": "A", "Num_pak": 1},
        {"MpCode": "MOCK001", "Bk_pak": 5.0, "Type_pak": "B", "Num_pak": 2},
    ]).to_sql("HydStrat", connection, index=False, if_exists="replace")
    pd.DataFrame([{"Mpcode": "MOCK001", "Maaiveld": 2.0}]).to_sql(
        "MpMv",
        connection,
        index=False,
        if_exists="replace",
    )


def main(argv: list[str] | None = None) -> None:
    """Build the synthetic SQLite database at a requested path."""
    parser = argparse.ArgumentParser(description="Build the synthetic DAWACO SQLite database used by tests.")
    parser.add_argument("database_path", type=Path, help="Path to the SQLite database to create.")
    args = parser.parse_args(argv)

    engine = build_mock_dawaco_database(args.database_path)
    engine.dispose()


if __name__ == "__main__":
    main()
