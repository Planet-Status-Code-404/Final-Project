import ollama
import json

class json_resposne:
    """

    """

    def __init__(self, json_object):
        self.function = json_object["function"]
        self.restrictions = json_object["restrictions"]


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
        
        return json_output["response"]
    
    def parse_json_response(json_resposne):
        """

        """






class llm_function():
    def __init__(self, json_str: str):
        self.json_str = json_str
        self.function = json_str["function"]
        self.parameters = json_str["parameters"]
        self.condtions = json_str["conditions"]

    def construct_where_clause(self):
        sql_clauses: {
            

        }

        sql_args: {
            
        }
        

    def construct_SQL_query(self):
        

        