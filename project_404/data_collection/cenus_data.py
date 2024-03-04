import requests
import json
import pandas as pd
from pathlib import Path


def load_dataframe(response):
    """
    Convert JSON response to a pandas DataFrame.

    Parameters:
    - response (Response): The JSON response object obtained from an API request.

    Returns:
    - dataframe (DataFrame): A pandas DataFrame containing the data from the JSON response.
    """
    data_json = response.json()
    columns = data_json[0]
    rows = data_json[1:]
    dataframe = pd.DataFrame(rows, columns=columns)
    return dataframe


# Dictionary consisting of Census State codes for targetted states
state_code_dictionary = {
    "Illinois": "17",
    "Louisiana": "22",
    "Washington": "53",
    "Florida": "12",
    "California": "06",
}

## DATASET 1: Demographic Characteristics(DP)- Population Distribution Race Wise
variable_guide_dp = "https://api.census.gov/data/2020/dec/dp/variables.html"
url_dp = "https://api.census.gov/data/2020/dec/dp?"
dp_dictionary = {
    "DP1_0078C": "white_population",
    "DP1_0079C": "black_african_american_population",
    "DP1_0080C": "american_indian_alaskan_native_population",
    "DP1_0081C": "asian_population",
    "DP1_0082C": "native_hawaiian_and_other_pacific_islander_population",
    "DP1_0083C": "Other_race_population",
}
params_dp = {
    "get": "NAME,DP1_0078C,DP1_0079C,DP1_0080C,DP1_0081C,DP1_0082C,DP1_0083C",
    "for": "TRACT:*",
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

## DATASET 2
# Demographic and Housing Characteristics(DHC): Race and Housing Characteristics
variable_guide_dhc = "https://api.census.gov/data/2020/dec/dhc/variables.html"
url_dhc = "https://api.census.gov/data/2020/dec/dhc?"
dhc_variable_dictionary = {
    "H12A_002N": "owner_occuppied_white",
    "H12A_010N": "renter_occupied_white",
    "H12B_002N": "owner_occupied_black_or_african_american",
    "H12B_010N": "renter_occupied_black_or_african_american",
    "H12C_002N": "owner_occuppied_american_indian_alaska_native",
    "H12C_010N": "renter_occupied_american_indian_alaska_native",
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

## DATASET 3: Community Resilience Estimates
# Loading Community Resilience Estimates for Counties
cre_dictionary = {
    "PRED0_E": "estimated_number_of_individuals_with_zero_components_of_social_vulnerability",
    "PRED0_PE": "rate_of_individuals_with_zero_components_of_social_vulnerability",
    "PRED12_E": "estimated_number_of_individuals_with_one_two_components_of_social_vulnerability",
    "PRED12_PE": "rate_of_individuals_with_one_two_components_of_social_vulnerability",
    "PRED3_E": "estimated_number_of_individuals_with_three_or_more_components_of_social_vulnerability",
    "PRED3_PE": "rate_of_individuals_with_three_or_more_components_of_social_vulnerability",
}
params_cre = {
    "get": "NAME,PRED0_E,PRED0_PE,PRED12_E,PRED12_PE,PRED3_E,PRED3_PE",
    "for": "TRACT:*",
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


## Data Cleaning and Appending to Dataframe
# Adding the Census_Tract_ID
def add_geo_id(dataframe, state_column, county_column, tract_column):
    """
    Adds a new column 'geo_id' to the DataFrame by concatenating state,
    county, and tract codes.

    Parameters:
    - dataframe (DataFrame): The pandas DataFrame to which the new column will be added.
    - state_column (str): The name of the column containing state codes.
    - county_column (str): The name of the column containing county codes.
    - tract_column (str): The name of the column containing tract codes.

    Returns:
    - dataframe (DataFrame): The modified DataFrame with the new 'Census_Tract_ID' column.
    """
    # Convert columns to strings
    dataframe[state_column] = dataframe[state_column].astype(str)
    dataframe[county_column] = dataframe[county_column].astype(str)
    dataframe[tract_column] = dataframe[tract_column].astype(str)

    # Create new column 'geo_id' containing concatenated values
    dataframe["geo_id"] = (
        dataframe[state_column] + dataframe[county_column] + dataframe[tract_column]
    )
    return dataframe


compiled_dataframe_dp = add_geo_id(
    compiled_dataframe_dp,
    "state",
    "county",
    "tract",
)
compiled_dataframe_dhc = add_geo_id(
    compiled_dataframe_dhc,
    "state",
    "county",
    "tract",
)
compiled_dataframe_cre = add_geo_id(
    compiled_dataframe_cre,
    "state",
    "county",
    "tract",
)

# Merging Dataframes and writing to the CSV file
# Merge the first two DataFrames
dataset_one_and_two = pd.merge(
    compiled_dataframe_dp,
    compiled_dataframe_dhc,
    on=["geo_id", "NAME", "state", "county", "tract"],
    how="outer",
)
# Merge the third DataFrame with the merged result
census_dataframe = pd.merge(
    dataset_one_and_two,
    compiled_dataframe_cre,
    on=["geo_id", "NAME", "state", "county", "tract"],
    how="outer",
)
census_dataframe[["Census_Tract", "County_Name", "State_Name"]] = census_dataframe[
    "NAME"
].str.split("; ", expand=True)
census_dataframe.drop(columns=["Census_Tract", "NAME"], inplace=True)

# Remove leading and trailing whitespaces
census_dataframe["State_Name"] = census_dataframe["State_Name"].str.strip()
census_dataframe["County_Name"] = census_dataframe["County_Name"].str.strip()

# Rearranging Columns
desired_columns = [
    "geo_id",
    "state",
    "State_Name",
    "county",
    "County_Name",
    "tract",
]
remaining_columns = [
    col for col in census_dataframe.columns if col not in desired_columns
]
new_order = desired_columns + remaining_columns
final_merged_df = census_dataframe[new_order]

# Exporting dataframe to csv file
output_path = Path(__file__).resolve().parent / "output_data"
output_path.mkdir(parents=True, exist_ok=True)
final_merged_df.to_csv(output_path / "census_data.csv", index=False)
