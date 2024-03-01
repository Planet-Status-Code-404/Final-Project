import ollama # Ollama is program that allows us to create and host LLMs
from typing import List, Dict
from inflect import engine # Used to convert things like "1st" to "first" -- helpful for communicating with the LLM
from pygris import tracts # Gets census (tigris) shapefiles
import folium # Used to make leaflet interactive maps
import pandas as pd
import geopandas # Used to handle spatial data
# The idea came from similar use in R, but the use of webbrowser was infromed by this post
# https://stackoverflow.com/questions/53069033/python-how-to-open-map-created-with-folium-in-browser-when-running-application
import webbrowser
import json_repair # Useful for coercing output from the LLM to proper JSON

from chatbot.model.json_responses import json_response, VAR_NAMES
from chatbot.model.prompt_prefixes import function_agent_prefix


class agent_functions:
    """

    """

    def __init__(self):
        self.tract_shp = self.get_shapefiles()
        self.db = "SQL database"

    def _get_shapefiles(self):
        states = ["CA", "IL", "TX", "WA", "LA"]

        tracts_shp = tracts(year = 2020, state = states[0])
        tracts_shp["state_name"] = states[0]

        for state in states[1:]:
            state_tracts = tracts(year = 2020, state = state)
            state_tracts["state_name"] = state

            tracts_shp = pd.concat([tracts_shp, state_tracts], axis = 0)
        return tracts_shp
    
    def construct_from_statement(self, json_response_obj: json_response) -> str:
        """Construct FROM statement with neccessary JOINs for SQL"""
        SQL_tables = json_response_obj.SQL_tables

        tables_str = f"FROM {SQL_tables[0]} "
        if len(SQL_tables) > 1:
            for table in SQL_tables:
                tables_str += f"JOIN {table} ON {SQL_tables[0]}.geo_id = {table}.geo_id "

        return tables_str
    
    def construct_where_statement(self, json_response_obj: json_response) -> str:
        """Construct WHERE statement with for SQL"""
        conditions_dict = json_response_obj.conditions
        cond = "OR".join([cond for cond in conditions_dict.values()])

        return cond

    def request_simple_functions_data(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """
        func_name = json_response_obj.parameters["function_name"]
        column = json_response_obj.parameters["column"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        # Change to actually call from SQL
        # STATUS is the equivalent of saying no function
        # The choice to still give it a function name is for simplicity and consistency with the LLM
        if func_name == "STATUS":
            query = f"SELECT {column} {tables} WHERE {conditions}"
        else:
            query = f"SELECT {func_name}({column}) {tables} WHERE {conditions}"

        pass

    # def request_status_data(self, json_response_obj: json_response) -> str:
    #     """
    #     Construct SQL query 
    #     """
    #     func_name = json_response_obj.parameters["function_name"]
    #     select_column = json_response_obj.parameters["select_columns"]
    #     reported_variable = json_response_obj.parameters["reported_variable"]
        
    #     tables = self.construct_from_statement(json_response_obj)
    #     conditions = self.construct_where_statement(json_response_obj)

    #     query = f"SELECT {func_name}({reported_variable}) {tables} WHERE {conditions}"

    #     pass

    def request_top_k(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """
        k = json_response_obj.parameters["k"]
        select_column = json_response_obj.parameters["select_columns"]
        reported_variable = json_response_obj.parameters["reported_variable"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        query = f"SELECT {reported_variable} {tables} WHERE {conditions} ORDER"\
        f"BY {select_column} LIMIT {k}"

        pass

    def request_map(self, json_response_obj: json_response) -> str:
        """
         
        """
        #use import colour to generate a color scale for the map
        # https://pypi.org/project/colour/

        # Use fisher-jenks natural breaks
        # https://github.com/mthh/jenkspy
        pass

    def get_data(self, json_response_obj: json_response) -> str:
        """
        
        """
        if json_response_obj:
            ""
        
        pass


class function_calling_agent(ollama.Client):
    """
    Agent to convert natural language to function calls.

    """

    def __init__(self, tunnel_key) -> None:
        self.model_name = "mistral"
        self.context = None
        super().__init__(host = tunnel_key)
        

    def get_json(self, prompt: str) -> List[Dict]:
        """
        Generates a resposne from the LLM and coerces it to JSON

        """
        json_output = self.generate(
            model=self.model_name,
            prompt=prompt,
            context=self.context,
            format='json'
        )
        self.context = json_output["context"]
        
        return json_repair.loads(json_output["response"].replace("\\", ""))["queries"]

    def retry_request(
            self,
            agent_function_call: agent_functions,
            num_of_retries=1) -> agent_functions | str:
        """
        Recursively makes requests to the LLM to resolve nonmatches between the functions
        and parameters and what are available.

        Returns an agent_functions object or a string if it can't correct the issue

        """
        if not agent_function_call.correction_message:
            return agent_function_call
        if num_of_retries == 0:
            return "Could not complete request"

        # Consider making the resubmitted prompt more complicated
        # Tell it to choose from a list of potential options
        json_func_object = self.get_json(
            prompt=
            f"{agent_function_call.correction_message}\n"
            f"The possible function values are {agent_function_call.available_functions}\n"
            f"The possible parameter values are {agent_function_call.available_parameters}\n"
            "Please try again."
        )
        new_function_call = agent_functions(json_func_object)
        new_message = new_function_call.correction_needed

        if new_message:
                new_request = self.retry_request(new_function_call, num_of_retries - 1)
                return new_request

        return new_function_call

    def call_functions(self, prompt: str):
        """
        Call each function from the JSON output

        **Look to see if I can prompt the LLM to include the question matched to the JSON request

        """
        answers = []

        for i, json_func_object in enumerate(self.get_json(prompt)):
            functions = self.retry_request(agent_functions.get_data(json_func_object))

            if functions == "Could not complete request":
                return "Could not complete request"
            
            # The use of inlect.engine() was inspired by this Stack post
            # https://stackoverflow.com/questions/11180845/is-there-a-library-to-convert-integer-to-first-second-third
            answers.append(f"The {engine().ordinal(i)} answer is: {functions.get_data()}")

        return "\n".join(answers)

            