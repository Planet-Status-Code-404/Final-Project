import ollama # Ollama is program that allows us to create and host LLMs
import json
import json_repair # Useful for coercing output from the LLM to proper JSON
from typing import List, Dict
from inflect import engine # Used to convert things like "1st" to "first" -- helpful for communicating with the LLM
from matplotlib.colors import is_color_like # Used to determine if something is a color
from pygris import tracts # Gets census (tigris) shapefiles
import folium # Used to make leaflet interactive maps
import pandas as pd
import geopandas # Used to handle spatial data
# The idea came from similar use in R, but the use of webbrowser was infromed by this post
# https://stackoverflow.com/questions/53069033/python-how-to-open-map-created-with-folium-in-browser-when-running-application
import webbrowser

# Dictionary to define the available functions and whether they are simple or complex
FUNCTIONS = {
    "simple": {"SUM", "COUNT", "MAX", "MIN", "MEAN", "MEDIAN"},

    "complex": {
        "FIND_TOP_K", # The top k of some parameter
        "STATUS", # What is the state of some parameter with or without some condition
        "MAP" # Generate a map based on the parameters and conditions
    }
}

# Dictionary to define all the available variable names and which table they're in
VAR_NAMES = {
    "var_name": "SQL table name",
    "climate vulnerability index": "idk"
}

#Dictionary to define the potential errors that may be raised due to issues in JSON output
ERRORS = {
    "invalid function name": "The 'function_name' outputted to JSON was not one of the valid functions listed",
    "invalid function format": "The structure of the JSON output missed an important and required aspect necessary to output the correct response", 
    "invalid parameter name": "The 'parameter' outputted to JSON was not one of the valid parameters listed"
}

DEFAULT_MAP_COLOR = "Blue"

NGROK_TUNNEL_KEY = ""


class json_response:
    """
    A single function json object outputted from a function calling agent.
    Parses the inputted JSON and assign the function name, parameters, and
    conditions associated with the function.

    """

    def __init__(self, json_object: str):
        
        self.func_name = json_object["function_name"].upper()
        self.type = self._set_type()
        self.errors = []

        self.set_parameters(json_object)
        self.set_conditions(json_object)

    def is_available_function(self):
        """
        Verifies that the function of the function call is a legal function.

        Returns:

        """
        return self.func_name in FUNCTIONS["simple"] or\
            self.func_name in FUNCTIONS["complex"]
    
    def _set_type(self):
        if not self.is_available_function():
            return None
        if self.func_name not in FUNCTIONS["simple"]:
            return "complex"
        return "simple" 
    
    def valid_color_for_map(self, color_str: str) -> None :
        """
        Need to check the "color" parameter to determine if it is a valid color to be mapped
        """
        if is_color_like(color_str):
            return color_str
        
        dual_color = color_str.split("-")
        for color in dual_color:
            if not is_color_like(color):
                return None
            
        return color_str
    
    def _parse_top_k_params(self, raw: str):
        if len(raw) == 3 and raw[0].isdigit():
            k, select_column, reported_variable = raw
            return k, select_column, reported_variable
        
        elif len(raw) == 2 and raw[0].isdigit():
            k, select_column = raw
            reported_variable = select_column
            return k, select_column, reported_variable
        
        else:
            return ("invalid function format", "FIND_TOP_K")
        
    def _parse_status_params(self, raw: str):

        if len(raw) == 3 and raw[0] in FUNCTIONS["simple"]:
            function_name, select_column, reported_variable = raw
            return function_name, select_column, reported_variable
        
        elif len(raw) == 2 and raw[0] in FUNCTIONS["simple"]:
            function_name, select_column = raw
            reported_variable = select_column
            return function_name, select_column, reported_variable
        
        else:
            return ("invalid function format", "STATUS")
        
    def _parse_map_params(self, raw: str):
        if raw[0] not in VAR_NAMES:
            # Variable to be mapped has not been specified
            return ("invalid function format", "MAP")
        
        param_dict = {"select_column": raw[0]}

        for p in raw[1:]:
            if self.valid_color_for_map(p):
                param_dict["color"] = p

            else:
                # Replace with working location function
                param_dict["location"] = p
            # implement location method
            # if self.is_location(p):
            #     param_dict["location"] = p

        return param_dict        
    
    def set_parameters(self, json_object: str) -> None:
        """
        Sets parameters based on the function specified in the call
        
        """
        # Simple
        raw_params = [param.lower() for param in json_object["parameters"]]
        if self.type == "simple":
            self.parameters = {"column": raw_params[0]}

        # Top k
        if self.func_name == "FIND_TOP_K":
            output = self._parse_top_k_params(raw_params)
            if output != ("invalid function format", "FIND_TOP_K"):
                k, select_column, reported_variable = output
                self.parameters = {
                    "k": k,
                    "select_columns": select_column,
                    "reported_variable": reported_variable
                }
            self.errors.append(output)

        # Status
        if self.func_name == "STATUS":
            output = self._parse_status_params(raw_params)
            if output != ("invalid function format", "STATUS"):
                function_name, select_column, reported_variable = output
                self.parameters = {
                    "function_name": function_name,
                    "select_columns": select_column,
                    "reported_variable": reported_variable
                }
            self.errors.append(output)

        # Map
        if self.func_name == "MAP":
            output = self._parse_map_params(raw_params)
            if output != ("invalid function format", "MAP"):
                self.parameters = {
                    "select_column": output.get("select_column"),
                    "color": output.get("color", DEFAULT_MAP_COLOR),
                    "location": output.get("location", None)
                }
            self.errors.append(output)

    def set_conditions(self, json_object: str) -> None:
        """
        Sets conditions based on the function specified in the call

        """
        conds_dict = {}

        for i, cond in enumerate(json_object["conditions"]):
            var_name = cond["variable_name"]
            restriction = cond["restriction"][0]
            bool_operators = cond["bool_operators"]

            conds_dict[var_name] = conds_dict.get(var_name, [])

            if i == 0:
                conds_dict[var_name].append(f"{var_name} {restriction}")

            if i > 1:
                conds_dict[var_name].append(f"{bool_operators} {var_name} {restriction}")

        self.conditions = {
            var_name: " ".join(conditions)
            for var_name, conditions in conds_dict.items()
        }

    def is_location():
        """
        Function to determine whether a string is a valid location.
        
        Must check that zip code is valid
        Determine if state, city, county

        Likely can produce list available locations in dataset and use that to compare

        Fuzzy matching?
        """
        pass

    def __eq__(self, other: "json_response") -> bool:
        return (
            self.func_name == other.func_name and
            self.parameters == other.parameters and
            self.conditions == other.conditions
        )
    # Checked documentation for how to use classes as dictionary keys (__hash__)
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    def __hash__(self) -> int:
        return hash(" ".join(
            [self.func_name] + 
            list(self.parameters.keys()) + 
            list(self.parameters.values()) +
            list(self.conditions.keys()) +
            list(self.conditions.values())
            )
        )


