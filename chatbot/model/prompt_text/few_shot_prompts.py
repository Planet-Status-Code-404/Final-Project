FUNCTION_AGENT_FEW_SHOT_PROMPTS = \
"""
The following example:

    [INST] Here is another example:

    What is the average life expectancy in Los Angeles with a population above 20000

    Should be converted to [/INST]

    "queries" : [
        {
            "function_name": "mean"
            "parameters": ["LIFEEXP"]
            "conditions": {
                [
                    "variable_name": "total_population",
                    "restriction": ["> 20000"]
                ],
                [
                    "variable_name": "location",
                    "restriction": ["== Los Angeles"]
                ]
            }
        }
    ]

    [INST] Here is another example:

    Make me a map of particulate matter in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "function_name": "map"
            "parameters": ["RAW_E_PM25", "", "Los Angeles"]
            "conditions": {
                [
                    "variable_name": "",
                    "restriction": [""]
                ]
            }
        }
    ]


    Again remember, you are a helpful code assistant meant to help with function calling. Your task is to generate a valid JSON 
    object from the user's input. ONLY use the following values for "function_name". Only respond in JSON format. Do not elaborate after outputting JSON.

    If for some reason, you do not have enough information, politely request the necessary information. Do not make assumptions.

"""