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

# Loading the

# Cleaning Dataset
