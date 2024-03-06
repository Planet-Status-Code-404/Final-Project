import pandas as pd
import pathlib

def get_variable_names():
    """
    Helper function to get the names of the variables used in the database.

    Returns (dict): Returns a dictionary of the vairable names as keys and values 
        as a list of the table it comes from and its description
    
    """ 
    data_tracker_file = pathlib.Path(__file__).parent\
    / "../data_collection/~data_documentation/variable_names.xlsx"

    data_tracker = pd.read_excel(data_tracker_file, sheet_name=None)

    var_names = {}

    for table_name in data_tracker:
        if table_name not in []: #["merged_cvi_data", "EPA_Sample_Data", "final_redlining_tract_csv"]:
            for row in data_tracker[table_name].itertuples():
                # ignore rows that have missing variable names
                try:
                    var = getattr(row, "JSON_Variable").lower().replace(",", "")
                except:
                    continue
                description = getattr(row, "Description")
                var_names[var] = [table_name.lower().replace(" ","_"), description]

    return var_names
