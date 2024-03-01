import json
from pprint import pprint
import pandas as pd 
import geopandas as gpd
from pygris import tracts
import requests

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

def clean_richmond_data (city_name, richmond_redlining: str):
    """
    Purpose: 
    Input: the name of the city whose data we want to explore
    Output: dictionaries with data for said city
    """
    city_dict = {} #build this out so all the rows can be seen in the data frame!!!
    city_list = []
    mapping_inequality=open(r'data_collection/mappinginequality.json')
    richmond_data = json.load(mapping_inequality)
    for key, data in richmond_data.items():
        if key == "features":
            for index in range(len(data)): #iterating through range of the length of the data #index #summer TA helped 
                    city_data = data[index]["properties"]["city"]
                    if city_data == city_name:
                        #  city_dict = {"properties": data[index]["properties"]}
                        city_dict = {"area_id": data[index]["properties"]["area_id"], 
                            "city": data[index]["properties"]["city"],
                            "state": data[index]["properties"]["state"],
                            "city_survey":data[index]["properties"]["city_survey"],
                            "category": data[index]["properties"]["category"],
                            "grade":data[index]["properties"]["grade"],
                            "label": data[index]["properties"]["label"],
                            "residential":data[index]["properties"]["residential"],
                            "commercial":data[index]["properties"]["commercial"],
                            "industrial":data[index]["properties"]["industrial"],
                            "fill":data[index]["properties"]["fill"],
                            "geometry_type": data[index]["geometry"]["type"],
                            "coordinates": data[index]["geometry"]["coordinates"],} #Summer TA helped 
                        # city_dict = {"property": data[index]["properties"], "geometry": data[index]["geometry"]} #summer TA helped 
                        
                        # polygon = data[index]["geometry"]["type"]
                        # tracts = gpd.read_file("/Users/kiranjivnani/Final-Project/data_collection/Boundaries - Census Tracts - 2010.geojson")
                        # joined_data = gpd.sjoin(polygon, tracts, op='intersects')
                        # for index, row in joined_data.iterrows():
                        #     print(row['tract_id'])
                        
                        # print(pygris.tract(state = "NY"))
                        
                        # ny_tract = pygris.tract(state= "NY")
                        # print(ny_tract)
                        
                        city_list.append(city_dict)

    richmond_redlining_df=pd.DataFrame(city_list)
    # pprint(dataframe)

    # richmond_redlining_df.to_csv(richmond_redlining, index=False,header=True) #code taken from geeksforgeeks
    # print(f"CSV file '{richmond_redlining}' has been created!")

##############################################################################

def clean_climate_vul_index_master (state_list):
    # final_dict = {}
    # final_list = []
    # climate_vul_df = pd.read_csv(relative_csv_path) #https://datatofish.com/import-csv-file-python-using-pandas/
    # # climate_vul_df["County"] = climate_vul_df["County"].str.strip()
    # climate_vul_df["State"] = climate_vul_df["State"].str.strip()
    # for index,row in climate_vul_df.iterrows():
    #     if state.lower()== row['State'].lower():
    #     # if state.lower() == row["State"].lower() and county.lower()==row["County"].lower():
    #         final_dict = {index: row}
    #         final_list.append(final_dict)
    #         climate_index_df = pd.DataFrame(final_list)
    # return climate_index_df
    final_list = []
    
    climate_vul_df = pd.read_csv(r"data_collection/Master CVI Dataset - overview.csv")
    climate_index_df.drop(columns=['All,Baseline','Infrastructure,Baseline',
    'Baseline: Environment'])
    climate_vul_df["State"] = climate_vul_df["State"].str.strip()
    for state in state_list:
        state_data = climate_vul_df[climate_vul_df['State'].str.lower() == state.lower()]
        final_list.append(state_data)

    if final_list:
        climate_index_df = pd.concat(final_list, ignore_index=True)
        # pd.set_option('display.max_columns', None)
        # print(climate_index_df)
        return climate_index_df

    # climate_index_df.to_csv(clean_climate_vul, index=False,header=True) #code taken from geeksforgeeks
    # print(f"CSV file '{clean_climate_vul}' has been created!")


