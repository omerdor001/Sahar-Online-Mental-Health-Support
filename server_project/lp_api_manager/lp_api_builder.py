from lp_api_manager.lp_api_call import *

"""
LpApiBuilder Class

This class implements the Builder design pattern to construct lp_api_manager calls.

Attributes:
    base_url (str): The base URL for the lp_api_manager call.
    type (ApiType): The HTTP method type for the lp_api_manager call. Default is POST.
    headers (dict): The headers for the lp_api_manager call.
    json (dict): The JSON body for the lp_api_manager call.
    params (dict): The query parameters for the lp_api_manager call.

Methods:
    __init__(self, base_url="", type=ApiType.POST):
        Initializes the APIBuilder with the provided base URL and HTTP method type.

    add_type(self, type):
        Sets the HTTP method type for the lp_api_manager call.

    add_headers(self, headers):
        Adds headers to the lp_api_manager call.

    add_body(self, body):
        Adds a JSON body to the lp_api_manager call.

    add_params(self, params):
        Adds query parameters to the lp_api_manager call.

    build_call(self):
        Builds the lp_api_manager call using the specified parameters and returns an APICall object.
"""


class LpApiBuilder:
    def __init__(self, base_url="", type=LpApiType.POST):
        self.type = type
        self.base_url = base_url
        self.headers = {}
        self.json = None
        self.params = {}

    def add_type(self, type):
        self.type = type
        return self

    def add_headers(self, headers):
        self.headers.update(headers)
        return self

    def add_body(self, body):
        self.json = body
        return self

    def add_params(self, params):
        self.params.update(params)
        return self

    def build_call(self):
        return LpApiCall(
            self.base_url,
            type=self.type,
            headers=self.headers,
            json=self.json,
            params=self.params,
        )