class agent_functions:
    """

    """

    def __init__(self):
        self.tract_shp = self.get_shapefiles()


    def _get_shapefiles(self):
        states = ["CA", "IL", "TX", "WA", "FL"]

        tracts_shp = tracts(year = 2020, state = states[0])
        tracts_shp["state_name"] = states[0]

        for state in states[1:]:
            state_tracts = tracts(year = 2020, state = state)
            state_tracts["state_name"] = state

            tracts_shp = pd.concat([tracts_shp, state_tracts], axis = 0)
        return tracts_shp


    # def verify_inputs(self) -> None | str:
    #     """
    #     Verify that the JSON inputs are valid and generate a correction message
    #     if they are wrong.

    #     """
    #     errant_functions = self.function_call.verify_function(self.available_functions)
    #     errant_parameters = self.function_call.verify_parameters(self.available_parameters)

    #     correction_message = ""
    #     if errant_functions:
    #         correction_message += f"The function: {errant_functions} was included" 
    #         "in the JSON output, but this is not an available function."

    #     if errant_parameters:
    #         if len(errant_functions) > 1:
    #             correction_message += f"The parameters: {errant_functions}, were"
    #             "included in the JSON output, but these are not available parameters."
    #         else:
    #             correction_message += f"The parameter: {errant_functions}, was"
    #             "included in the JSON output, but this is not an available parameter."

    #     if errant_functions or errant_parameters:
    #         return correction_message
    #     return None


    def request_simple_functions_data(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """
        func_name = json_response_obj.parameters["function_name"]
        column = json_response_obj.parameters["column"]

        pass

    def request_status_data(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """

        pass

    def request_top_k(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """

        pass

    def request_map(self, json_response_obj: json_response, color=DEFAULT_MAP_COLOR) -> str:
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

    def __init__(self) -> None:
        self.model_name = "PSC404"
        self.system_message = \
        """

        """
        self.context = None
        super().__init__(host=NGROK_TUNNEL_KEY)
        

    def get_json(self, prompt: str) -> List[Dict]:
        """
        Generates a resposne from the LLM and coerces it to JSON

        """
        json_output = self.generate(
            model=self.model_name,
            prompt=prompt,
            system=self.system_message,
            context=self.context,
            format='json'
        )
        self.context = json_output["context"]
        
        return json.loads(json_output["response"].replace("\\", ""))["queries"]

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

            
                
            

            







# a = """
# "role": "system", 
#      "content":
         
#         <s>[INST] 

#         You are a helpful code assistant mean to help with data analysis. Your task is to generate a valid JSON 
#         object from a user's input. Only respond in JSON format. Do not elaborate after outputting 
#         JSON. 

#         These are the available functions and their descriptions:
#             "mean": "take the average or mean"
#             "sum": "sums a variable across a dataset"
#             "count": "counts something across a dataset"

#         The following example:

#         What is the average Climate index in Chicago? 

#         Should be converted to [/INST]

#         "queries": [
#             {
#                 "filter": "Chicago",
#                 "function_name": "average",
#                 "function_parameters": "Climate index"
#             }
#         ]

#         [INST] Here is another example:

#         What is the total population in Salt Lake City, Utah?

#         Should be converted to [/INST]

#         "queries": [
#             {
#                 "filter": "Salt Lake City, Utah",
#                 "function_name": "sum",
#                 "function_parameters": "population"
#             }
#         ]
    
#         [INST] Here is another example:

#         "How many rivers are in Arizona? Also how many people live in Evanston, Illinois?"

#         Should be converted to [/INST]

#         "queries": [
#             {
#                 "filter": "Arizona",
#                 "function_name": "count",
#                 "function_parameters": "rivers"
#             },
#             {
#                 "filter": "Evanston, Illinois",
#                 "function_name": "sum",
#                 "function_parameters": "population"
#             }
#         ]

#         [INST] "how many trees are in my zip code, 60617" [/INST]

#         </s>

#     """

        

        