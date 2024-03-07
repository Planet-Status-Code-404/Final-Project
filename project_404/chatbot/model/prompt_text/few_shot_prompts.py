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
            "parameters": ["psc_124"],
            "conditions": [
                {
                    "variable_name": "psc_142",
                    "restriction": ["> 20000"],
                    "boolean_operator": ""
                },
                {
                    "variable_name": "psc_61",
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
            "parameters": ["psc_138", "", "Los Angeles"],
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
            "parameters": ["psc_5", "green-red", "Chicago"],
            "conditions": [
                {
                    "variable_name": "psc_124",
                    "restriction": ["> 40"],
                    "boolean_operator": ""
                },
                {
                    "variable_name": "psc_138",
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
            "parameters": ["psc_28"],
            "conditions": [
                {
                    "variable_name": "psc_61",
                    "restriction": ["== Chicago"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    [INST] Here is another example:

    Give me the average psc_78 in Chicago.

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Give me the average resilience score in Chicago",
            "function_name": "abg",
            "parameters": ["psc_78"],
            "conditions": [
                {
                    "variable_name": "psc_61",
                    "restriction": ["== Chicago"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    [INST] Here is another example:

    Make me a map of psc_5 in Chicago where psc_30 is greater than 500.

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a map of psc_5 in Chicago",
            "function_name": "map",
            "parameters": ["psc_5", "", "Chicago"],
            "conditions": [
                {
                    "variable_name": "psc_30",
                    "restriction": ["> 500"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    [INST] Here is another example:

    Make me a map of social vulnerability score in Chicago if psc_140 is equal to 5.

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a map of social vulnerability score in Chicago",
            "function_name": "map",
            "parameters": ["psc_77", "", "Chicago"],
            "conditions": [
                {
                    "variable_name": "psc_140",
                    "restriction": ["== 5"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    [INST] Here is another example:

    Make me a map of resilience score in Chicago.

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a map of resilience score in Chicago",
            "function_name": "map",
            "parameters": ["psc_78", "", "Chicago"],
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

    Make me a map of people who have one or two components contributing to social vulnerability in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a map of people who have one or two components contributing to social vulnerability in Los Angeles",
            "function_name": "map",
            "parameters": ["psc_176", "", "Los Angeles"],
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

    Give me the average asian populations in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Give me the average asian populations in Los Angeles",
            "function_name": "avg",
            "parameters": ["psc_159"],
            "conditions": [
                {
                    "variable_name": "psc_61",
                    "restriction": ["== Los Angeles"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    
    [INST] Here is another example:

    Give me the top 5 asian populations in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a green map of asian populations in Los Angeles",
            "function_name": "top_k",
            "parameters": ["5", "psc_159", "psc_159"],
            "conditions": [
                {
                    "variable_name": "psc_61",
                    "restriction": ["== Los Angeles"],
                    "boolean_operator": ""
                }
            ]
        }
    ]

    
    [INST] Here is another example:

    Make me a green map of asian populations in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a green map of asian populations in Los Angeles",
            "function_name": "map",
            "parameters": ["psc_159", "green", "Los Angeles"],
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

    Make me a blue map of black populations in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a blue map of black populations in Los Angeles",
            "function_name": "map",
            "parameters": ["psc_157", "blue", "Los Angeles"],
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

    Make me a orange map of white populations in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a orange map of white populations in Los Angeles",
            "function_name": "map",
            "parameters": ["psc_156", "orange", "Los Angeles"],
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

    Make me a orange map of earthquake risk in Los Angeles

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a orange map of earthquake risk in Los Angeles",
            "function_name": "map",
            "parameters": ["psc_82", "orange", "Los Angeles"],
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

    Make me a red-green map of the number of brownfields in Los Angeles where pariculate matter is greater than 4

    Should be converted to [/INST]

    "queries" : [
        {
            "prompt": "Make me a red-green map of the number of brownfields in Los Angeles where pariculate matter is greater than 4",
            "function_name": "map",
            "parameters": ["psc_144", "red-green", "Los Angeles"],
            "conditions": [
                {
                    "variable_name": "psc_138",
                    "restriction": ["> 4"],
                    "boolean_operator": ""
                }
            ]
        }
    ]


    Again remember, you are a helpful code assistant meant to help with function calling. Your task is to generate a valid JSON 
    object from the user's input. Only respond in JSON format. Do not elaborate after outputting JSON.

    If for some reason, you do not have enough information, politely request the necessary information. Do not make assumptions. Do not explain yourself.

"""