import json
from pprint import pprint
import pandas as pd
import geopandas as gpd
from pygris import tracts
import requests
import pathlib

SOURCE_DATA = file_path = pathlib.Path(__file__).parent / "source_data"
OUTPUT_DATA = file_path = pathlib.Path(__file__).parent / "output_data"


class Tract:  # this code has been taken from agents.py
    def __init__(self):
        self.tract_shp = self.get_shapefiles()

    def get_shapefiles(self):
        states = ["LA", "IL", "TX", "WA", "CA"]

        tracts_shp = tracts(year=2020, state=states[0])
        tracts_shp["state_name"] = states[0]

        for state in states[1:]:
            state_tracts = tracts(year=2020, state=state)
            state_tracts["state_name"] = state

            tracts_shp = pd.concat([tracts_shp, state_tracts], axis=0)
        return tracts_shp


#############################################################################
# This section of the file contains data collection, processing,manipulation,#
# and cleaning functions for the Richmond Redlining dataset.                 #
#############################################################################


def clean_richmond_data():
    """
    Purpose: Get data from the Richmond Redlining Mapping Inequality dataset
    The states that we are examining are: Louisiana,Illinois, California,
    Texas, and Washington.
    Input: None
    Output: A dataframe with data for the specified list of states.
    """
    state_list = ["LA", "IL", "TX", "WA", "CA"]

    mapping_inequality = open(f"{SOURCE_DATA}/mappinginequality.json")
    richmond_data = gpd.read_file(mapping_inequality)
    richmond_dataframe = richmond_data[richmond_data["state"].isin(state_list)]
    richmond_dataframe["state"] = (
        richmond_dataframe["state"].str.lower().str.replace(" ", "_")
    )
    return richmond_dataframe


def matching_tracts():  # this code is taken from gis stack exchange and modified
    """
    Purpose: Create a new csv which has tract information for specified state
    list along with the data from the richmond redlining dataset. The states
    that we are examining are: Louisiana, Illinois, California, Texas, and
    Washington.
    Inputs: None
    Output: A dataframe with data for the specified list of states.
    """
    richmond_data_df = clean_richmond_data()
    tracts_shp_df = Tract()
    tracts_shp_df.tract_shp = tracts_shp_df.tract_shp.to_crs(richmond_data_df.crs)
    combined_tracts_df = gpd.overlay(
        tracts_shp_df.tract_shp, richmond_data_df, how="intersection"
    )
    combined_tracts_df["tract_area"] = combined_tracts_df.geometry.to_crs(
        richmond_data_df.crs
    ).area
    combined_tracts_df.drop_duplicates(subset="tract_area", keep=False, inplace=True)
    combined_tracts_df.drop(columns=["tract_area"], inplace=True)
    return combined_tracts_df


def clean_redlined_with_tract_data():
    """
    Purpose: Create a CSV file with combined information from the 2 previous functions.
    Inputs: None
    Output: CSV
    """
    redlining_with_tracts_df = matching_tracts()
    redlining_with_tracts_df.columns = (
        redlining_with_tracts_df.columns.str.lower().str.replace("geoid", "geo_id")
    )
    redlining_with_tracts_df = redlining_with_tracts_df.loc[
        :,
        ["geo_id"]
        + [col for col in redlining_with_tracts_df.columns if col != "geo_id"],
    ]  # https://saturncloud.io/blog/pandas-tips-reorder-columns/
    redlining_with_tracts_df = redlining_with_tracts_df.drop_duplicates(
        subset=["geo_id"], keep="last"
    )  # https://www.aporia.com/resources/how-to/drop-duplicate-rows-across-columns-dataframe/#:~:text=and%20PySpark%20DataFrames.-,Pandas,the%20columns%20are%20the%20same.&text=In%20some%20cases%2C%20having%20the,for%20being%20considered%20as%20duplicates.
    redlining_with_tracts_df.to_csv(
        f"{OUTPUT_DATA}/redlining_with_tracts.csv",
        index=False,
        header=True,
    )
    print("The new CSV file redlining_tract_csv was created!")


#############################################################################
# This section of the file contains data collection, processing,manipulation,#
# and cleaning functions for the Climate Vulnerability datasets.             #
#############################################################################


