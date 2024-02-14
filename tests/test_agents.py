import pytest
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

AVAILABLE_FUNC = [
    "SUM",
    "COUNT",
    "MAX",
    "MIN",
    "MEAN",
    "MEDIAN",
    "VAR",
    "STD",
    "STATUS", 
    "TOP_K", 
    "BOTTOM_K",
    "MAP"
]

AVAILABLE_PARAMS = [
    "vulnerability index",
    "climate risk"
]

def test_json_function_call_transformations():
    json_call = agents.json_function_call(EXAMPLE_JSON_FUNCTION)

    assert json_call.func_name == EXAMPLE_JSON_FUNCTION_CALL["function_name"]
    assert json_call.parameters == EXAMPLE_JSON_FUNCTION_CALL["parameters"]
    assert json_call.conditions == EXAMPLE_JSON_FUNCTION_CALL["conditions"]


def test_json_function_call_valid_function():
    json_call = agents.json_function_call(EXAMPLE_JSON_FUNCTION)

    # Test if when the function is in list, the output is None
    assert not json_call.verify_function(AVAILABLE_FUNC)
    # Test that when the function is not in list, the ouptut is the errant function
    assert json_call.verify_function(["COUNT"]) == "SUM"


def test_json_function_call_valid_params():
    json_call = agents.json_function_call(EXAMPLE_JSON_FUNCTION)

    # Test if when the param is in list, the output is None
    assert not json_call.verify_parameters(AVAILABLE_PARAMS)
    # Test that when the param is not in list, the ouptut is the errant param(s)
    assert json_call.verify_parameters(["vulnerability index"]) == [
        "climate risk"
        ]
    assert json_call.verify_parameters(["not a param"]) == [
        "vulnerability index",
        "climate risk"
        ]