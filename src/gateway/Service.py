"""
Repository of APIS
- allows us to access Wikipedia and any other future APIs.
- Possible states of the API
- Modular to handle multiple different types (wikipedia, etc)
"""

import json
import uuid
import requests
import requests
from collections.abc import Callable
from typing import Any
import inspect
import wikipediaapi
from ..utils.Message import Message
from ..utils.UserType import UserType

DICT_VALUE = "api_keys"
MAX_MSG_LEN = 130


class Service:
    """PUT ALL IMPLEMENTED WEB INTERFACING HERE"""

    func_dict: dict[str, Callable[[Any], Any]]
    api_dict: dict[str, str]
    user_type: UserType

    def __init__(self, user_type) -> None:
        """Initialize that service guy
        Resources:
            - json to dict:
                https://www.geeksforgeeks.org/python/convert-json-to-dictionary-in-python/
        """
        self.user_type = user_type
        self.func_dict = {
            "wikipedia": self.wikipedia,
            "weather": self.weather,
            "pokemon": self.pokemon,
            "nasa": self.nasa,
            # "country": self.country,
            "book": self.book,
            # TODO: add more here
        }
        print("added services")
        # Opening JSON file
        with open("secrets.json") as json_file:
            data = json.load(json_file)
            self.api_dict = data[DICT_VALUE]
        print("added api keys")

    def call_api(self, service_name: str, query_args: Any) -> Any:
        """Call the api by name of website/service and query string

        Args:
            service_name (str): What website

        Returns:
             returned_obj (TBD): The text file returned
        """
        function = self.func_dict[service_name]
        return function(query_args)

    def get_params(self, service_name: str) -> Any:
        """Gets the required params of the api

        Args:
            service_name (str): What website

        Returns:
             Any: the params required
        """
        function = self.func_dict[service_name]
        sig = inspect.signature(function)
        param_names = list(sig.parameters.keys())
        return param_names

    
    # TODO: I will fix this, I wanted to use the python wiki instead of the url, but I couldn't get the plain
    # wiki stlying out of it
    def wikipedia(self, string_to_be_queried: str) -> Any:
        """Wikipedia query

        Args:
            string_to_be_queried (str): Thing to look up on wikepedia (Ex: Ghonnerrea),
            it is a verbose name as that is what is printed by the device

        Returns:
             returned_obj (TBD): The test file returned
        """

        assert type(string_to_be_queried) is str, (
            f"you bad bad bad bad you, I want strings not, {type(string_to_be_queried)}s"
        )

        if self.user_type is UserType.BASIC_MESH:
            wiki_wiki = wikipediaapi.Wikipedia(
                user_agent="WikiMesh (nrunyan@unm.edu)",  # wikapedia requires that u ID yourself
                language="en",
                extract_format=wikipediaapi.ExtractFormat.WIKI,
            )

            results = wiki_wiki.page(string_to_be_queried)
            print(results.text)

            return results.text

        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "prop": "revisions",
            "titles": string_to_be_queried,
            "redirects": 1,
            "rvprop": "content",
            "rvslots": "main",
        }

        headers = {"User-Agent": "WikiMesh (nrunyan@unm.edu)"}

        response = requests.get(url, params=params, headers=headers, timeout=20)

        response.raise_for_status()
        data = response.json()

        page = data["query"]["pages"][0]

        if "missing" in page:
            return None

        wiki_text = page["revisions"][0]["slots"]["main"]["content"]

        print(wiki_text)
        return wiki_text

    def weather(self, latitude=35.0844, longitude=-106.6504):
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
        )
        response.raise_for_status()
        return response.json()

    def pokemon(self, name):
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
        response.raise_for_status()
        return response.json()

    def nasa(self):
        response = requests.get(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": self.api_dict[nasa]},
        )
        response.raise_for_status()
        return response.json()

    def book(self, name):
        response = requests.get(
            "https://openlibrary.org/search.json", params={"q": name, "limit": 5}
        )
        response.raise_for_status()
        return response.json()

    # def country(self, name):
    #     response = requests.get(
    #         f"https://restcountries.com/v3.1/name/{name}"
    #     )
    #     response.raise_for_status()
    #     return response.json()

    def available_services(self) -> str:
        return "Available services: " + ", ".join(self.func_dict)
