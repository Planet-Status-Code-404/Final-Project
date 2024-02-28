import os
import requests
import json
import sqlite3
import pandas as pd

# Need to use provided API key offline

api_key = os.environ.get("CENSUS_API_KEY")


def load_dataframe(response):
    data_json = response.json()
    columns = data_json[0]
    rows = data_json[1:]
    dataframe = pd.DataFrame(rows, columns=columns)
    return dataframe


state_code_dictionary = {
    "Illinois": "17",
    "Louisiana": "22",
    "Washington": "53",
    "Florida": "12",
    "California": "06",
}

## 2020 Decennial Census
# Demographic Characteristics(DP): Distribution of Race
variable_guide_dp = "https://api.census.gov/data/2020/dec/dp/variables.html"
url_dp = "https://api.census.gov/data/2020/dec/dp?"
dp_dictionary = {
    "DP1_0078C": "White Population",
    "DP1_0079C": "Black or African American Population",
    "DP1_0080C": "American Indian and Alaskan Native Population",
    "DP1_0081C": "Asian Population",
    "DP1_0082C": "Native Hawaiian and Other Pacific Islander Population",
    "DP1_0083C": "Other Race Population",
}
params_dp = {
    "get": "NAME,DP1_0078C,DP1_0079C,DP1_0080C,DP1_0081C,DP1_0082C,DP1_0083C",
    "for": "TRACT:*",
    "key": api_key,
}
dp_dataframes = {}
for state, state_code in state_code_dictionary.items():
    params_dp["in"] = f"state:{state_code}"
    response_dp = requests.get(url_dp, params=params_dp)
    dp_dataframes[state] = load_dataframe(response_dp)

# Renaming column names as per variable list
for state, dataframe in dp_dataframes.items():
    # Mapping old column names to new ones
    column_mapping_dhc = {
        old_name: dp_dictionary.get(old_name, old_name)
        for old_name in dataframe.columns
    }
    dp_dataframes[state] = dataframe.rename(columns=column_mapping_dhc)

compiled_dp = []
for state, df in dp_dataframes.items():
    compiled_dp.append(df)

compiled_dataframe_dp = pd.concat(compiled_dp, ignore_index=True)

# Demographic and Housing Characteristics(DHC): Race and Housing Characteristics
variable_guide_dhc = "https://api.census.gov/data/2020/dec/dhc/variables.html"
url_dhc = "https://api.census.gov/data/2020/dec/dhc?"
dhc_variable_dictionary = {
    "H12A_002N": "owner_occuppied_white",
    "H12A_010N": "renter_occupied_white",
    "H12B_002N": "owner_occupied_black_or_african_american",
    "H12B_010N": "renter_occupied_black_or_african_american",
    "H12C_002N": "owner_occuppied_american_indian_&_alaska_native",
    "H12C_010N": "renter_occupied_american_indian_&_alaska_native",
    "H12D_002N": "owner_occupied_asian",
    "H12D_010N": "renter_occupied_asian",
    "H12E_002N": "owner_occupied_native_hawaiian",
    "H12E_010N": "renter_occupied_native_hawaiian",
    "H12F_002N": "owner_occuppied_other_race",
    "H12F_010N": "renter_occuppied_other_race",
}
params_dhc = {
    "get": "NAME,H12A_002N,H12A_010N,H12B_002N,H12B_010N,H12C_002N,H12C_010N,H12D_002N,H12D_010N,H12E_002N,H12E_010N,H12F_002N,H12F_010N",
    "for": "TRACT:*",
    "key": api_key,
}
ddhc_df_dataframes = {}
for state, state_code in state_code_dictionary.items():
    params_dhc["in"] = f"state:{state_code}"
    response_ddhc = requests.get(url_dhc, params=params_dhc)

    ddhc_df_dataframes[state] = load_dataframe(response_ddhc)

# Renaming column names as per variable list
for state, dataframe in ddhc_df_dataframes.items():
    # Mapping old column names to new ones
    column_mapping_dhc = {
        old_name: dhc_variable_dictionary.get(old_name, old_name)
        for old_name in dataframe.columns
    }
    ddhc_df_dataframes[state] = dataframe.rename(columns=column_mapping_dhc)

compiled_dhc = []
for state, df in ddhc_df_dataframes.items():
    compiled_dhc.append(df)

compiled_dataframe_dhc = pd.concat(compiled_dhc, ignore_index=True)

# Loading Community Resilience Estimates for Counties
cre_dictionary = {
    "PRED0_E": "Estimated number of individuals with zero components of social vulnerability",
    "PRED0_PE": "Rate of individuals with zero components of social vulnerability",
    "PRED12_E": "Estimated number of individuals with one-two components of social vulnerability",
    "PRED12_PE": "Rate of individuals with one-two components of social vulnerability",
    "PRED3_E": "Estimated number of individuals with three or more components of social vulnerability",
    "PRED3_PE": "Rate of individuals with three or more components of social vulnerability",
}
params_cre = {
    "get": "NAME,PRED0_E,PRED0_PE,PRED12_E,PRED12_PE,PRED3_E,PRED3_PE",
    "for": "TRACT:*",
    "key": api_key,
}
url = "https://api.census.gov/data/2022/cre?"

cre_dataframes = {}
for state, state_code in state_code_dictionary.items():
    params_cre["in"] = f"state:{state_code}"
    response_cre = requests.get(url, params=params_cre)

    cre_dataframes[state] = load_dataframe(response_cre)


# CRE: Renaming column names as per variable list
for state, dataframe in cre_dataframes.items():
    # Mapping old column names to new ones
    column_mapping_cre = {
        old_name: cre_dictionary.get(old_name, old_name)
        for old_name in dataframe.columns
    }
    cre_dataframes[state] = dataframe.rename(columns=column_mapping_cre)

cre_compiled_dfs = []
for state, df in cre_dataframes.items():
    cre_compiled_dfs.append(df)

# Concatenate all DataFrames in the list along the rows (axis=0)
compiled_dataframe_cre = pd.concat(cre_compiled_dfs, ignore_index=True)

# Merge the first two DataFrames
merged_df = pd.merge(
    compiled_dataframe_dp,
    compiled_dataframe_dhc,
    on=["NAME", "state", "county", "tract"],
    how="outer",
)
# Merge the third DataFrame with the merged result
final_merged_df = pd.merge(
    merged_df,
    compiled_dataframe_cre,
    on=["NAME", "state", "county", "tract"],
    how="outer",
)


def compute_census_tract(dataframe, state, county, tract):
    pass


# print(final_merged_df.columns)
# print(final_merged_df[["NAME", "state", "county", "tract"]].head())
# final_merged_df.to_csv("census_data.csv", index=False)


# WRITING TO SQL DATABASE
def creating_sql_database(data, database_name, table_name):
    connection = sqlite3.connect(database_name)
    data.to_sql(table_name, connection, if_exists="replace", index=False)

    connection.commit()
    connection.close()
