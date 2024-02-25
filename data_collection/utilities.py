import pandas as pd
from sqlalchemy import create_engine

def dataframe_to_sql(df, directory, db_name):
    """
    Converts a pandas DataFrame to a SQL database file.
    
    Parameters:
    - df: The pandas DataFrame to be converted to SQL.
    - directory: The target directory where the SQL database file will be created.
    - db_name: The name of the database file to be created.
    
    Returns:
    - A string message indicating the success of the operation.
    """
    # Create the SQLAlchemy engine
    engine = create_engine(f'sqlite:///{directory}/{db_name}.db')

    # Write the data to the SQL database
    df.to_sql(db_name, engine, index=False, if_exists='replace')
    
    return f"Database {db_name}.db created successfully in {directory}"
