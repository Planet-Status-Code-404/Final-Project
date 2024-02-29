from chatbot.model.utilities import get_variable_names
from chatbot.model.prompt_text.inital_instructions import FUNCTION_AGENT_INITIAL_INSTRUCTIONS
from chatbot.model.prompt_text.few_shot_prompts import FUNCTION_AGENT_FEW_SHOT_PROMPTS


class function_agent_prefix:
    def __init__(self):
        self.var_names = self.get_var_names_and_descriptions()
        self.inital_instructions = FUNCTION_AGENT_INITIAL_INSTRUCTIONS
        self.few_shot_prompts = FUNCTION_AGENT_FEW_SHOT_PROMPTS
        self.define_conditions()

    def get_var_names_and_descriptions(self):
        """ Get variable names and descriptions from database """
        var_dict = get_variable_names()

        var_names_and_desc = ""
        for var, table_and_descr in var_dict.items():
            _, desc = table_and_descr
            
            var_names_and_desc += f"'{var}': {desc}\n"

        return var_names_and_desc
    
    def define_conditions(self):
        """Define set of conditions to be used in prompt"""

        self.conditions = \
        """
        "conditions" also require a {restriction}. A {restriction} represents a way to filter the {variable_name}. 
        Possible restrictions and their definitions are below:
            "== {some value}": the "variable_name" should be exactly equal to the value set by the user
            "> {some value}": the "variable_name" should be greater than value set by the user
            ">= {some value}": the "variable_name" should be greater or equal to the value set by the user
            "< {some value}": the "variable_name" should be less than value set by the user
            "<= {some value}": the "variable_name" should be less or equal to the value set by the user
        """

        self.conditions += \
        """
        "conditions" also require {boolean_operator}. A {boolean_operator} represents a way to combine {restriction}.
        Possible boolean_operator and their definitions are below:
            "OR": use the boolean operator "OR" to combine the "conditions"
            "AND": use the boolean operator "AND" to combine the "conditions".

        """

    def prompt(self):
        """Generate the prompt prefix"""

        return (
            f"{self.inital_instructions}\n" +
            "When choosing a value for {parameters}, {variable_name}, 'select_column', or 'reported_variable' " +
            "the availale values and their descriptions are below. ONLY choose among these variables:\n"
            f"{self.var_names}" +
            f"{self.conditions}\n" +
            "'conditions' are ways that the user may want to restrict the data. " +
            "A condition requires a {variable_name} in the dataset and a way to filter it." +
            f"{self.few_shot_prompts}\n" +
            "</s>"
        )



    
