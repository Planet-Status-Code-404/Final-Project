import sys
from project_404.data_collection import census_data
from project_404.data_collection import richmond
from project_404.data_collection import epa
from project_404.data_collection import utilities
from project_404.chatbot.model.agents import function_calling_agent, response_agent
from project_404.chatbot.utilities import create_data_documentation


def data_collection():
    """
    This function downloads and/or pre-process the dataset along with performing
    cleaning operations and returns the csv files in the data_collection/output_data folder.
    *For the state_list parameter please use: ["LA", "IL", "TX", "WA", "CA"]*
    """
    census_data.process_census_data_to_csv()
    richmond.clean_redlined_with_tract_data()
    richmond.combine_cvi_df()
    richmond.clean_fema_data()

def data_collection_epa(cities: list, max_rows, visualization: bool, columns_to_viz: list):
     """
    This function downloads and/or pre-process the dataset along with performing
    cleaning operations and returns the csv files in the data_collection/output_data folder
        for the EPA data only!

        Parameters:
        city: enter only list combination of ["Chicago", "Dallas", "New_Orleans", "Houston", "Los_Angeles"]
                Capitalization is important, it is case sensitive
        max_rows: Choose any positive number but expect 2-10 seconds for each row API call. This is created for you 
                    to be able to try a sample without waiting for the entire function to run.
        visualization: if you want exploratory visualization mark as True and give a list of columns to visualize
        columns_to_viz: list of column names, suggested to be between 1-3, see Readme file for column names.

        Output: creates a "EPA_Data.csv" in data_collection/output_data

    Example call: 
    app.data_collection_epa(["Chicago", "Dallas", "New_Orleans", "Houston", "Los_Angeles"], 
                            5, True, ["demographics.P_LOWINC","demographics.PCT_MINORITY"])
    """  
     list_of_dfs = []
     for city in cities:
        if city.lower() == 'chicago':
            df = epa.collect_epa_data_from(city, max_rows, f"{city}_Tract_ID.csv")
            df = utilities.clean_epa(df)
            list_of_dfs.append(df)
        else:
            df = epa.collect_epa_data_from(city, max_rows, f"{city}_Tract_ID.xlsx")
            df = utilities.clean_epa(df)
            list_of_dfs.append(df)

     merged_df = utilities.merge_dfs_to_csv(list_of_dfs, "EPA_Data.csv")

     if visualization:
         epa.visualize_data(merged_df, columns_to_viz)


def start_chatbot(ngrok_tunnel_key):
    """
    This function uses a 3-stage process whereby a user can input natural
    language that is converted into python function parameters, and
    then is summarized back to the user.

    """
    # Generate list of usable variables
    create_data_documentation()
    function_calling_bot = function_calling_agent(ngrok_tunnel_key)
    response_bot = response_agent(ngrok_tunnel_key)

    while True:
        prompt = input("\n>>> ")

        if prompt in ["q", "quit", "quit()"]:
            break

        try:
            answers = function_calling_bot.call_functions(prompt)
        except ValueError:
            answers = "Apologies, it seems that there isn't enough data for me " +\
                f"to fulfill your request, {prompt}. Please try again."
        except NameError:
            answers = "Apologies, I am having difficulty understanding your request " +\
                f"{prompt}. Please try again and make sure to use one of the provided variable names"
        except:
            answers = "Apologies, I am having difficulty understanding your request " +\
                f"{prompt}. Please try again."

        response_bot.responds_with_answers(answers)


def run():
    if len(sys.argv) != 2:
        print(f"Usage: python3 -m project_404 <data_collection> OR <climate_bot>")
        sys.exit()

    if sys.argv[1] == "data_collection":
        print("Start data collection process? (y/n)")
        response = input("\n>>> ")

        if response in ["y", "yes", "Y", "Yes"]:
            data_collection()
        else:
            sys.exit()

    if sys.argv[1] == "climate_bot":
        print("Start climate chatbot? (y/n)")
        response = input("\n>>> ")

        if response in ["y", "yes", "Y", "Yes"]:
            print("Please input Ngrok tunnel key")
            print(
                "The key should mostly resemble <https://####-##-###-###-##.ngrok-free.app>"
            )
            ngrok_tunnel_key = input("\n>>> ")

            if ngrok_tunnel_key in ["q", "quit", "quit()"]:
                sys.exit()
            else:
                print("\n\nInitializing chatbot. This will take a moment.")
                start_chatbot(ngrok_tunnel_key)

        else:
            sys.exit()
