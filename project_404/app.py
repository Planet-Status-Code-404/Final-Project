import sys
from project_404.data_collection import census_data
from project_404.chatbot.model.agents import function_calling_agent, response_agent


def data_collection():
    """
    This function downloads and/or pre-process the dataset along with performing
    cleaning operations and returns the csv files in the data_collection/output_data folder.
    """
    census_data.process_census_data_to_csv()


def start_chatbot(ngrok_tunnel_key):
    """
    This function uses a 3-stage process whereby a user can input natural
    language that is converted into python function parameters, and
    then is summarized back to the user.

    """
    function_calling_bot = function_calling_agent(ngrok_tunnel_key)
    response_bot = response_agent(ngrok_tunnel_key)

    while True:
        prompt = input("\n>>> ")

        if prompt in ["q", "quit", "quit()"]:
            break

        answers = function_calling_bot.call_functions(prompt)
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
                start_chatbot(ngrok_tunnel_key)

        else:
            sys.exit()
