from enum import Enum


class LpApiType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class LpApiCall:
    def __init__(self, url, type=LpApiType.POST, headers=None, json=None, params=None):
        self.type = type
        self.url = url
        self.headers = headers
        self.body = json
        self.params = params
