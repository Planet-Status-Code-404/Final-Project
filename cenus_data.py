import os
from dotenv import load_dotenv
import requests
import json
import sqlite3
import pandas as pd

# Need to use provided API key offline
load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")


def load_dataframe(response):
    data_json = response.json()
    columns = data_json[0]
    rows = data_json[1:]
    dataframe = pd.DataFrame(rows, columns=columns)
    return dataframe


## 2020 Decennial Census
# Demographic and Housing Characteristics(DHC-A): Sex and Age County-Wise Data
variable_guide_dhca = "https://api.census.gov/data/2020/dec/ddhca/variables.html"
url_dhca = "https://api.census.gov/data/2020/dec/ddhca?"
dhca_variable_dictionary = {
    "T02001_002N": "Total_Male",
    "T02001_003N": "Male_under_18",
    "T02001_004N": "Male_18_to_44",
    "T02001_005N": "Male_45_to_64",
    "T02001_006N": "Male_65_and_over",
    "T02001_007N": "Total_Female",
    "T02001_008N": "Female_under_18",
    "T02001_009N": "Female_18_to_44",
    "T02001_010N": "Female_45_to_64",
    "T02001_011N": "Male_65_and_over",
}
params_dhca = {
    "get": "NAME,T02001_002N,T02001_003N,T02001_004N,T02001_005N,T02001_006N,T02001_007N,T02001_008N,T02001_009N,T02001_010N,T02001_011N",
    "for": "county:*",
    "key": api_key,
}
response_ddhca = requests.get(url_dhca, params=params_dhca)

ddhca_df = load_dataframe(response_ddhca)

# Renaming column names
# Mapping old column names to new ones
column_mapping = {
    old_name: dhca_variable_dictionary.get(old_name, old_name)
    for old_name in ddhca_df.columns
}
ddhca_df = ddhca_df.rename(columns=column_mapping)
print(ddhca_df.head())

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
    "for": "county:*",
    "key": api_key,
}
response_ddhc = requests.get(url_dhc, params=params_dhc)

ddhc_df = load_dataframe(response_ddhc)

# Renaming column names
# Mapping old column names to new ones
column_mapping_dhc = {
    old_name: dhc_variable_dictionary.get(old_name, old_name)
    for old_name in ddhc_df.columns
}
ddhc_df = ddhc_df.rename(columns=column_mapping_dhc)

# Loading Community Resilience Estimates for Counties
params_cre = {
    "get": "NAME,PRED0_E,PRED0_PE,PRED12_E,PRED12_PE,PRED3_E,PRED3_PE",
    "for": "county:*",
    "key": api_key,
}
url = "https://api.census.gov/data/2022/cre?"
response_cre = requests.get(url, params=params_cre)

cre_dataframe = load_dataframe(response_cre)


# WRITING TO SQL DATABASE
def creating_sql_database(data, database_name, table_name):
    connection = sqlite3.connect(database_name)
    data.to_sql(table_name, connection, if_exists="replace", index=False)

    connection.commit()
    connection.close()
