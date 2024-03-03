import pandas as pd
from sqlalchemy import create_engine
import pathlib

def dataframe_to_sql(df, table_name, db_name):
    """
    Stores a DataFrame in a SQL database.

    Parameters:
    - df: DataFrame to store in the database.
    - table_name: Name of the table to store the data.
    - db_name: Name of the database.

    Returns:
    - A message indicating the success of the operation.
    """
    # Create the engine to connect to the SQLite database
    engine = create_engine(f'sqlite:///data_collection/data_files/{db_name}.db')

    # Use the to_sql() method to write records stored in a DataFrame to a SQL database
    df.to_sql(table_name, engine, index=False, if_exists='replace')
    
    # Return a success message
    return f"The data has been successfully stored in the '{table_name}' table of the '{db_name}.db' database."

def merge_dfs_to_csv(list_of_dfs, name_of_csv):
    """
    Takes a list of DataFrames and Merges into one.
    
    Inspired by https://pandas.pydata.org/docs/user_guide/merging.html

    Parameters: 
    - list_of_dfs A list of Pandas DataFrames
    - name_of_csv: string for the name of csv.

    Returns:
    - a dataframe that merges the parameters.
    """

    merged_df = pd.concat(list_of_dfs)

    merged_df.to_csv(f"data_collection/output_data/{name_of_csv}")

    return merged_df
