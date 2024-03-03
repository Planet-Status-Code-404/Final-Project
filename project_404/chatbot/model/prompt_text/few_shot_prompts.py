FUNCTION_AGENT_FEW_SHOT_PROMPTS = \
"""
The following example:

    [INST] Here is another example:

    What is the average life expectancy in Los Angeles with a population above 20000

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "What is the average life expectancy in Los Angeles with a population above 20000",
            "function_name": "mean",
            "parameters": ["demographics.LIFEEXP"],
            "conditions": [
                {
                    "variable_name": "main.totalPop",
                    "restriction": ["> 20000"],
                    "boolean_operator": ""
                },
                {
                    "variable_name": "city",
                    "restriction": ["== Los Angeles"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    [INST] Here is another example:

    Make me a map of particulate matter in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a map of particulate matter in Los Angeles",
            "function_name": "map",
            "parameters": ["main.RAW_E_PM25", "", "Los Angeles"],
            "conditions": [
                {
                    "variable_name": "",
                    "restriction": [""],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    [INST] Here is another example:

    Make me a green-red map of baseline health in Chicago where life expectancy is greater than 40 or particulate air is higher than 8

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a green-red map of baseline health in Chicago where life expectancy is greater than 40 or particulate air is higher than 8",
            "function_name": "map",
            "parameters": ["baseline_health", "green-red", "Chicago"],
            "conditions": [
                {
                    "variable_name": "demographics.LIFEEXP",
                    "restriction": ["> 40"],
                    "boolean_operator": ""
                },
                {
                    "variable_name": "main.RAW_E_PM25",
                    "restriction": ["> 8"],
                    "boolean_operator": "OR"
                }
            ]
        }
    ]

    [INST] Here is another example:

    What is the percent of english speaking populations in Chicago

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "What is the percent of english speaking populations in Chicago",
            "function_name": "status",
            "parameters": ["demographics.P_ENGLISH"],
            "conditions": [
                {
                    "variable_name": "city",
                    "restriction": ["== Chicago"],
                    "boolean_operator": ""
                }
            ]
        }
    ]


    Again remember, you are a helpful code assistant meant to help with function calling. Your task is to generate a valid JSON 
    object from the user's input. ONLY use the following values for "function_name". Only respond in JSON format. Do not elaborate after outputting JSON.

    If for some reason, you do not have enough information, politely request the necessary information. Do not make assumptions. Do not explain yourself.

"""