import json
from pprint import pprint
import pandas as pd 
def clean_richmond_data (city_name):
    """
    Purpose: 
    Input: the name of the city whose data we want to explore
    Output: dictionaries with data for said city
    """
    city_dict = {} #build this out so all the rows can be seen in the data frame!!!
    city_list = []
    mapping_inequality=open('data_collection/mappinginequality.json')
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
                        city_list.append(city_dict)

    dataframe=pd.DataFrame(city_list)
    pprint(dataframe)

def clean_climate_vul_index (relative_csv_path,county,state):
    final_dict = {}
    climate_vul_df = pd.read_csv(relative_csv_path) #https://datatofish.com/import-csv-file-python-using-pandas/
    climate_vul_df["County"] = climate_vul_df["County"].str.strip()
    climate_vul_df["State"] = climate_vul_df["State"].str.strip()
    for index,row in climate_vul_df.iterrows():
        if state.lower() == row["State"].lower() and county.lower()==row["County"].lower():
            final_dict = {index: row}
    pprint(final_dict)

def clean_fema_data(relative_csv_path,county,state):
    fema_dict = {}
    fema_df = pd.read_csv(relative_csv_path)
    for col in fema_df.columns:
        print(col)


     
    

     
    


    