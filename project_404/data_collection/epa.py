import pandas as pd
import requests
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt 

def collect_epa_data_from(city, max_rows, data_file):
    """
    Collects EPA data for a given city and stores it in a DataFrame.

    Parameters:
    - city: City name as a string.
    - max_rows: Maximum number of rows of data to collect.
    - data_file: Path to the file containing FIPS codes.

    Returns:
    - DataFrame with collected data.
    """

    #Only Chicago fips codes are in a cvs file and formatted differently.
    if city.lower() == 'chicago':
        fips_codes_df = pd.read_csv(f"project_404/data_collection/source_data/{data_file}")
        fips_codes_df['Processed'] = fips_codes_df.iloc[:, 0].apply(lambda x: str(int(x * 100)).ljust(6, '0'))
        base_fips = "17031"
        fips_codes = {base_fips + processed_id for processed_id in fips_codes_df['Processed']}
    else:
        fips_codes_df = pd.read_excel(f"project_404/data_collection/source_data/{data_file}", header=None, engine='openpyxl')
        fips_codes = set(fips_codes_df[0].astype(str).str.pad(width=11, side='left', fillchar='0'))
    
    # DataFrame to store all results
    data = pd.DataFrame()
    
    # Initialize counters for tracking API calls
    success_count = 0
    fail_count = 0
    
    for i, fips_code in enumerate(fips_codes):
        if i >= max_rows:
            break  # Exit the loop after reaching max_calls

        # Construct the API URL for data
        url = f"https://ejscreen.epa.gov/mapper/ejscreenRESTbroker1.aspx?namestr={fips_code}&geometry=&distance=&unit=9035&areatype=tract&areaid={fips_code}&f=json"
        response = requests.get(url)
        
        json_data = response.json()
        if 'data' in json_data:
            df = pd.json_normalize(json_data['data'])
            data = pd.concat([data, df], ignore_index=True)
            success_count += 1
        else:
            fail_count += 1

    print(f"{city}: Success: {success_count}, Failures: {fail_count}")
    return data

def visualize_data(df: pd.DataFrame, columns: list):
    """
    Generates a pairplot from the given DataFrame for preliminary understanding of the data. 

    Parameters:
    - df: DataFrame to visualize.
    - columns: List of column names to be visualized.

    Returns:
    - None.
    """
    # If you don't already have seaborn
    # %pip install --upgrade seaborn
    # %pip install --upgrade numpy


    # If you don't already have seaborn
    # %pip install --upgrade seaborn
    # %pip install --upgrade numpy

    # Setting the theme
    sns.set_theme(style='darkgrid', palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc=None)

    # Convert to numeric
    df[columns] = df[columns].apply(pd.to_numeric)

    # Generate the pairplot
    sns.pairplot(df, vars=columns, height=3)
    
    # Display the plot
    plt.show()
    

