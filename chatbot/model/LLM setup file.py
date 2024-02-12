"""
This code pulls the 7b-Instruct version of Mistral via Ollama. 

This LLM was chose as it the model typically has better performance than 
comparable models, namely Llama 2: 7b. It is, however, 

Requirements: 7b models typically require at least 8GB of RAM
Source (s): 
    https://ollama.ai/library/mistral
    https://mistral.ai/news/announcing-mistral-7b/

    https://github.com/ollama/ollama-python/tree/main?tab=readme-ov-file
    
"""
import ollama
status_code = ollama.pull("mistral")

assert status_code["status"] == "success", \
"Mistral 7b did not successfully install, please try again"

modelfile= \
'''
FROM mistral

PARAMETER temperature 1

PARAMETER num_ctx 4096

SYSTEM You are a concise, helpful, and friendly assitant named PSC404, meant to help people understand Climate
Change. Only answer questions regarding Climate Change, Climate migration, 
Climate vulnerability, and related topics.
'''

ollama.create(model='PSC404', modelfile=modelfile)

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
        

        
