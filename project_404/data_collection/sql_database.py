import sqlite3
import os
import csv
import pathlib

db_file_path = pathlib.Path(__file__).parent / "output_data/climate_database.db"
csv_directory_path = pathlib.Path(__file__).parent / "output_data"


def insert_tables_to_database(csv_directory_path, db_file_path):
    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()

    for root, _, files in os.walk(csv_directory_path):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                table_name = os.path.splitext(file)[0]

                with open(csv_file_path, "r") as csv_file:
                    csv_reader = csv.reader(csv_file)
                    headers = next(csv_reader)

                    # Search for the primary key 'geo_id'
                    primary_key_column = None
                    for header in headers:
                        if "geo_id" in header.lower():
                            primary_key_column = header
                            break
                    if primary_key_column is None:
                        raise Exception("geo_id not found")

                    remaining_columns = [
                        (
                            f'"{column}"'
                            if any(c in column for c in [" ", ",", "&"])
                            else column
                        )
                        for column in headers
                        if column != primary_key_column
                    ]
                    table_creation_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({primary_key_column} INTEGER PRIMARY KEY, {' ,'.join(remaining_columns)})"

                    cursor.execute(table_creation_sql)
                    print(f"Table '{table_name}' created successfully.")

                    # Insert data into the table
                    for row in csv_reader:
                        placeholders = ", ".join(["?"] * len(row))
                        cursor.execute(
                            f"INSERT INTO {table_name} VALUES ({placeholders})", row
                        )
                    print("values added to data")
    connection.commit()
    connection.close()


# Executing the function to add data in the directory to the database
insert_tables_to_database(csv_directory_path, db_file_path)
