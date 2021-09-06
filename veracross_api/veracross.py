"""
A Veracross API class for the v3 API

This class provides an easy interface to the Veracross API for python.

Rate limiting and pagination will be handled automatically.

Based on: https://gist.github.com/kiwidamien/09bb2d4a55c9fb3b265697ba12c1ff8e
See also: https://kiwidamien.github.io/getting-data-with-oauth.html
"""

__author__ = "Matthew Denaburg"


import time
import requests
import base64


_TOKEN_URL = "https://accounts.veracross.com/{school_short_name}/oauth/token"
_DATA_URL = "https://api.veracross.com/{school_short_name}/v3/"


def base64_encode_string(string: str) -> str:
    """return a string encoded in base 64"""

    return base64.b64encode(string.encode()).decode()


class Veracross:
    """A Veracross V3 API wrapper."""

    def __init__(self, school_short_name: str, client_id: str,
                 client_secret: str) -> None:
        self.rate_limit_remaining = 300
        self.rate_limit_reset = 0

        self.school_short_name = school_short_name

        self.token_url = _TOKEN_URL.format(school_short_name=school_short_name)
        self.data_url = _DATA_URL.format(school_short_name=school_short_name)

        self.token = None

        self.__client_id = client_id
        self.__client_secret = client_secret

    def _set_timers(self, limit_remaining: int, limit_reset: int) -> None:
        """
        Sets the rate limits.

        :param limit_remaining: Count of API calls remaining from header
        X-Rate-Limit-Remaining
        :param limit_reset: Reset Timer from header X-Rate-Limit-Reset
        """

        self.rate_limit_remaining = int(limit_remaining)
        self.rate_limit_reset = int(limit_reset)

        if self.rate_limit_remaining == 1:
            time.sleep(self.rate_limit_reset + 1)

    def _get_token(self):
        """Get an access token

        :returns: the token
        """

        headers = {
            "Authorization": "Basic " +
            base64_encode_string(f"{self.__client_id}:{self.__client_secret}"),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        params = {
            "grant_type": "client_credentials"
        }

        r = requests.post(_TOKEN_URL, headers=headers, params=params)

        self.token = r.json()["access_token"]
        return self.token

    def pull(self, endpoint: str, include_value_lists: bool,
             path_parameters: str, **query_parameters):
        """Get Veracross data with pagination"""

        if self.token is None:
            self._get_token()

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        # if we want/need value lists
        if include_value_lists:
            headers["X-API-Value-Lists"] = "include"

        response = requests.get(self.data_url, headers=headers)

        result = {
            "records": [],
            "value_lists": {}
        }

        if response.status_code == 200:
            page = 1
            pages = 1

            # if there are multiple pages
            if "X-Total-Count" in response.headers:
                pages = int(response.headers["X-Total-Count"]) // 100 + 1

            while page <= pages:
                json_data = response.json()
                data = json_data.get("data", [])

                if isinstance(data, list):
                    result["records"].


class VeracrossAPIResult:
    """   """

    __slots__ = ("fields",)

    def __init__(self):
        pass
