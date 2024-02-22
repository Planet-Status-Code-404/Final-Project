import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd

load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")

# Loading Community Resilience Estimates for Counties
params_cre = {
    "get": "NAME,PRED0_E,PRED0_PE,PRED12_E,PRED12_PE,PRED3_E,PRED3_PE",
    "for": "county:*",
    "key": api_key,
}
url = "https://api.census.gov/data/2022/cre?"
response = requests.get(url, params=params_cre)

# Write data as pandas dataframe
data = response.json()

columns = data[0]
rows = data[1:]
cre_df = pd.DataFrame(rows, columns=columns)
# print(cre_df.head())

## 2020 Decennial Census
# Demographic and Housing Characteristics(DHC-A): Sex and Age County-Wise Dataset
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

# Load data in Json
ddhca_data = response_ddhca.json()
columns_ddhca = ddhca_data[0]
rows_ddhca = ddhca_data[1:]

ddhca_df = pd.DataFrame(rows_ddhca, columns=columns_ddhca)

# Renaming column names
# Mapping old column names to new ones
column_mapping = {
    old_name: dhca_variable_dictionary.get(old_name, old_name)
    for old_name in ddhca_df.columns
}
ddhca_df = ddhca_df.rename(columns=column_mapping)

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
# Load data in Json
ddhc_data = response_ddhc.json()
columns_ddhc = ddhc_data[0]
rows_ddhc = ddhc_data[1:]

ddhc_df = pd.DataFrame(rows_ddhc, columns=columns_ddhc)
# Renaming column names
# Mapping old column names to new ones
column_mapping_dhc = {
    old_name: dhc_variable_dictionary.get(old_name, old_name)
    for old_name in ddhc_df.columns
}
ddhc_df = ddhc_df.rename(columns=column_mapping_dhc)

print("ddhc_df.head()", ddhc_df.head())


# print("ddhca_df", ddhca_df.head())

# Cleaning Dataset
