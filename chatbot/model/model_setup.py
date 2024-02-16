import ollama
from chatbot.model.system_messages import SYSTEM_FUNCTION_CALLING

def model_setup():
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

    status_code = ollama.pull("mistral")

    assert status_code["status"] == "success", \
    "Mistral 7b did not successfully install, please try again"

    modelfile= \
    """
    FROM mistral

    PARAMETER temperature .5

    SYSTEM
    """

    modelfile =+ SYSTEM_FUNCTION_CALLING

    ollama.create(model='test', modelfile=modelfile)
