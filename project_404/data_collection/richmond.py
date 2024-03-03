#still need to add some citations! 
import json
from pprint import pprint
import pandas as pd 
import geopandas as gpd
import matplotlib.pyplot as plt
from pygris import tracts
import requests
import reprlib

class Tract: #this code has been taken from agents.py
    def __init__(self):
        self.tract_shp = self.get_shapefiles()

    def get_shapefiles(self):
        states = ["LA", "IL", "TX", "WA","CA"]

        tracts_shp = tracts(year = 2020, state = states[0])
        tracts_shp["state_name"] = states[0]

        for state in states[1:]:
            state_tracts = tracts(year = 2020, state = state)
            state_tracts["state_name"] = state

            tracts_shp = pd.concat([tracts_shp, state_tracts], axis = 0)
        return tracts_shp
    
# This section of the file contains data collection, processing, manipulation, and cleaning functions
# for the Richmond Redlining Data
    
def clean_richmond_data (state_list):
    """
    Input: list of states whose data we want to explore
    Output: dictionaries with data for the specified list of states
    """
    mapping_inequality=open(r'data_collection/source_data/mappinginequality.json')
    richmond_data = gpd.read_file(mapping_inequality) 
    richmond_dataframe = richmond_data[richmond_data['state'].isin(state_list)]
    return richmond_dataframe
    

####################################################

def matching_tracts(state_list): #this code is taken from gis stack exchange and modified  
    '''
    Purpose: Create a new csv which has tract information for specified state
    list along with the data from the richmond redlining dataset. 
    Inputs: List (list of states), csv string. The case (upper/lower) should not matter.
    Output: new csv 
    '''
    richmond_data_df = clean_richmond_data(state_list)
    tracts_shp_df = Tract()
    tracts_shp_df.tract_shp = tracts_shp_df.tract_shp.to_crs(richmond_data_df.crs)
    combined_tracts_df = gpd.overlay(tracts_shp_df.tract_shp, richmond_data_df, how='intersection')
    combined_tracts_df['tract_area'] = combined_tracts_df.geometry.to_crs(richmond_data_df.crs).area # THIS WAS THE MISSING PIECE 
    combined_tracts_df.drop_duplicates(subset='tract_area', keep=False, inplace=True)
    combined_tracts_df.drop(columns=['tract_area'], inplace=True)
    return combined_tracts_df
    
def clean_redlined_with_tract_data(state_list,redlining_tract_csv:str): #combined_tract_redlining:str
    redlining_with_tracts_df = matching_tracts(state_list)
    redlining_with_tracts_df.columns = redlining_with_tracts_df.columns.str.lower().str.replace("geoid","geo_id")
    redlining_with_tracts_df = redlining_with_tracts_df[['geo_id'] + [col for col in redlining_with_tracts_df.columns if col != 'geo_id']] #https://saturncloud.io/blog/pandas-tips-reorder-columns/
    redlining_with_tracts_df.to_csv(f"{redlining_tract_csv}.csv", index=False, header=True) #taken from my pa4
    print(f"The new CSV file '{redlining_tract_csv} was created!") #do we need this in here or should we take it out?
        
# This section of the file contains data collection, processing, manipulation, and cleaning functions
# for the Climate Vulnerability datasets.

def clean_climate_vul_master (state_list:list):
    '''
    Purpose: 
    -Extract data from the Climate Vulnerability Index Master Overview dataset
    for the specified state list. 
    -Filter out columns that are not needed and since only one name needs to be
    changed use repr methods to filter instead of hardcoding! 
    -Put the data into a pandas dataframe.
    Inputs: state_list (the list of states for which we want data)
    Output: new pandas dataframe with our filtered data.
    '''
    final_cvi_list = []
    filtered_cvi_dict = {}
    climate_vul_df = pd.read_csv(r"data_collection/source_data/master_cvi_data_overview.csv")
    climate_vul_df.drop(columns=['Baseline: All','Baseline: Infrastructure',
    'Baseline: Environment'])
    climate_vul_df.columns = climate_vul_df.columns.str.lower().str.replace(" ","_").str.replace(":","")\
    .str.replace("fips_code","geo_id")
    climate_vul_df["state"] = climate_vul_df["state"].str.strip()
    print(climate_vul_df.columns)
    for state in state_list:
        state_data = climate_vul_df[climate_vul_df['state'].str.lower() == state.lower()]
        final_cvi_list.append((state_data))
    if final_cvi_list:
        climate_index_df = pd.concat(final_cvi_list, ignore_index=True)
    return climate_index_df