def clean_climate_vul_indicators(state_list):
    # final_dict = {}
    # final_list = []
    # climate_vul_df = pd.read_csv(relative_csv_path) #https://datatofish.com/import-csv-file-python-using-pandas/
    # # climate_vul_df["County"] = climate_vul_df["County"].str.strip()
    # climate_vul_df["State"] = climate_vul_df["State"].str.strip()
    # for index,row in climate_vul_df.iterrows():
    #     if state.lower()== row['State'].lower():
    #     # if state.lower() == row["State"].lower() and county.lower()==row["County"].lower():
    #         final_dict = {index: row}
    #         final_list.append(final_dict)
    #         climate_index_df = pd.DataFrame(final_list)
    # return climate_index_df
    final_list = []
    climate_vul_df = pd.read_csv(r"data_collection/Master CVI Dataset - indicators.csv")
    climate_vul_df.drop(columns =['Geographic Coordinates','Self-Reported Physical Health',
    'Self-Reported Mental Health',"Drug Overdose Deaths per 100,000 People",'Alcohol Abuse',
    'Suicide Rates','Current Diabetes','Current Adult Asthma','Stroke','COPD','CHD',
   'Cancer','High Blood Pressure','Cholesterol Screening','Routine Doctor Visit',
   'Colonoscopy','Mammogram','Older Men Preventive Screening','Older Women Preventive Screening',
   'Dental Exams','COVID-19 Deaths','Hepatitis A','Hepatitis B','HIV','Chlamydia','Gonorrhea'
   ,'Syphillis','Childhood Asthma','ADHD Prevalence','ADHD Treatment','Veterans Population',
   ,'Lane miles per capita','Road Quality and Maintenance','Performance,Bridge Quality and Maintenance',
   'Walkability','Bikability','Residential Energy Cost Burden','Share of energy from fossil fuels',
   'EV Charging Stations','Modified Retail Food Environment Index','Payday lending rank',
   ,'Tax Base: Median Real Estate Taxes Paid','Voter Turnout 2020','Public Library Locations'
    'Total vehicle miles traveled per capita','Passenger vehicle miles traveled per capita',
    'Truck vehicle miles traveled per capita','Heavy Duty Vehicle vehicle miles traveled per capita',
    'Proximity to Ports','Rail Crossings','Traffic Proximity and Volume','National Transportation Noise Map',
    'Risk-Screening Environmental Indicators (RSEI)','Air Tox Respiratory','Air Tox Neurological','Air Tox Liver','Air Tox Developmental',
    'Air Tox Reproductive','Air Tox Kidney','Air Tox Immunological','Air Tox Thyroid',
    'Air Tox Total Cancer Risk','Black Carbon','Agricultural pesticides','Lead Paint: % housing units built before 1960',
    ,'Superfund Sites','Brownfields','Stream Toxicity Risk-Screening Environmental Indicators (RSEI)',
    'Proximity to facilities participating in air markets','NPL sites','Hazardous Waste Management Facilities (TSDFs)',
    'Hazardous Waste Generator/Incinerators','Facilities with Enforcement or Violation',
    'Landfills','TSCA Facilities','Risk Management Plan Facilities','Chemical Manufacturers',
    'Metal Recyclers,Active Oil and Gas Wells','Annual average PM2.5 concentrations','NO2 concentration',
    'Ozone concentration,Parks and Greenspace','Impermeable Surfaces','Forest Land Cover',
    ,'Increase in childhood asthma incidence','Aedes aldopictus dengue transmission increase',
    'Aedes aegypti dengue transmission increase','Aedes aegypti zika transmission increase',
    'Property taxes expected to be lost by 2045 due to chronic inundation','High-Risk Jobs Productivity (% Change)',
    'Yields (% change)','Outdoor workers - work days at risk per year','Expected Annual Loss - Agriculture Value',
    'Expected Annual Loss - Building Value','Expected Annual Loss - Population Equivalence',
    'Residential Energy Expenditures (% change)','Share of Jobs in Agriculture','Methane Emissions',
    'Property Crimes (% change)','Violent Crimes (% change)','Cold Wave - Annualized Frequency,Days with maximum temperature above 35 C',
    'Days with maximum temperature above 40C','Frost Days','Maximum of maximum temperatures','Mean temperature'
    ,'Drought - Annualized Frequency','Consecutive Dry Days','Wildfire - Annualized Frequency','Surface PM2.5',
    'Snowfall','Standardized Precip Index','Total Precipitation','Coastal Flooding - Annualized Frequency',
    'Riverine Flooding - Annualized Frequency','Sea Level Rise','Hurricane - Annualized Frequency',
    'Tornado - Annualized Frequency','Winter Weather - Annualized Frequency'])
    climate_vul_df["State"] = climate_vul_df["State"].str.strip()

    for state in state_list:
        state_data = climate_vul_df[climate_vul_df['State'].str.lower() == state.lower()]
        final_list.append(state_data)

    if final_list:
        climate_index_df = pd.concat(final_list, ignore_index=True)
        # pd.set_option('display.max_columns', None)
        # print(climate_index_df)
        return climate_index_df

