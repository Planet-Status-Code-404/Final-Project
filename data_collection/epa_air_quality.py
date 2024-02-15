from urllib.request import urlopen
import json 
import pandas as pd
import pprint

#API = email=onurcan@uchicago.edu&key=dunswift96

# store the URL in url as  
# parameter for urlopen 
url = "https://api.github.com"
cook_county_control_sites = "https://aqs.epa.gov/data/api/list/sitesByCounty?email=onurcan@uchicago.edu&key=dunswift96&state=17&county=031"

# store the response of URL 
response = urlopen(cook_county_control_sites)  
cook_county = json.loads(response.read())

cook_county = cook_county[cook_county['value_represented'] is not None]

print(cook_county)
