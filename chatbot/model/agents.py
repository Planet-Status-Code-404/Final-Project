import ollama
import json
from typing import List

class json_function_call:
    """
    A single function json object outputted from a function calling agent

    """

    def __init__(self, json_object: str):
        
        self.func_name = json_object["function"].upper()
        self.parameters = json_object["parameters"]
        self.conditions = json_object["conditions"]

    def verify_function(self, available_functions: List[str]):
        """
        Verifies that the function of the function call is a legal function.

        Returns:
          Nothing - if the function is legal
          Function name - if the the function name is not available
        """
        if self.function not in available_functions:
            return self.function
        return None

    def verify_parameters(self, available_parameters: List[str]):
        """
        Verifies that the paramaters of the function call are all valid.

        Returns:
          None - if the parameter name is in the database
          parameter name - if the parameter name is not in the database
        """
        errant_params = []
        for param in self.parameters:
            if param not in available_parameters:
                errant_params.append(param)
        return errant_params


class agent_functions:
    """

    """

    def __init__(self, json_function: json_function_call):
        self.function_call = json_function
        self.func_name = json_function.func_name
        self.parameters = json_function.parameters
        self.conditions = json_function.conditions

        self.simple_functions = [
            # The next 8 functions are the "simple" functions
            "SUM",
            "COUNT",
            "MAX",
            "MIN",
            "MEAN",
            "MEDIAN",
            "VAR",
            "STD"
        ]

        self.complex_functions = [
            # The next 4 functions are the "complex" functions
            "STATUS", # What is the state of some parameter with or without some condition
            "TOP_K", # The top k of some parameter
            "BOTTOM_K", # The bottom k of some parameter
            "MAP" # Generate a map based on the parameters and conditions
        ]

        self.available_functions = self.simple_functions + self.complex_functions

    def verify_inputs(self):
        if 

    def construct_sql_query(self):



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
        super().__init__()

    def get_json(self, prompt: str):
        """

        """
        json_output = self.generate(
            model=self.model_name,
            prompt=prompt,
            system=self.system_message,
            context=self.context
            format='json'
        )
        self.context = json_output["context"]
        
        return json.loads(json_output["response"].replace("\\", ""))["queries"]
    

    
    def call_functions(self, prompt: str):
        """

        """

        for function_call in self.get_json(prompt):
            json_function = json_function_call(function_call)

            func = json_function.function
            parameters = json_function.parameters
            conditions = json_function.conditions


            








message = [
    { "role": "system", 
     "content":
         """
        <s>[INST] 

        You are a helpful code assistant mean to help with data analysis. Your task is to generate a valid JSON 
        object from a user's input. Only respond in JSON format. Do not elaborate after outputting 
        JSON. 

        These are the available functions and their descriptions:
            "mean": "take the average or mean"
            "sum": "sums a variable across a dataset"
            "count": "counts something across a dataset"

        The following example:

        What is the average Climate index in Chicago? 

        Should be converted to [/INST]

        "queries": [
            {
                "filter": "Chicago",
                "function_name": "average",
                "function_parameters": "Climate index"
            }
        ]

        [INST] Here is another example:

        What is the total population in Salt Lake City, Utah?

        Should be converted to [/INST]

        "queries": [
            {
                "filter": "Salt Lake City, Utah",
                "function_name": "sum",
                "function_parameters": "population"
            }
        ]
    
        [INST] Here is another example:

        "How many rivers are in Arizona? Also how many people live in Evanston, Illinois?"

        Should be converted to [/INST]

        "queries": [
            {
                "filter": "Arizona",
                "function_name": "count",
                "function_parameters": "rivers"
            },
            {
                "filter": "Evanston, Illinois",
                "function_name": "sum",
                "function_parameters": "population"
            }
        ]

        [INST] "how many trees are in my zip code, 60617" [/INST]

        </s>

    """

        

        