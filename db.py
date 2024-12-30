import pandas as pd
import sqlite3

# Options.
excel_file = "filtered_list.xlsx"
sheet_name = "2024"

df = pd.read_excel(excel_file, sheet_name=sheet_name)

db_name = "database.db"
conn = sqlite3.connect(db_name)

table_name = "users"
df.to_sql(table_name, conn, if_exists="replace", index=False)

conn.close()

print(
    f"Data from {excel_file} has been successfully written to {db_name} in table {table_name}."
)
