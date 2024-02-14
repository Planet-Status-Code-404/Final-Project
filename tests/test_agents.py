import pytest
import sys
print(sys.path)
from chatbot.model import agents

EXAMPLE_JSON_FUNCTION = {
    "function_name": "sum",
    "parameters": ["vulnerability index", "Climate risk"],
    "conditions": ["location: Chicago"]
}
EXAMPLE_JSON_FUNCTION_CALL = {
    "function_name": "SUM",
    "parameters": ["vulnerability index", "climate risk"],
    "conditions": ["location: chicago"]
}

def test_json_function_call():
    json_call = agents.json_function_call(EXAMPLE_JSON_FUNCTION)

    assert json_call.func_name == EXAMPLE_JSON_FUNCTION_CALL["function_name"]
    assert json_call.parameters == EXAMPLE_JSON_FUNCTION_CALL["parameters"]
    assert json_call.conditions == EXAMPLE_JSON_FUNCTION_CALL["conditions"]