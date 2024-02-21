from urllib.request import urlopen
import json 
import pandas as pd
import pprint

#API = email=onurcan@uchicago.edu&key=dunmallard98

# store the URL in url as  
# parameter for urlopen 
# url = "https://api.github.com"
# cook_county_control_sites = "https://aqs.epa.gov/data/api/list/sitesByCounty?email=onurcan@uchicago.edu&key=dunmallard98&state=17&county=031"

# # store the response of URL 
# response = urlopen(cook_county_control_sites)  
# cook_county = json.loads(response.read())

# cook_county = cook_county[cook_county['value_represented'] is not None]

# print(cook_county)

epa_tri = "https://ejscreen.epa.gov/mapper/ejscreenRESTbroker1.aspx?namestr=Chicago&geometry=&distance=&unit=9035&areatype=city&areaid=1714000&f=json"
tri_response= urlopen(epa_tri)
tri_data = json.loads(tri_response.read())

print(tri_data)