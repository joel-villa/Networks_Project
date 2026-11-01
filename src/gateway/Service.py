"""
Repository of APIS
- allows us to access Wikipedia and any other future APIs.
- Possible states of the API
- Modular to handle multiple different types (wikipedia, etc)
"""

import json
from collections.abc import Callable
from typing import Any
import inspect

DICT_VALUE = "api_keys"


class Service:
    """PUT ALL IMPLEMENTED WEB INTERFACING HERE"""

    func_dict: dict[str, Callable[[Any], Any]]
    api_dict: dict[str, str]

    def __init__(self) -> None:
        """Initialize that service guy
        Resources:
            - json to dict:
                https://www.geeksforgeeks.org/python/convert-json-to-dictionary-in-python/
        """
        self.func_dict = {
            "wikipedia": self.wikipedia,
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
    
    
    def get_params(self, service_name:str)->Any:
        function = self.func_dict[service_name]
        sig = inspect.signature(function)
        param_names = list(sig.parameters.keys())
        return param_names


    def wikipedia(self, string_to_be_queried: str) -> Any:
        """Wikipedia query

        Args:
            string_to_be_queried (str): Thing to look up on wikepedia (Ex: Ghonnerrea), it is a verbose name as that is what is printed by the device

        Returns:
             returned_obj (TBD): The test file returned
        """
        assert type(string_to_be_queried) is str, (
            f"you bad bad bad bad you, I want strings not, {type(string_to_be_queried)}s"
        )
        return "Im not implemented, I've never been implemented"
        # raise NotImplementedError

    def available_services(self) -> str:
        return "Available services: " + ", ".join(self.func_dict)   
