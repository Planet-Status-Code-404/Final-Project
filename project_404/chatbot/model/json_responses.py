from matplotlib.colors import is_color_like # Used to determine if something is a color
from project_404.chatbot.utilities import get_variable_names
import re

# Dictionary to define the available functions and whether they are simple or complex
FUNCTIONS = {
    "simple": {"SUM", "COUNT", "MAX", "MIN", "MEAN", "MEDIAN", 
               "STATUS",}, # What is the state of some parameter with or without some condition

    "complex": {
        "FIND_TOP_K", # The top k of some parameter
        "MAP" # Generate a map based on the parameters and conditions
    }
}


# Dictionary to define all the available variable names and which table they're in
VAR_NAMES = {var_name: table_and_descr[0] for var_name, table_and_descr in get_variable_names().items()}


#Dictionary to define the potential errors that may be raised due to issues in JSON output
ERRORS = {
    "invalid function name": "The 'function_name' outputted to JSON was not one of the valid functions listed",
    "invalid function format": "The structure of the JSON output missed an important and required aspect necessary to output the correct response", 
    "invalid parameter name": "The 'parameter' outputted to JSON was not one of the valid parameters listed"
}

DEFAULT_MAP_COLOR = "Blue"


class json_response:
    """
    A single json function object outputted from a function calling agent.
    Parses the inputted JSON and assign the function name, parameters, and
    conditions associated with the function.

    """

    def __init__(self, json_object: str):
        
        self.prompt_text = json_object["prompt_text"].upper()
        self.func_name = json_object["function_name"].upper()
        
        self.type = self._set_type()
        self.errors = []

        self.set_parameters(json_object)
        self.set_conditions(json_object)

        self.set_SQL_tables_list()

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

            select_column = f"{VAR_NAMES[select_column]}.{select_column}"
            reported_variable = f"{VAR_NAMES[reported_variable]}.{reported_variable}"

            return k, select_column, reported_variable
        
        elif len(raw) == 2 and raw[0].isdigit():
            k, select_column = raw

            select_column = f"{VAR_NAMES[select_column]}.{select_column}"
            reported_variable = select_column

            return k, select_column, reported_variable
        
        else:
            return ("invalid function format", "FIND_TOP_K")
        
    def _parse_map_params(self, raw: str):
        if raw[0] not in VAR_NAMES:
            # Variable to be mapped has not been specified
            return ("invalid function format", "MAP")
        
        param_dict = {"select_column": f"{VAR_NAMES[raw[0]]}.{raw[0]}"}

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
            self.parameters = {"column": f"[{VAR_NAMES[raw_params[0]]}].[{raw_params[0]}]"}

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
            else:
                self.errors.append(output)

        # Map
        if self.func_name == "MAP":
            output = self._parse_map_params(raw_params)
            if output != ("invalid function format", "MAP"):
                self.parameters = {
                    "select_columns": output.get("select_column"),
                    "color": output.get("color", DEFAULT_MAP_COLOR),
                    "location": output.get("location", None)
                }
            else:
                self.errors.append(output)

    def set_conditions(self, json_object: str) -> None:
        """
        Sets conditions based on the function specified in the call

        """
        conds_dict = {}

        for i, cond in enumerate(json_object["conditions"]):
            var_name = cond["variable_name"].lower()
            restriction = cond["restriction"][0].lower()
            bool_operators = cond["bool_operators"].upper()

            conds_dict[var_name] = conds_dict.get(var_name, [])

            # Set variable's table as prefix
            if i == 0:
                conds_dict[var_name].append(
                    f"[{VAR_NAMES[var_name]}].[{var_name}] {restriction}"
                )
            # Combine conditions by boolean operator
            if i > 1:
                conds_dict[var_name].append(
                    f"{bool_operators} [{VAR_NAMES[var_name]}].[{var_name}] {restriction}"
                )

        self.conditions = {
            var_name: " ".join(conditions)
            for var_name, conditions in conds_dict.items()
        }

    def set_SQL_tables_list(self) -> None:
        """Method to obtain the list of all the tables neccessary to make the SQL query"""

        table_lst = []

        for param_key, param_values in self.parameters.items():
            if param_key in ["column", "reported_variable", "select_columns"]:
                table_lst.extend(re.findall(r"([\w_]+)\.", param_values))

        for cond_var_names in self.conditions.keys():
            table_lst.append(VAR_NAMES[cond_var_names])
        
        self.SQL_tables = set(table_lst)

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