def clean_climate_vul_indicators(state_list):
    '''
   *Special note: Please note that this dataframe is too big to be in the Git
    repo. However, you can download it here:

    Purpose: 
    -Extract data from the Climate Vulnerability Index Indicators dataset
    for the specified state list. 
    -Filter out columns that are not needed and hardcode the col names 
    -Put the data into a pandas dataframe.
    Inputs: state_list (the list of states for which we want data)
    Output: new pandas dataframe with our filtered data.
    '''
    final_list = []
    climate_vul_df = pd.read_csv(r"data_collection/source_data/master_cvi_data_indicators.csv")
    filtered_dict = {"State":'state','County':'county','FIPS Code':'geo_id',
                     'Geographic Coordinates':'geographic_coordinates',
                     'Infant Mortality':'infant_mortality','Child Mortality':'child_mortality',
                     'Free or Reduced Price School Lunch':'free_reduced_school_lunch_price',
                     'Medically Underserved Areas':'medically_underserved_areas',
                    'Current Lack of Health Insurance':'current_lack_health_insurance',
                    'Proximity to hospitals':'proximity_hospitals','Below Poverty':'below_poverty',
                    'Unemployed':'unemployed','Low Income':'low_income',
                    'No High School Diploma':'no_hs_diploma',
                    'Single-Parent Households':"single_parent_household",
                    'Minority':'minority','Speaks English Less than Well':"less_english",
                    'Undocumented Population':'undocumented_pop', 'Homeless Population':'homeless_pop',
                    'Veterans Population':'vet_pop','Mobile Homes':'mobile_homes',
                    'Food Insecurity': 'food_insecurity','Housing Affordability (renters)':'renter_affordability',
                    'Housing Affordability (owners)':'owner_affordability','HUD Public Housing':'public_housing',
                    'Temperature-related mortality': 'temp_mortality','Deaths from climate disasters':'climate_disaster_deaths',
                    'FEMA Hazard Mitigation Grants': 'fema_hazard_mit_grants',
                    'Cost of climate disasters':'climate_disaster_cost',
                    'Urban Heat Island Extreme Heat Days':'urban_heat_isl_days',
                    'Drought - Annualized Frequency': "annual_drought_freq",
                    'Coastal Flooding - Annualized Frequency': 'annual_coastal_flooding_freq',
                    "Sea Level Rise":"sea_level_rise",
                    "Hurricane - Annualized Frequency":'annual_hurricane_freq',
                    'Tornado - Annualized Frequency': 'annual_tornado_freq',
                    'Winter Weather - Annualized Frequency': "annual_winter_weather_freq"
                    }
    for state in state_list:
        state_rows = climate_vul_df[climate_vul_df['State'] == state] 
        for index,row in state_rows.iterrows():
            climate_vul_dict = {}
            for key,value in filtered_dict.items():
                climate_vul_dict[filtered_dict[key]]= row[key]
                final_list.append(climate_vul_dict)
    final_cvi_df = pd.DataFrame(final_list)
    return final_cvi_df
    

