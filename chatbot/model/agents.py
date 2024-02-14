import ollama
import json
from typing import List, Dict
from inflect import engine

class json_function_call:
    """
    A single function json object outputted from a function calling agent

    """

    def __init__(self, json_object: str):
        
        self.func_name = json_object["function_name"].upper()
        self.parameters = [param.lower() for param in json_object["parameters"]]
        self.conditions = [cond.lower() for cond in json_object["conditions"]]

    def verify_function(self, available_functions: List[str]):
        """
        Verifies that the function of the function call is a legal function.

        Returns:
          Nothing - if the function is legal
          Function name - if the the function name is not available
        """
        if self.func_name not in available_functions:
            return self.func_name
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

    def __init__(self, json_object: str):
        self.function_call = json_function_call(json_object)
        self.func_name = self.function_call.func_name
        self.parameters = self.function_call.parameters
        self.conditions = self.function_call.conditions

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
        self.available_parameters = self.get_available_parameters()

        self.correction_needed = self.verify_inputs()

    def verify_inputs(self) -> None | str:
        """
        Verify that the JSON inputs are valid and generate a correction message
        if they are wrong.

        """
        errant_functions = self.function_call.verify_function(self.available_functions)
        errant_parameters = self.function_call.verify_parameters(self.available_parameters)

        correction_message = ""
        if errant_functions:
            correction_message += f"The function: {errant_functions} was included" 
            "in the JSON output, but this is not an available function."

        if errant_parameters:
            if len(errant_functions) > 1:
                correction_message += f"The parameters: {errant_functions}, were"
                "included in the JSON output, but these are not available parameters."
            else:
                correction_message += f"The parameter: {errant_functions}, was"
                "included in the JSON output, but this is not an available parameter."

        if errant_functions or errant_parameters:
            return correction_message
        return None
    
    def get_available_parameters(self) -> List[str]:
        """
        Use the SQL schema to get the available column names as potential 
        parameters
        """
        pass

    def request_simple_functions_data(self) -> str:
        """
        Construct SQL query 
        """

        pass

    def request_status_data(self) -> str:
        """
        Construct SQL query 
        """

        pass

    def request_top_k(self) -> str:
        """
        Construct SQL query 
        """

        pass

    def request_bottom_k(self) -> str:
        """
        Construct SQL query 
        """

        pass

    def request_map(self) -> str:
        """
         
        """

        pass

    def get_data():
        """
        
        """

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
        super().__init__()

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
            prompt=f"{agent_function_call.correction_message} Please try again."
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
            functions = self.retry_request(agent_functions(json_func_object))

            if functions == "Could not complete request":
                return "Could not complete request"
            
            # The use of inlect.engine() was inspired by this Stack post
            # https://stackoverflow.com/questions/11180845/is-there-a-library-to-convert-integer-to-first-second-third
            answers.append(f"The {engine().ordinal(i)} answer is: {functions.get_data()}")

        return "\n".join(answers)

            
                
            

            







a = """
"role": "system", 
     "content":
         
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

        

        