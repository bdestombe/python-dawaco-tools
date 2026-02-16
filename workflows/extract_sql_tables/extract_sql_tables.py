from sqlalchemy import inspect
import pandas as pd
from dawacotools.io import engine

inspector = inspect(engine)

tables = inspector.get_table_names()
for table in tables:
    print(table)

omit_tables = ["Stijghgt", ]
selected_tables = [table for table in tables if table not in omit_tables]

# dfs = {table: pd.read_sql_table(table, engine) for table in selected_tables}
dfs = {}

for table in selected_tables:
    print(f"Reading table: {table}")
    df = pd.read_sql_table(table, engine)
    dfs[table] = df
    print(f"Finished reading table: {table}, number of rows: {len(df)}")

export_filename = "dawaco_sql_tables.xlsx"
with pd.ExcelWriter(export_filename, engine="openpyxl") as writer:
    for table, df in dfs.items():
        print(f"Writing table: {table} to Excel")
        df.to_excel(writer, sheet_name=table, index=False)

print(engine)