def combine_cvi_df(merged_cvi_data:str): 
    state_list = ["LA", "IL", "TX", "WA","CA"]
    df_cvi_master = clean_climate_vul_master(state_list)
    df_cvi_indicators = clean_climate_vul_indicators(state_list)
    merged_cvi_df = pd.merge(df_cvi_master,df_cvi_indicators, how='left', left_on=['geo_id'], right_on=['geo_id']) 
    merged_cvi_df = merged_cvi_df[['geo_id'] + [col for col in merged_cvi_df.columns if col != 'geo_id']]
    merged_cvi_df.to_csv(f"{merged_cvi_data}.csv", index=False,header=True) #code taken from my PA 4! 
    print(f"The new CSV File '{merged_cvi_data}' was created!") 

# This section of the file contains data collection, processing, manipulation, and cleaning functions
# for the FEMA National Climate Index data

def clean_fema_data(state_list,fema_data:str):
    rename_fema_dict = {"STATE": "state","COUNTY":"county","COUNTYFIPS": "countyfips", #https://saturncloud.io/blog/how-to-rename-column-and-index-with-pandas/#:~:text=Renaming%20columns%20in%20Pandas%20is,are%20the%20new%20column%20names.
    "TRACT": "tract","TRACTFIPS": "geo_id","POPULATION": "population",
    "RISK_VALUE": "risk_value","SOVI_SCORE": "social_vul_score","RESL_SCORE": "resilience_score",
    "DRGT_EVNTS": "drought_events","DRGT_RISKS":"drought_risk",'DRGT_EALS': 'drought_expected_annual_loss_score',
    "ERQK_EVNTS": "earthquake_events","ERQK_RISKS":"earthquake_risk",'ERQK_EALS': "earthquake_expected_annual_loss_score",
    "HAIL_EVNTS": "hail_events","HAIL_RISKS":"hail_risks",'HAIL_EALS':'hail_expected_annual_loss_score',
    "HWAV_EVNTS":"heatwave_events","HWAV_RISKS":"heatwave_risks", "HWAV_EALS":'heatwave_expected_annual_loss_score',
    "HRCN_EVNTS":"hurricane_events","HRCN_RISKS":'hurricane_risks',"HRCN_EALS":'hurricane_expected_annual_loss_score',
    "LNDS_EVNTS":"landslide_events","LNDS_RISKS": "landslide_risks","LNDS_EALS":'landslide_expected_annual_loss_score',
    "TRND_EVNTS":"tornado_events","TRND_RISKS":"tornado_risks", "TRND_EALS":'tornado_expected_annual_loss_score',
    "TSUN_EVNTS":"tsunami_events","TSUN_RISKS":"tsunami_risks", 'TSUN_EALS':'tsunami_expected_annual_loss_score',
    "WFIR_EVNTS":"wildfire_events","WFIR_RISKS":"wildfire_risks", "WFIR_EALS":'wildfire_expected_annual_loss_score',
    "WNTW_EVNTS":"winter_events","WNTW_RISKS":"winter_risks","WNTW_EALS": 'winter_annual_loss_score'}

    fema_list = []
    fema_df = pd.read_csv(r"data_collection/source_data/fema_nri_censustracts.csv")
    # print(fema_df.columns)
    fema_df = fema_df.drop(columns=["OID_","NRI_ID","STATEFIPS","COUNTYTYPE","STCOFIPS"
    ,"AREA","RISK_SPCTL","EAL_SCORE","EAL_RATNG","EAL_SPCTL","EAL_VALT","EAL_VALB"
    ,"EAL_VALP","EAL_VALPE","EAL_VALA","ALR_VALB","ALR_VALP","ALR_VALA","ALR_NPCTL",
    "ALR_VRA_NPCTL","AVLN_EVNTS","AVLN_AFREQ","AVLN_EXP_AREA","AVLN_EXPB",
    "AVLN_EXPP","AVLN_EXPPE","AVLN_EXPT", "AVLN_HLRB", "AVLN_HLRP","AVLN_HLRR",
    "AVLN_EALB", "AVLN_EALP", "AVLN_EALPE", "AVLN_EALT", "AVLN_EALS",
    "AVLN_ALRP",  "AVLN_RISKV","AVLN_RISKS", "AVLN_RISKR", "CFLD_EVNTS",
    "CFLD_AFREQ", "CFLD_EXP_AREA", "CFLD_EXPB", "CFLD_EXPP", "CFLD_EXPPE", "CFLD_EXPT", 
    "CFLD_HLRB", "CFLD_HLRP","CFLD_HLRR", "CFLD_EALB", "CFLD_EALP", "CFLD_EALPE", 
    "CFLD_EALT", "CFLD_EALS","CFLD_EALR", "CFLD_ALRB", "CFLD_ALRP", "CFLD_RISKV", 
    "CWAV_EXPA", "CWAV_EXPT", "CWAV_HLRB","CWAV_HLRP", "CWAV_HLRA", "CWAV_HLRR", "CWAV_EALB", 
    "CWAV_EALA", "CWAV_EALS", "CWAV_EALR", "CWAV_ALRB", "CWAV_ALRP","CWAV_ALRA" ,"DRGT_EXPA", "DRGT_EXPT"
    ,"DRGT_HLRA", "DRGT_HLRR", "DRGT_EALA", "DRGT_EALR", "DRGT_ALRA",
    "ERQK_EXPB","ERQK_EXPT", "ERQK_HLRB", "ERQK_HLRP", "ERQK_HLRR","ERQK_EALB",
    "ERQK_EALR", "ERQK_ALRB", "ERQK_ALRP","HAIL_EXPB", "HAIL_EXPPE",
    "HAIL_EXPA", "HAIL_EXPT", "HAIL_HLRB", "HAIL_HLRP", "HAIL_HLRA", "HAIL_HLRR",
    "HAIL_EALB","HAIL_EALA", "HAIL_EALR", "HAIL_ALRB", "HAIL_ALRP",
    "HAIL_ALRA","HWAV_EXPB","HWAV_EXPPE", "HWAV_EXPA", "HWAV_EXPT", "HWAV_HLRB", 
    "HWAV_HLRP","HWAV_HLRA", "HWAV_HLRR", "HWAV_EALB","HWAV_EALA",
    "HWAV_EALR", "HWAV_ALRB","HWAV_ALRP", "HWAV_ALRA" , "HRCN_EXPB", "HRCN_EXPPE", 
    "HRCN_EXPA", "HRCN_EXPT", "HRCN_HLRB", "HRCN_HLRP","HRCN_HLRA", "HRCN_HLRR",
    "HRCN_EALB", "HRCN_EALA","HRCN_EALR", "HRCN_ALRB","HRCN_ALRP",
    "HRCN_ALRA","ISTM_EXPB", "ISTM_EXPPE","ISTM_EXPT", "ISTM_HLRB", "ISTM_HLRP",
    "ISTM_HLRR","ISTM_EALB","ISTM_EALS", "ISTM_EALR", "ISTM_ALRB", "ISTM_ALRP", 
    "LNDS_EXPB","LNDS_EXPPE", "LNDS_EXPT", "LNDS_HLRB","LNDS_HLRP", "LNDS_HLRR",
    "LNDS_EALB", "LNDS_EALR", "LNDS_ALRB","STATEABBRV","BUILDVALUE",
    "AGRIVALUE","RISK_SCORE","RISK_RATNG","SOVI_RATNG","SOVI_SPCTL","RESL_RATNG",
    "RESL_SPCTL","RESL_VALUE","CRF_VALUE","AVLN_ALRP","CFLD_ALR_NPCTL",
    "CFLD_RISKR","CWAV_EVNTS","CWAV_AFREQ","CWAV_EXP_AREA","CWAV_EXPB","CWAV_EXPP",
    "CWAV_EXPPE","CWAV_EALP","CWAV_EALPE","CWAV_EALT","CWAV_ALR_NPCTL","CWAV_RISKV",
    "CWAV_RISKS","CWAV_RISKR","DRGT_EALT","DRGT_ALR_NPCTL","DRGT_RISKV","DRGT_RISKR",
    "ERQK_EXPP","ERQK_EXPPE","ERQK_EALP","ERQK_EALPE","ERQK_EALT","ERQK_ALR_NPCTL",
    "ERQK_RISKV","ERQK_RISKR","HAIL_EXPP","HAIL_EALP","HAIL_EALPE","HAIL_EALT",
    "HAIL_ALR_NPCTL","HAIL_RISKV","HAIL_RISKR","HWAV_EXPP","HWAV_EALP","HWAV_EALPE",
    "HWAV_EALT","HWAV_ALR_NPCTL","HWAV_RISKV","HRCN_EXPP","HRCN_EALP","HRCN_EALPE",
    "HRCN_EALT","HRCN_ALR_NPCTL","HRCN_RISKV","HRCN_RISKR","ISTM_EVNTS",
    "ISTM_AFREQ","ISTM_EXP_AREA","ISTM_EXPP","ISTM_EALP","ISTM_EALPE","ISTM_EALT",
    "ISTM_ALR_NPCTL","ISTM_RISKV","ISTM_RISKS","ISTM_RISKR","LNDS_EXPP","LNDS_EALP",
    "LNDS_EALPE","LNDS_EALT","LNDS_ALRP","LNDS_ALR_NPCTL","LNDS_RISKV","LNDS_RISKR",    
    "LTNG_EVNTS","LTNG_AFREQ","LTNG_EXP_AREA","LTNG_EXPB","LTNG_EXPP","LTNG_EXPPE",
    "LTNG_EXPT","LTNG_HLRB","LTNG_HLRP","LTNG_HLRR","LTNG_EALB","LTNG_EALP",
    "LTNG_EALPE","LTNG_EALT","LTNG_EALS","LTNG_EALR","LTNG_ALRB","LTNG_ALRP",
    "LTNG_ALR_NPCTL","LTNG_RISKV","LTNG_RISKS","LTNG_RISKR","RFLD_EVNTS",
    "RFLD_AFREQ","RFLD_EXP_AREA","RFLD_EXPB","RFLD_EXPP","RFLD_EXPPE","RFLD_EXPA",
    "RFLD_EXPT","RFLD_HLRB","RFLD_HLRP","RFLD_HLRA","RFLD_HLRR","RFLD_EALB",
    "RFLD_EALP","RFLD_EALPE","RFLD_EALA","RFLD_EALT","RFLD_EALS","RFLD_EALR",
    "RFLD_ALRB","RFLD_ALRP","RFLD_ALRA","RFLD_ALR_NPCTL","RFLD_RISKV","RFLD_RISKS",
    "RFLD_RISKR","SWND_EVNTS","SWND_AFREQ","SWND_EXP_AREA","SWND_EXPB",
    "SWND_EXPP", "SWND_EXPPE", "SWND_EXPA", "SWND_EXPT", "SWND_HLRB", 
    "SWND_HLRP", "SWND_HLRA", "SWND_HLRR", "SWND_EALB", "SWND_EALP", "SWND_EALPE",
    "SWND_EALA", "SWND_EALT", "SWND_EALS", "SWND_EALR", "SWND_ALRB", "SWND_ALRP",
    "SWND_ALRA", "SWND_ALR_NPCTL", "SWND_RISKV", "SWND_RISKS", "SWND_RISKR",
    "TRND_EXPB", "TRND_EXPP", "TRND_EXPPE", "TRND_EXPA", "TRND_EXPT", "TRND_HLRB",
    "TRND_HLRP", "TRND_HLRA", "TRND_HLRR", "TRND_EALB", "TRND_EALP", "TRND_EALPE",
    "TRND_EALA", "TRND_EALT", "TRND_EALR", "TRND_ALRB", "TRND_ALRP", 
    "TRND_ALRA", "TRND_ALR_NPCTL", "TRND_RISKV","TRND_RISKR","TSUN_EXPB", "TSUN_EXPP", 
    "TSUN_EXPPE", "TSUN_EXPT", "TSUN_HLRB", "TSUN_HLRP", "TSUN_HLRR", "TSUN_EALB", 
    "TSUN_EALP", "TSUN_EALPE", "TSUN_EALT","TSUN_EALR", "TSUN_ALRB",
    "TSUN_ALRP", "TSUN_ALR_NPCTL", "TSUN_RISKV","TSUN_RISKR", "VLCN_EVNTS", 
    "VLCN_AFREQ", "VLCN_EXP_AREA", "VLCN_EXPB", "VLCN_EXPP", "VLCN_EXPPE", 
    "VLCN_EXPT", "VLCN_HLRB", "VLCN_HLRP", "VLCN_HLRR", "VLCN_EALB", "VLCN_EALP",
    "VLCN_EALPE", "VLCN_EALT", "VLCN_EALS", "VLCN_EALR", "VLCN_ALRB", "VLCN_ALRP",
    "VLCN_ALR_NPCTL", "VLCN_RISKV", "VLCN_RISKS", "VLCN_RISKR","WFIR_EXPB", "WFIR_EXPP",
    "WFIR_EXPPE", "WFIR_EXPA", "WFIR_EXPT", "WFIR_HLRB", "WFIR_HLRP", "WFIR_HLRA", 
    "WFIR_HLRR", "WFIR_EALB", "WFIR_EALP", "WFIR_EALPE", "WFIR_EALA", "WFIR_EALT",
    "WFIR_EALR", "WFIR_ALRB", "WFIR_ALRP", "WFIR_ALRA", "WFIR_ALR_NPCTL",
    "WFIR_RISKV","WFIR_RISKR","WNTW_EXPB", "WNTW_EXPP", "WNTW_EXPPE", "WNTW_EXPA",
    "WNTW_EXPT", "WNTW_HLRB", "WNTW_HLRP", "WNTW_HLRA", "WNTW_HLRR", "WNTW_EALB", 
    "WNTW_EALP", "WNTW_EALPE", "WNTW_EALA", "WNTW_EALT", "WNTW_EALR", 
    "WNTW_ALRB", "WNTW_ALRP", "WNTW_ALRA", "WNTW_ALR_NPCTL", "WNTW_RISKV","WNTW_RISKR",
    "NRI_VER","CFLD_RISKS","HWAV_RISKR","DRGT_AFREQ",'DRGT_EXP_AREA',
    "ERQK_AFREQ","ERQK_EXP_AREA","HAIL_AFREQ","HAIL_EXP_AREA","HWAV_AFREQ","HWAV_EXP_AREA",
    "HRCN_AFREQ","HRCN_EXP_AREA","LNDS_AFREQ","LNDS_EXP_AREA","TRND_AFREQ",
    "TRND_EXP_AREA","TSUN_AFREQ","TSUN_EXP_AREA",
    "WFIR_AFREQ", "WNTW_AFREQ","WNTW_EXP_AREA","WFIR_EXP_AREA"])
    
    for state in state_list: 
        for index,row in fema_df.iterrows():
            if state.lower() == row["STATE"].lower():
                fema_dict = {}
                for key,value in rename_fema_dict.items():
                    fema_dict[rename_fema_dict[key]]= row[key]
                fema_list.append(fema_dict)
    final_fema_df = pd.DataFrame(fema_list)
    final_fema_df = final_fema_df[['geo_id'] + [col for col in final_fema_df.columns if col != 'geo_id']] #https://saturncloud.io/blog/pandas-tips-reorder-columns/
    final_fema_df.to_csv(f"{fema_data}.csv", index=False,header=True) 
    print(f"CSV file '{fema_data}' has been created!")
    
                
                # dataframe = pd.DataFrame(fema_dict)
    # pprint(final_df)
    


     
    


    