def combine_CVI_df(df_cvi_master,df_cvi_indicators,state_list,merged_cvi_data:str): 
    df_cvi_master = clean_climate_vul_index_master(state_list)
    df_cvi_indicators = clean_climate_vul_indicators(state_list)

    merged_cvi_df = pd.merge(df_cvi_master,df_cvi_indicators how='left', left_on=['FIPS Code'], right_on=['FIPS Code']) 

    merged_cvi_df.to_csv(merged_cvi_data, index=False,header=True) #code taken from PA 4! 
    print(f"The CSV file '{merged_cvi_data.csv}' was created!") 

##############################################################################

def clean_fema_data(relative_csv_path,county,state,fema_data):
    rename_fema_dict = {"STATE": "State","COUNTY":"County","COUNTYFIPS": "Countyfips", #https://saturncloud.io/blog/how-to-rename-column-and-index-with-pandas/#:~:text=Renaming%20columns%20in%20Pandas%20is,are%20the%20new%20column%20names.
    "TRACT": "Tract","TRACTFIPS": "Tractfips","POPULATION": "Population",
    "RISK_VALUE": "Risk_value","SOVI_SCORE": "Social_vul_score","RESL_SCORE": "Resilience_score",
    "DRGT_EVNTS": "Drought_events","DRGT_AFREQ": "Drought_area_freq","DRGT_EXP_AREA": "Drought_experience_area",
    "DRGT_RISKS":"Drought_risk","ERQK_EVNTS": "Earthquake_events","ERQK_AFREQ":"Earthquake_area_freq",
    "ERQK_EXP_AREA":"Earthquake_experience_area","ERQK_RISKS":"Earthquake_risk","HAIL_EVNTS": "Hail_events",
    "HAIL_AFREQ":"Hail_area_freq","HAIL_EXP_AREA":"Hail_experience_area","HAIL_RISKS":"Hail_risks",
    "HWAV_EVNTS":"Heatwave_events","HWAV_AFREQ":"Heatwave_area","HWAV_EXP_AREA":'Heatwave_area_exposure',
    "HWAV_RISKS":"Heatwave_risks", "HRCN_EVNTS":"Hurricane_events","HRCN_AFREQ": "Hurriceane_freq",
    "HRCN_EXP_AREA":"Hurricane_exposure_area","HRCN_RISKS":'Hurricane_risks',"LNDS_EVNTS":"Landslide_events",
    "LNDS_AFREQ": 'Landslide_area_freq',"LNDS_EXP_AREA":"Landslide_exposure_area",
    "LNDS_RISKS": "Landslide_risks","TRND_EVNTS":"Tornado_events","TRND_AFREQ":"Tornado_area_freq",
    "TRND_EXP_AREA":"Tornado_exposure_area","TRND_RISKS":"Tornado_risks","TSUN_EVNTS":"Tsunami_events",
    "TSUN_AFREQ":"Tsunami_area_freq","TSUN_EXP_AREA":"Tsunami_exposure_area",
    "TSUN_RISKS":"Tsunami_risks","WFIR_EVNTS":"Wildfire_events","WFIR_AFREQ":"Wildfire_area_freq",
    "WFIR_EXP_AREA":"Wildfire_exposure_area","WFIR_RISKS":"Wildfire_risks",
    "WNTW_EVNTS":"Winter_events","WNTW_AFREQ":"Winter_area_freq","WNTW_EXP_AREA":"Winter_exposure_area",
    "WNTW_RISKS":"Winter_risks"}
    # fema_dict = {}
    fema_list = []
    fema_df = pd.read_csv(relative_csv_path)
    fema_df = fema_df.drop(columns=["OID_","NRI_ID","STATEFIPS","COUNTYTYPE","STCOFIPS"
    ,"AREA","RISK_SPCTL","EAL_SCORE","EAL_RATNG","EAL_SPCTL","EAL_VALT","EAL_VALB"
    ,"EAL_VALP","EAL_VALPE","EAL_VALA","ALR_VALB","ALR_VALP","ALR_VALA","ALR_NPCTL",
    "ALR_VRA_NPCTL","AVLN_EVNTS","AVLN_AFREQ","AVLN_EXP_AREA","AVLN_EXPB",
    "AVLN_EXPP","AVLN_EXPPE","AVLN_EXPT", "AVLN_HLRB", "AVLN_HLRP","AVLN_HLRR",
    "AVLN_EALB", "AVLN_EALP", "AVLN_EALPE", "AVLN_EALT", "AVLN_EALS","AVLN_EALR",
    "AVLN_ALRB", "AVLN_ALRP",  "AVLN_RISKV","AVLN_RISKS", "AVLN_RISKR", "CFLD_EVNTS",
    "CFLD_AFREQ", "CFLD_EXP_AREA", "CFLD_EXPB", "CFLD_EXPP", "CFLD_EXPPE", "CFLD_EXPT", 
    "CFLD_HLRB", "CFLD_HLRP","CFLD_HLRR", "CFLD_EALB", "CFLD_EALP", "CFLD_EALPE", 
    "CFLD_EALT", "CFLD_EALS","CFLD_EALR", "CFLD_ALRB", "CFLD_ALRP", "CFLD_RISKV", 
    "CWAV_EXPA", "CWAV_EXPT", "CWAV_HLRB","CWAV_HLRP", "CWAV_HLRA", "CWAV_HLRR", "CWAV_EALB", 
    "CWAV_EALA", "CWAV_EALS", "CWAV_EALR", "CWAV_ALRB", "CWAV_ALRP","CWAV_ALRA" ,"DRGT_EXPA", "DRGT_EXPT"
    ,"DRGT_HLRA", "DRGT_HLRR", "DRGT_EALA",  "DRGT_EALS", "DRGT_EALR", "DRGT_ALRA",
    "ERQK_EXPB","ERQK_EXPT", "ERQK_HLRB", "ERQK_HLRP", "ERQK_HLRR","ERQK_EALB",
    "ERQK_EALS","ERQK_EALR", "ERQK_ALRB", "ERQK_ALRP","HAIL_EXPB", "HAIL_EXPPE",
    "HAIL_EXPA", "HAIL_EXPT", "HAIL_HLRB", "HAIL_HLRP", "HAIL_HLRA", "HAIL_HLRR",
    "HAIL_EALB","HAIL_EALA", "HAIL_EALS", "HAIL_EALR", "HAIL_ALRB", "HAIL_ALRP",
    "HAIL_ALRA","HWAV_EXPB","HWAV_EXPPE", "HWAV_EXPA", "HWAV_EXPT", "HWAV_HLRB", 
    "HWAV_HLRP","HWAV_HLRA", "HWAV_HLRR", "HWAV_EALB","HWAV_EALA", "HWAV_EALS",
    "HWAV_EALR", "HWAV_ALRB","HWAV_ALRP", "HWAV_ALRA" , "HRCN_EXPB", "HRCN_EXPPE", 
    "HRCN_EXPA", "HRCN_EXPT", "HRCN_HLRB", "HRCN_HLRP","HRCN_HLRA", "HRCN_HLRR",
    "HRCN_EALB", "HRCN_EALA",  "HRCN_EALS" ,"HRCN_EALR", "HRCN_ALRB","HRCN_ALRP",
    "HRCN_ALRA","ISTM_EXPB", "ISTM_EXPPE","ISTM_EXPT", "ISTM_HLRB", "ISTM_HLRP",
    "ISTM_HLRR","ISTM_EALB","ISTM_EALS", "ISTM_EALR", "ISTM_ALRB", "ISTM_ALRP", 
    "LNDS_EXPB","LNDS_EXPPE", "LNDS_EXPT", "LNDS_HLRB","LNDS_HLRP", "LNDS_HLRR",
    "LNDS_EALB",  "LNDS_EALS", "LNDS_EALR", "LNDS_ALRB","STATEABBRV","BUILDVALUE",
    "AGRIVALUE","RISK_SCORE","RISK_RATNG","SOVI_RATNG","SOVI_SPCTL","RESL_RATNG",
    "RESL_SPCTL","RESL_VALUE","CRF_VALUE","AVLN_ALR_NPCTL","CFLD_ALR_NPCTL",
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
    "TRND_EALA", "TRND_EALT", "TRND_EALS", "TRND_EALR", "TRND_ALRB", "TRND_ALRP", 
    "TRND_ALRA", "TRND_ALR_NPCTL", "TRND_RISKV","TRND_RISKR","TSUN_EXPB", "TSUN_EXPP", 
    "TSUN_EXPPE", "TSUN_EXPT", "TSUN_HLRB", "TSUN_HLRP", "TSUN_HLRR", "TSUN_EALB", 
    "TSUN_EALP", "TSUN_EALPE", "TSUN_EALT", "TSUN_EALS", "TSUN_EALR", "TSUN_ALRB",
    "TSUN_ALRP", "TSUN_ALR_NPCTL", "TSUN_RISKV","TSUN_RISKR", "VLCN_EVNTS", 
    "VLCN_AFREQ", "VLCN_EXP_AREA", "VLCN_EXPB", "VLCN_EXPP", "VLCN_EXPPE", 
    "VLCN_EXPT", "VLCN_HLRB", "VLCN_HLRP", "VLCN_HLRR", "VLCN_EALB", "VLCN_EALP",
    "VLCN_EALPE", "VLCN_EALT", "VLCN_EALS", "VLCN_EALR", "VLCN_ALRB", "VLCN_ALRP",
    "VLCN_ALR_NPCTL", "VLCN_RISKV", "VLCN_RISKS", "VLCN_RISKR","WFIR_EXPB", "WFIR_EXPP",
    "WFIR_EXPPE", "WFIR_EXPA", "WFIR_EXPT", "WFIR_HLRB", "WFIR_HLRP", "WFIR_HLRA", 
    "WFIR_HLRR", "WFIR_EALB", "WFIR_EALP", "WFIR_EALPE", "WFIR_EALA", "WFIR_EALT",
    "WFIR_EALS", "WFIR_EALR", "WFIR_ALRB", "WFIR_ALRP", "WFIR_ALRA", "WFIR_ALR_NPCTL",
    "WFIR_RISKV","WFIR_RISKR","WNTW_EXPB", "WNTW_EXPP", "WNTW_EXPPE", "WNTW_EXPA",
    "WNTW_EXPT", "WNTW_HLRB", "WNTW_HLRP", "WNTW_HLRA", "WNTW_HLRR", "WNTW_EALB", 
    "WNTW_EALP", "WNTW_EALPE", "WNTW_EALA", "WNTW_EALT", "WNTW_EALS", "WNTW_EALR", 
    "WNTW_ALRB", "WNTW_ALRP", "WNTW_ALRA", "WNTW_ALR_NPCTL", "WNTW_RISKV","WNTW_RISKR",
    "NRI_VER","CFLD_RISKS","HWAV_RISKR"])
    # for col in fema_df.columns:
    #     print(col)
    for index,row in fema_df.iterrows():
        if state.lower() == row["STATE"].lower() and county.lower()==row["COUNTY"].lower():
            fema_dict = {}
            for key,value in rename_fema_dict.items():
                # print(value)
                fema_dict[rename_fema_dict[key]]= row[key]
            fema_list.append(fema_dict)
    final_fema_df = pd.DataFrame(fema_list)
                
                # dataframe = pd.DataFrame(fema_dict)
    # pprint(final_df)
    final_fema_df.to_csv(fema_data, index=False,header=True) #code taken from geeksforgeeks
    print(f"CSV file '{fema_data.csv}' has been created!")


     
    


    