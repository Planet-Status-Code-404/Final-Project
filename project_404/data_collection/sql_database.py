import sqlite3
import os
import csv
import pathlib

db_file_path = pathlib.Path(__file__).parent / "output_data/climate_database.db"
csv_directory_path = pathlib.Path(__file__).parent / "output_data"


def insert_tables_to_database(csv_directory_path, db_file_path):
    """
    Traverses through the csv_directory_path and converts csv files present in the
    folder to add to the climate_database.

    Parameters:
    - csv_directory_path (str): The path to the directory containing CSV files.
    - db_file_path (str): The path to the SQLite database file.

    Raises:
    - Exception: If the 'geo_id' column is not found in any of the CSV files.

    Returns:
    - None
    """
    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()

    for root, _, files in os.walk(csv_directory_path):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                table_name = os.path.splitext(file)[0]

                with open(csv_file_path, "r", encoding="utf-8") as csv_file:
                    csv_reader = csv.reader(csv_file)
                    headers = next(csv_reader)

                    # Search for the primary key 'geo_id'
                    primary_key_column = None
                    for header in headers:
                        if "geo_id" in header.lower():
                            primary_key_column = header
                            break
                    if primary_key_column is None:
                        print(f"Skipping file {file} as 'geo_id' column not found")
                        continue

                    remaining_columns = [
                        (
                            f'"{column}"'
                            if any(c in column for c in [" ", ",", "&", "."])
                            else column
                        )
                        for column in headers
                        if column != primary_key_column
                    ]
                    table_creation_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({primary_key_column} INTEGER PRIMARY KEY, {' ,'.join(remaining_columns)})"

                    cursor.execute(table_creation_sql)

                    # Insert data into the table with error handling
                    row_number = 0
                    for row in csv_reader:
                        row_number += 1
                        try:
                            cursor.execute(
                                f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(row))})",
                                row,
                            )
                        except UnicodeDecodeError as e:
                            print(
                                f"Skipping row {row_number} due to UnicodeDecodeError: {e}"
                            )
                            continue
                        except sqlite3.IntegrityError as e:
                            pass
    print("Database created successfully and Tables added")
    connection.commit()
    connection.close()


# Executing the function to add data in the directory to the database
insert_tables_to_database(csv_directory_path, db_file_path)