def clean_climate_vul_master():
    """
    Purpose:
    -Extract data from the Climate Vulnerability Index Master Overview dataset
    for the specified state list (in function).
    -Filter out columns that are not needed and since only one name needs to be
    changed other cleaning methods to filter instead of hardcoding.
    -Put the data into a pandas dataframe.
    Inputs: None
    Output: New pandas dataframe with our filtered data.
    """
    state_list = ["LA", "IL", "TX", "WA", "CA"]
    final_cvi_list = []
    climate_vul_df = pd.read_csv(f"{SOURCE_DATA}/master_cvi_data_overview.csv")
    climate_vul_df.drop(
        columns=["Baseline: All", "Baseline: Infrastructure", "Baseline: Environment"]
    )
    climate_vul_df.columns = (
        climate_vul_df.columns.str.lower()
        .str.replace(" ", "_")
        .str.replace(":", "")
        .str.replace("fips_code", "geo_id")
    )
    climate_vul_df["state"] = climate_vul_df["state"].str.strip()
    for state in state_list:
        state_data = climate_vul_df[
            climate_vul_df["state"].str.lower() == state.lower()
        ]
        final_cvi_list.append((state_data))
    if final_cvi_list:
        climate_index_df = pd.concat(final_cvi_list, ignore_index=True)
    return climate_index_df


def clean_climate_vul_indicators():
    """
    *Special note: Please note that this data source for this function
    is too big to be in the GitHub repo. However, they are both availabile
    in the dropbox.

     Purpose:
     -Extract data from the Climate Vulnerability Index Indicators dataset
     for the specified state list (in function).
     -Filter out columns that are not needed and hardcode the col names
     -Put the data into a pandas dataframe.
     Inputs: State_list (the list of states for which we want data)
     Output: New pandas dataframe with our filtered data.
    """
    state_list = ["LA", "IL", "TX", "WA", "CA"]
    final_list = []
    climate_vul_df = pd.read_csv(f"{SOURCE_DATA}/master_cvi_data_indicators.csv")
    filtered_dict = {
        "State": "state",
        "County": "county",
        "FIPS Code": "geo_id",
        "Geographic Coordinates": "geographic_coordinates",
        "Infant Mortality": "infant_mortality",
        "Child Mortality": "child_mortality",
        "Free or Reduced Price School Lunch": "free_reduced_school_lunch_price",
        "Medically Underserved Areas": "medically_underserved_areas",
        "Current Lack of Health Insurance": "current_lack_health_insurance",
        "Proximity to hospitals": "proximity_hospitals",
        "Below Poverty": "below_poverty",
        "Unemployed": "unemployed",
        "Low Income": "low_income",
        "No High School Diploma": "no_hs_diploma",
        "Single-Parent Households": "single_parent_household",
        "Minority": "minority",
        "Speaks English Less than Well": "less_english",
        "Undocumented Population": "undocumented_pop",
        "Homeless Population": "homeless_pop",
        "Veterans Population": "vet_pop",
        "Mobile Homes": "mobile_homes",
        "Food Insecurity": "food_insecurity",
        "Housing Affordability (renters)": "renter_affordability",
        "Housing Affordability (owners)": "owner_affordability",
        "HUD Public Housing": "public_housing",
        "Temperature-related mortality": "temp_mortality",
        "Deaths from climate disasters": "climate_disaster_deaths",
        "FEMA Hazard Mitigation Grants": "fema_hazard_mit_grants",
        "Cost of climate disasters": "climate_disaster_cost",
        "Urban Heat Island Extreme Heat Days": "urban_heat_isl_days",
        "Drought - Annualized Frequency": "annual_drought_freq",
        "Coastal Flooding - Annualized Frequency": "annual_coastal_flooding_freq",
        "Sea Level Rise": "sea_level_rise",
        "Hurricane - Annualized Frequency": "annual_hurricane_freq",
        "Tornado - Annualized Frequency": "annual_tornado_freq",
        "Winter Weather - Annualized Frequency": "annual_winter_weather_freq",
    }
    state_list = ["LA", "IL", "TX", "WA", "CA"]
    for state in state_list:
        state_rows = climate_vul_df[climate_vul_df["State"] == state]
        for index, row in state_rows.iterrows():
            climate_vul_dict = {}
            for key, value in filtered_dict.items():
                climate_vul_dict[filtered_dict[key]] = row[key]
                final_list.append(climate_vul_dict)
    final_cvi_df = pd.DataFrame(final_list)
    return final_cvi_df


