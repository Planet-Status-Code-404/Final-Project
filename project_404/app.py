import sys
from project_404.chatbot.model.agents import function_calling_agent, response_agent

def data_collection():
    pass


def start_chatbot():
    function_calling_bot = function_calling_agent()
    response_bot = response_agent()
    while True:
        prompt = input(">> ")


        
        if prompt == "quit":
            break


def run():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <data_collection> OR <climate_bot>")
        sys.exit(1)

    if sys.argv[1] == "data_collection":
        print("Start data collection process? (y/n)")
        response = input(">> ")

        if response in ["y", "yes", "Y", "Yes"]:
           data_collection()
        else:
            sys.exit(1)

    if sys.argv[1] == "climate_bot":
        print("Start climate chatbot? (y/n)")
        response = input(">> ")

        if response in ["y", "yes", "Y", "Yes"]:
           start_chatbot()
        else:
            sys.exit(1)
        