import pandas as pd
from sqlalchemy import create_engine

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