def combine_cvi_df():
    """
    *Special note: Please note that this CSV is too big to be uploaded to GitHub.
    You can find it in the dropbox (https://www.dropbox.com/home/Planet%20Status%20Code%20404)

     Purpose:Combine the two Climate Vulnerability Index dataframes and
     produce a joint data CSV.
     Inputs: None.
     Output: CSV.
    """

    df_cvi_master = clean_climate_vul_master()
    df_cvi_indicators = clean_climate_vul_indicators()
    merged_cvi_df = pd.merge(
        df_cvi_master,
        df_cvi_indicators,
        how="inner",
        left_on=["geo_id"],
        right_on=["geo_id"],
    )  # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html
    merged_cvi_df = merged_cvi_df[
        ["geo_id"] + [col for col in merged_cvi_df.columns if col != "geo_id"]
    ]
    merged_cvi_df.to_csv(f"{OUTPUT_DATA}/merged_cvi_data.csv", index=False, header=True)
    print("The new CSV File merged_cvi_data' was created!")


###############################################################################
# This section of the file contains data collection, processing, manipulation,#
# and cleaning functions for the FEMA National Climate Index data             #
###############################################################################


def clean_fema_data():
    """
    Purpose: Get data from the FEMA National Risk Index. All the column names
    have been hardcoded.
    Inputs: None
    Output: CSV
    """
    rename_fema_dict = {  # https://saturncloud.io/blog/how-to-rename-column-and-index-with-pandas/#:~:text=Renaming%20columns%20in%20Pandas%20is,are%20the%20new%20column%20names.
        "STATE": "state",
        "COUNTY": "county",
        "COUNTYFIPS": "countyfips",
        "TRACT": "tract",
        "TRACTFIPS": "geo_id",
        "POPULATION": "population",
        "RISK_VALUE": "risk_value",
        "SOVI_SCORE": "social_vul_score",
        "RESL_SCORE": "resilience_score",
        "DRGT_EVNTS": "drought_events",
        "DRGT_RISKS": "drought_risk",
        "DRGT_EALS": "drought_expected_annual_loss_score",
        "ERQK_EVNTS": "earthquake_events",
        "ERQK_RISKS": "earthquake_risk",
        "ERQK_EALS": "earthquake_expected_annual_loss_score",
        "HAIL_EVNTS": "hail_events",
        "HAIL_RISKS": "hail_risks",
        "HAIL_EALS": "hail_expected_annual_loss_score",
        "HWAV_EVNTS": "heatwave_events",
        "HWAV_RISKS": "heatwave_risks",
        "HWAV_EALS": "heatwave_expected_annual_loss_score",
        "HRCN_EVNTS": "hurricane_events",
        "HRCN_RISKS": "hurricane_risks",
        "HRCN_EALS": "hurricane_expected_annual_loss_score",
        "LNDS_EVNTS": "landslide_events",
        "LNDS_RISKS": "landslide_risks",
        "LNDS_EALS": "landslide_expected_annual_loss_score",
        "TRND_EVNTS": "tornado_events",
        "TRND_RISKS": "tornado_risks",
        "TRND_EALS": "tornado_expected_annual_loss_score",
        "TSUN_EVNTS": "tsunami_events",
        "TSUN_RISKS": "tsunami_risks",
        "TSUN_EALS": "tsunami_expected_annual_loss_score",
        "WFIR_EVNTS": "wildfire_events",
        "WFIR_RISKS": "wildfire_risks",
        "WFIR_EALS": "wildfire_expected_annual_loss_score",
        "WNTW_EVNTS": "winter_events",
        "WNTW_RISKS": "winter_risks",
        "WNTW_EALS": "winter_annual_loss_score",
    }
    state_list = ["Louisiana", "Illinois", "Texas", "Washington", "California"]
    fema_list = []
    fema_df = pd.read_csv(f"{SOURCE_DATA}/fema_nri_censustracts.csv")
    for state in state_list:
        for index, row in fema_df.iterrows():
            if state.lower() == row["STATE"].lower():
                fema_dict = {}
                for key, value in rename_fema_dict.items():
                    fema_dict[rename_fema_dict[key]] = row[key]
                fema_list.append(fema_dict)
    final_fema_df = pd.DataFrame(fema_list)
    final_fema_df = final_fema_df[
        ["geo_id"] + [col for col in final_fema_df.columns if col != "geo_id"]
    ]  # https://saturncloud.io/blog/pandas-tips-reorder-columns/
    final_fema_df.to_csv(f"{OUTPUT_DATA}/fema_data.csv", index=False, header=True)
    print("The CSV file fema_data has been created!")
