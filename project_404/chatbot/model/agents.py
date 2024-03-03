import ollama # Ollama is program that allows us to create and host LLMs
from typing import List, Dict
from inflect import engine # Used to convert things like "1st" to "first" -- helpful for communicating with the LLM
from pygris import tracts # Gets census (tigris) shapefiles
import folium # Used to make leaflet interactive maps
import pandas as pd
import geopandas # Used to handle spatial data
# The idea came from similar use in R, but the use of webbrowser was infromed by this post
# https://stackoverflow.com/questions/53069033/python-how-to-open-map-created-with-folium-in-browser-when-running-application
import webbrowser
import json_repair # Useful for coercing output from the LLM to proper JSON
from jenkspy import jenks_breaks # Create Fisher-Jenks natural breaks for maps
import colour # Create color scales
import branca.colormap as cm
import sqlite3
import pathlib

from project_404.chatbot.model.json_responses import json_response, VAR_NAMES
from project_404.chatbot.model.prompt_prefixes import function_agent_prefix


class agent_functions:
    """

    """

    def __init__(self):
        self.tract_shp = self.get_shapefiles().set_index("GEOID")

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
        # If conditions are set for restrictions across vairbles use OR
        cond = "OR".join([cond for cond in conditions_dict.values()])

        return cond

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
            query = f"SELECT {column} {tables} WHERE {conditions}"
        else:
            query = f"SELECT {func_name}({column}) {tables} WHERE {conditions}"

        self.db_connection.execute(query)
        return self.db_connection.fetchall()

    # def request_status_data(self, json_response_obj: json_response) -> str:
    #     """
    #     Construct SQL query 
    #     """
    #     func_name = json_response_obj.parameters["function_name"]
    #     select_column = json_response_obj.parameters["select_columns"]
    #     reported_variable = json_response_obj.parameters["reported_variable"]
        
    #     tables = self.construct_from_statement(json_response_obj)
    #     conditions = self.construct_where_statement(json_response_obj)

    #     query = f"SELECT {func_name}({reported_variable}) {tables} WHERE {conditions}"

    #     pass

    def request_top_k(self, json_response_obj: json_response) -> str:
        """
        Construct SQL query 
        """
        k = json_response_obj.parameters["k"]
        select_column = json_response_obj.parameters["select_columns"]
        reported_variable = json_response_obj.parameters["reported_variable"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        query = f"SELECT {reported_variable} {tables} WHERE {conditions} ORDER"\
        f"BY {select_column} LIMIT {k}"

        self.db_connection.execute(query)
        return self.db_connection.fetchall()

    def get_map_data(self, json_response_obj: json_response):
        """Get data for map from SQL"""

        select_column = json_response_obj.parameters["select_columns"]

        tables = self.construct_from_statement(json_response_obj)
        conditions = self.construct_where_statement(json_response_obj)

        query = f"SELECT geoid, {select_column} {tables} WHERE {conditions}"

        # Inspired by https://stackoverflow.com/questions/36028759/how-to-open-and-convert-sqlite-database-to-pandas-dataframe
        return pd.read_sql_query(query, self.db_connection)

    def request_map(self, json_response_obj: json_response) -> str:
        """
        Create map from SQL data
         
        """
        # Used https://www.latlong.net/ to find coordinates
        location_coords = {
            "Chicago": (41.881832, -87.623177),
            "New Orleans": (29.951065, -90.071533),
            "Los Angeles": (34.052235, -118.243683),
            "Seattle": (47.608013, -122.335167),
            "Houston": (29.749907, -95.358421)
        }

        location = json_response_obj.parameters["location"]
        select_column = json_response_obj.parameters["select_columns"]
        color = json_response_obj.parameters["color"]

        df = self.get_map_data(json_response_obj).set_index("geo_id")
        
        if location:
            map = folium.Map(
                location = location_coords[location],
                tiles="cartodb positron",
                zoom_start=3
            )
        else:
            # Default to US
            map = folium.Map(
                location = [48, -102],
                tiles="cartodb positron",
                zoom_start=3
            )

        data_scale = jenks_breaks(df[select_column].to_numpy(), n_classes=5)

        if "-" in color:
            color1, color2 = color.split("-")
            color_scale = list(colour.Color(color1).range_to(colour.Color(color2), 5))
            color = f"{color1}_{color2}"
        else:
            # Using generic, neutral grey as default "beginning"
            color_scale = list(
                colour.Color("#a7a7a8").range_to(colour.Color(color1), 5)
            )

        map_colors = cm.LinearColormap(
            [color.hex for color in color_scale],
            index = data_scale
        )

        # Filter tracts to the geo_ids in database call. Convert to geoJSON
        tracts = self.tract_shp["geo_id"].isin(df["geo_id"].unique())
        tracts = tracts.to_json()

        # geo_df = df.merge(self.tract_shp, how = "left", on = "geo_id")
        # Adapted from folium documentation: https://python-visualization.github.io/folium/latest/getting_started.html
        folium.GeoJson(
            data = tracts,
            style_function = lambda feature: {
                "fillColor": map_colors(df[feature["id"]]),
                "color": "black",
                "weight": 2,
                "dashArray": "1",
            }        
        ).add_to(map)

        output_map_file = f'{select_column}_{color}.html'
        map.save(output_map_file)

        return output_map_file

    def get_data(self, json_response_obj: json_response) -> str:
        """
        Call the right requesting function depending on the function name.

        Returns the answer for the request
        
        """
        if json_response_obj.type ==  "simple":
            answer = self.request_simple_functions_data(json_response_obj)
        elif json_response_obj.func_name ==  "FIND_TOP_K":
            answer = self.request_top_k(json_response_obj)
        elif json_response_obj.func_name ==  "MAP":
            answer = self.request_map(json_response_obj)
        
        return answer


class function_calling_agent(ollama.Client):
    """
    Agent to convert natural language to function calls.

    """

    def __init__(self, tunnel_key) -> None:
        self.model_name = "mistral"
        self.context = None
        self.functions = agent_functions()

        super().__init__(host = tunnel_key)
        

    def get_json(self, prompt: str) -> List[Dict]:
        """
        Generates a resposne from the LLM and coerces it to JSON

        """
        json_output = self.generate(
            model=self.model_name,
            prompt=f"{function_agent_prefix.prompt_prefix}\n{prompt}",
            context=self.context,
        )
        self.context = json_output["context"]
        
        return json_repair.loads(json_output["response"].replace("\\", ""))["queries"]

    # def retry_request(
    #         self,
    #         agent_function_call: agent_functions,
    #         num_of_retries=1) -> agent_functions | str:
    #     """
    #     Recursively makes requests to the LLM to resolve nonmatches between the functions
    #     and parameters and what are available.

    #     Returns an agent_functions object or a string if it can't correct the issue

    #     """
    #     if not agent_function_call.correction_message:
    #         return agent_function_call
    #     if num_of_retries == 0:
    #         return "Could not complete request"

    #     # Consider making the resubmitted prompt more complicated
    #     # Tell it to choose from a list of potential options
    #     json_func_object = self.get_json(
    #         prompt=
    #         f"{agent_function_call.correction_message}\n"
    #         f"The possible function values are {agent_function_call.available_functions}\n"
    #         f"The possible parameter values are {agent_function_call.available_parameters}\n"
    #         "Please try again."
    #     )
    #     new_function_call = agent_functions(json_func_object)
    #     new_message = new_function_call.correction_needed

    #     if new_message:
    #             new_request = self.retry_request(new_function_call, num_of_retries - 1)
    #             return new_request

    #     return new_function_call

    def call_functions(self, prompt: str):
        """
        Call each function from the JSON output

        **Look to see if I can prompt the LLM to include the question matched to the JSON request

        """
        answers = []

        for i, json_func_object in enumerate(self.get_json(prompt)):
            functions = self.retry_request(agent_functions.get_data(json_func_object))

            if functions == "Could not complete request":
                return "Could not complete request"
            
            # The use of inlect.engine() was inspired by this Stack post
            # https://stackoverflow.com/questions/11180845/is-there-a-library-to-convert-integer-to-first-second-third
            answers.append(f"The {engine().ordinal(i)} answer is: {functions.get_data()}")

        return "\n".join(answers)

class response_agent(ollama.Client):
    """
    Agent to take answers from the function calling agent and respond to user

    """

    def __init__(self, tunnel_key) -> None:
        self.model_name = "mistral"
        self.context = None
        self.functions = agent_functions()

        super().__init__(host = tunnel_key)