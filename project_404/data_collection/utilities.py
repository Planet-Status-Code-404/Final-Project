import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

def dataframe_to_sql(df, table_name, db_name):
    """
    Stores a DataFrame in a SQL database. This function is used for exploratory steps of 
    understanding how the Chatbot interacts with SQL databases.

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
    path = Path(__file__).resolve().parent / f"output_data/{name_of_csv}"
    merged_df.to_csv(path)

    return merged_df

def clean_epa(epa_df):
    """
    Cleans redundant EPA EJ DF columns we do not want.

    Parameters: epa_df -> a pandas dataframe of EPA EJ data.

    Returns: None, updates the EPA data file in place
    """

    epa_df.drop(["demographics.P_NHWHITE", "demographics.P_NHBLACK",
            "demographics.P_NHASIAN","demographics.P_HISP",
            "demographics.P_NHAMERIND","demographics.P_NHHAWPAC",
            "demographics.P_NHOTHER_RACE","demographics.P_NHTWOMORE"], axis=1)

    epa_df.rename(columns={"main.areaid": "geo_id"}, inplace=True)


    # List of columns to keep
    columns_to_keep = [
        "demographics.P_ENGLISH", "demographics.P_NON_ENGLISH", "demographics.P_AGE_LT5",
        "demographics.P_AGE_LT18", "demographics.P_AGE_GT17", "demographics.P_AGE_GT64",
        "demographics.P_HLI_OTHER_LI", "demographics.P_LOWINC", "demographics.PCT_MINORITY",
        "demographics.P_EDU_LTHS", "demographics.P_LIMITED_ENG_HH", "demographics.P_EMP_STAT_UNEMPLOYED",
        "demographics.P_DISABILITY", "demographics.P_MALES", "demographics.P_FEMALES",
        "demographics.LIFEEXP", "demographics.PER_CAP_INC", "demographics.HSHOLDS",
        "demographics.P_OWN_OCCUPIED", "main.RAW_D_PEOPCOLOR", "main.RAW_D_INCOME",
        "main.RAW_D_UNDER5", "main.RAW_D_OVER64", "main.RAW_D_UNEMPLOYED", "main.RAW_D_LIFEEXP",
        "main.RAW_E_DIESEL", "main.RAW_E_CANCER", "main.RAW_E_TRAFFIC", "main.RAW_E_O3",
        "main.RAW_E_PM25", "main.RAW_E_RSEI_AIR", "main.stateAbbr", "main.stateName",
        "main.totalPop", "main.NUM_AIRPOLL", "main.NUM_BROWNFIELD", "main.NUM_HOSPITAL",
        "main.statLayerCount", "main.statLayerZeroPopCount", "main.weightLayerCount",
        "main.distance", "main.unit", "main.areatype", "main.statlevel",
        "main.placename", "extras.RAW_HI_LIFEEXPPCT", "extras.RAW_HI_ASTHMA",
        "extras.RAW_HI_DISABILITYPCT", "extras.RAW_CG_NOHINCPCT", "extras.RAW_CI_FLOOD",
        "extras.RAW_CI_FLOOD30", "extras.RAW_CI_FIRE", "extras.RAW_CI_FIRE30", "geo_id"
    ]

    epa_df = epa_df.loc[:, columns_to_keep]

    return epa_df