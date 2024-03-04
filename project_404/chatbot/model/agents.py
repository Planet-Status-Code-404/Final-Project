import ollama # Ollama is program that allows us to create and host LLMs
from typing import List, Dict
from inflect import engine # Used to convert things like "1st" to "first" -- helpful for communicating with the LLM
from pygris import tracts # Gets census (tigris) shapefiles
import folium # Used to make leaflet interactive maps
import pandas as pd
# The idea came from similar use in R, but the use of webbrowser was infromed by this post
# https://stackoverflow.com/questions/53069033/python-how-to-open-map-created-with-folium-in-browser-when-running-application
import webbrowser
import json_repair # Useful for coercing output from the LLM to proper JSON
import json
from jenkspy import jenks_breaks # Create Fisher-Jenks natural breaks for maps
import colour # Create color scales
import branca.colormap as cm
import sqlite3
import pathlib
import re
import time

from project_404.chatbot.model.json_responses import json_response, VAR_NAMES
from project_404.chatbot.model.prompt_prefixes import function_agent_prefix


class agent_functions:
    """

    """

    def __init__(self):
        self.tract_shp = self._get_shapefiles().set_index("GEOID")

        # Connect to SQL database
        db_file_path = pathlib.Path(__file__).parent / "../../data_collection/output_data/climate_database.db"
        self.db_connection = sqlite3.connect(db_file_path)

        self.db_connection.row_factory = sqlite3.Row
        self.db_cursor = self.db_connection.cursor()

    def _get_shapefiles(self):
        states = ["CA", "IL", "TX", "WA", "LA"]

        tracts_shp = tracts(year = 2020, state = states[0])
        tracts_shp["state_name"] = states[0]

        for state in states[1:]:
            state_tracts = tracts(year = 2020, state = state)
            state_tracts["state_name"] = state

            tracts_shp = pd.concat([tracts_shp, state_tracts], axis = 0)
        return tracts_shp
    
    def construct_from_statement(self, json_response_obj: json_response) -> str:
        """Construct FROM statement with neccessary JOINs for SQL"""
        SQL_tables = json_response_obj.SQL_tables

        tables_str = f"FROM {SQL_tables[0]} "
        if len(SQL_tables) > 1:
            for table in SQL_tables:
                tables_str += f"JOIN {table} ON {SQL_tables[0]}.geo_id = {table}.geo_id "

        return tables_str
    
    def construct_where_statement(self, json_response_obj: json_response) -> str:
        """Construct WHERE statement with for SQL"""
        conditions_dict = json_response_obj.conditions
        if json_response_obj.conditions:
            # If conditions are set for restrictions across vairbles use OR
            cond = "OR".join([cond for cond in conditions_dict.values()])
            return "WHERE" + cond
        else:
            return ""

    def request_simple_functions_data(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """
        func_name = json_response_obj.func_name
        column = json_response_obj.parameters["column"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        # STATUS is the equivalent of saying no function
        # The choice to still give it a function name is for simplicity and consistency with the LLM
        if func_name == "STATUS":
            query = f"SELECT {column} {tables} {conditions} LIMIT 10"
        else:
            query = f"SELECT {func_name}({column}) {tables} {conditions}"

        # self.db_cursor.execute(query)
        # return self.db_cursor.fetchall()

        return pd.read_sql_query(query, self.db_connection)

    def request_top_k(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """
        k = json_response_obj.parameters["k"]
        select_column = json_response_obj.parameters["select_columns"]
        reported_variable = json_response_obj.parameters["reported_variable"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        query = f"SELECT {reported_variable} {tables} {conditions} ORDER"\
        f"BY {select_column} LIMIT {k}"

        return pd.read_sql_query(query, self.db_connection)

    def get_map_data(self, json_response_obj: json_response):
        """Get data for map from SQL"""

        select_column = json_response_obj.parameters["select_columns"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        query = f"SELECT geo_id, {select_column} {tables} {conditions}"

        # Inspired by https://stackoverflow.com/questions/36028759/how-to-open-and-convert-sqlite-database-to-pandas-dataframe
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#sqlite-fallback
        return pd.read_sql_query(query, self.db_connection)

    def request_map(self, json_response_obj: json_response) -> str:
        """
        Create map from SQL data
         
        """
        # Used https://www.latlong.net/ to find coordinates
        location_coords = {
            "chicago": (41.881832, -87.623177),
            "new orleans": (29.951065, -90.071533),
            "los angeles": (34.052235, -118.243683),
            "seattle": (47.608013, -122.335167),
            "houston": (29.749907, -95.358421)
        }
        state_fips = {
            "chicago": "17",
            "new orleans": "22",
            "los angeles": "06",
            "seattle": "53",
            "houston": "48"
        }

        location = json_response_obj.parameters["location"]
        select_column = json_response_obj.parameters["select_columns"]
        color = json_response_obj.parameters["color"]

        # Get SQL data and set geo_id to 11 digits if not already
        # Set index to geo_id
        df = self.get_map_data(json_response_obj)
        df["geo_id"] = df["geo_id"].astype(str).str.zfill(11).str.strip()
        df = df.set_index("geo_id")
        
        if location_coords.get(location, None):
            map = folium.Map(
                location = location_coords.get(location),
                tiles="cartodb positron",
                zoom_start=10
            )
        else:
            # Default to US
            map = folium.Map(
                location = [48, -102],
                tiles="cartodb positron",
                zoom_start=4
            )

        column_name = re.findall(r"\.\[([\w_]+)\]", select_column)[0]
        data_scale = sorted(jenks_breaks(pd.to_numeric(df[column_name]).to_numpy(), n_classes=5))

        if "-" in color:
            color1, color2 = color.split("-")
            # color.range_to is exclusive
            color_scale = list(colour.Color(color1).range_to(colour.Color(color2), 6))
            color_name = f"{color1}_{color2}"
        else:
            # Using generic, neutral grey as default "beginning"
            color_scale = list(
                colour.Color("#a7a7a8").range_to(colour.Color(color), 6)
            )
            color_name = color

        map_colors = cm.LinearColormap(
            # Hex code sometimes is reduced to something unrecognizable to cm (ex. red's hex code)
            colors = [colour.hex2rgb(color.hex) for color in color_scale],
            index = data_scale,
            vmin = data_scale[0],
            vmax = data_scale[-1]
        )
        map_colors.caption = column_name.replace("_", " ").capitalize()

        # Filter tracts to the geo_ids in database call. Convert to geoJSON
        tracts = self.tract_shp[self.tract_shp.index.isin(list(df.index.unique()))]

        # Filter to the state of the city of interest
        location_state_fips = state_fips.get(location, None)
        if location_state_fips:
            tracts = tracts.filter(regex=f"^{location_state_fips}", axis=0)
        tracts = tracts.to_json()

        folium.GeoJson(
            data = tracts,
            style_function = lambda feature: {
                "fillColor": map_colors(float(df[df.index == feature["id"]][column_name].iloc[0])),
                "color": "black",
                "weight": 1,
                "dashArray": "1",
                "fillOpacity": .7
            }        
        ).add_to(map)

        # Add legend
        map_colors.add_to(map)

        output_map_file = f'{column_name}_{color_name}_{location}.html'
        map.save(output_map_file)

        return output_map_file

    def get_data(self, json_response_obj: json_response) -> str:
        """
        Call the right requesting function depending on the function name.

        Returns the answer for the request
        
        """
        if json_response_obj.type == "simple":
            if json_response_obj.func_name == "STATUS":
                answer = self.request_simple_functions_data(json_response_obj).to_string(header=True, index=True)
            else:
                answer = self.request_simple_functions_data(json_response_obj).iloc[0]

        elif json_response_obj.func_name == "FIND_TOP_K":
            answer = self.request_top_k(json_response_obj).to_string(header=True, index=True)

        elif json_response_obj.func_name == "MAP":
            answer = self.request_map(json_response_obj)
        
        return answer


class function_calling_agent(ollama.Client):
    """
    Agent to convert natural language to function calls.

    """

    def __init__(self, tunnel_key: str) -> None:
        self.model_name = "mistral"
        self.context = None
        self.functions = agent_functions()
        self.prompt_prefix = function_agent_prefix()

        self.memory = {}

        super().__init__(host = tunnel_key)

    def text_to_json(self, prompt: str) -> List[Dict]:
        """
        Generates a resposne from the LLM and coerces it to JSON

        """
        json_output = self.generate(
            model=self.model_name,
            prompt=f"{self.prompt_prefix.prompt_prefix}\n{prompt}</s>"
        )
        # print(json_output["response"].replace("\\", "").strip().replace("\n", ""))
        # print(json.loads(json_output["response"].replace("\\", "").strip().replace("\n", "")))

        # self.context = json_output["context"]
        print(json_output["response"].replace("\\", "").strip().replace("\n", ""))
        
        return json_repair.loads(
            (
                "{" + 
                json_output["response"].replace("\\", "").strip().replace("\n", "") + 
                "}"
            )
        )["queries"]

    def call_functions(self, prompt: str):
        """
        Call each function from the JSON output

        """
        answers = []
        try:
            all_responses = self.text_to_json(prompt)
        except:
            answers.append("Your query could not be parsed. Sorry friend.")
            return "\n\n".join(answers)

        for i, json_text in enumerate(all_responses):
            print(json_text)
            json_response_obj = json_response(json_text)
            try:
                json_response_obj = json_response(json_text)
                print("Succesfully converted to json response")
            except:
                answers.append(f"The request, '{json_text['prompt']}', could not be met")
                continue
            
            already_answered = self.memory.get(json_response_obj, None) 

            if not already_answered:
                answer = self.functions.get_data(json_response_obj)
                self.memory[json_response_obj] = answer

            answers.append(
                f"The answer to the question, '{json_response_obj.prompt_text}'"
                  f"is:\n {self.functions.get_data(json_response_obj)}"
            )

            if json_response_obj.func_name == "MAP":
                # Opens leaflet map in new tab in browser
                # Note: requires browser (for WSL browser must be installed in Linux subsystem)
                webbrowser.open(answer, 2)

        return "\n\n".join(answers)


class response_agent(ollama.Client):
    """
    Agent to take answers from the function calling agent and respond to user

    """

    def __init__(self, tunnel_key) -> None:
        self.model_name = "mistral"
        super().__init__(host = tunnel_key)

    def responds_with_answers(self, answers):
        """Take answers from function calling agent and respond to user"""
        prompt_prefix = \
        """
        <s>[INST]

        You are a friendly and concise chatbot aimed at summarizing data and
        information.

        Below is information for you to summarize. Please give a brief summary/

        [/INST]
        """
        # Following documentation for streaming responses
        # https://github.com/ollama/ollama-python
        stream = self.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_prefix + answers + "</s>",
                }
            ],
            stream=True
        )

        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)


        
