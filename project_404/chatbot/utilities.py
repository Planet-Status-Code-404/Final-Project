import pandas as pd
import pathlib


def get_variable_names():
    """
    Helper function to get the names of the variables used in the database.

    Returns (dict): Returns a dictionary of the vairable names as keys and values
        as a list of the table it comes from and its description

    """
    data_tracker_file = (
        pathlib.Path(__file__).parent
        / "../data_collection/~data_documentation/variable_names.xlsx"
    )

    data_tracker = pd.read_excel(data_tracker_file, sheet_name=None)

    var_names = {}

    for table_name in data_tracker:
        if (
            table_name not in []
        ):  # ["merged_cvi_data", "EPA_Sample_Data", "final_redlining_tract_csv"]:
            for row in data_tracker[table_name].itertuples():
                # ignore rows that have missing variable names
                try:
                    var = getattr(row, "JSON_Variable").lower().replace(",", "")
                except:
                    continue
                description = getattr(row, "Description")
                var_names[var] = [table_name.lower().replace(" ", "_"), description]

    return var_names


def generate_standard_variable_names():
    """
    Creates a dictionary of variables with standard, generic names taking the
    format of psc_###. Outputs this standardized var dictionary and a traslation
    dictionary to convert back to the real values.

    """
    real_varlist = get_variable_names()
    var_crosswalk = {}
    standard_varlist = {}

    i = 0
    for var_name, table_and_desc in real_varlist.items():
        if table_and_desc[1].strip().lower() == "for internal use only":
            continue
        var_crosswalk[f"psc_{i}"] = var_name
        standard_varlist[f"psc_{i}"] = table_and_desc

        i += 1

    return standard_varlist, var_crosswalk


def create_data_documentation():
    """
    Generate a data dicitonary mapping the standardized variable names to their
    descriptions, tables, and original names. Outputs an .xslx file.

    """

    standard_varlist, var_crosswalk = generate_standard_variable_names()

    for std_var in standard_varlist:
        standard_varlist[std_var].append(var_crosswalk[std_var])

    std_df = pd.DataFrame.from_dict(standard_varlist, orient="index")
    std_df = std_df[[1, 2, 0]]
    std_df.columns = ["description", "original variable name", "dataset"]
    std_df.index.name = "variable name"
    std_df["description"] = std_df["description"].str.replace("\n", " ").str.strip()
 
    pd.DataFrame.to_excel(std_df, sheet_name="Documentation",
                         excel_writer=pathlib.Path(__file__).parent / "~Documentation/variable_names.xlsx")