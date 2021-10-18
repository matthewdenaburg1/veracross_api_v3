"""
A Veracross API class for the v3 API

This class provides an easy interface to the Veracross API for python.

Rate limiting and pagination will be handled automatically.

Based on: https://gist.github.com/kiwidamien/09bb2d4a55c9fb3b265697ba12c1ff8e
See also: https://kiwidamien.github.io/getting-data-with-oauth.html
"""

__author__ = "Matthew Denaburg"


from typing import List
import base64
import time

import requests
from requests_oauthlib import OAuth2Session


_TOKEN_URL = "https://accounts.veracross.com/{school_short_name}/oauth/token"
_DATA_URL = "https://api.veracross.com/{school_short_name}/v3"


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

        self.session = OAuth2Session(client_id)

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

    def get_token(self, scope: List[str]):
        """Get an access token with the specified scopes

        :returns: the token
        """

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        params = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "grant_type": "client_credentials",
            "scope": " ".join(scope)
        }

        response = requests.post(self.token_url, headers=headers, params=params)

        self.token = response.json()
        return self.token

    def pull(self, endpoint: str, record_id: int = None, **query_parameters):
        """Get Veracross data with pagination.

        If `record_id` is provided, `query_parameters` is ignored.

        :endpoint: which endpoint to pull data from.
        :record_id: an optional record id to attach to the end of the endpoint.
        """

        headers = {
            "Authorization": f"Bearer {self.token['access_token']!s}",
            "X-API-Value-Lists": "include"
        }

        url = f"{self.data_url}/{endpoint}"
        if isinstance(record_id, int):
            url = url + f"/{record_id!s}"

        response = requests.get(url, headers=headers)
        result = list()

        if response.status_code == 200:
            page = 1
            pages = 1

            # if there are multiple pages
            if "X-Total-Count" in response.headers:
                pages = int(response.headers["X-Total-Count"]) // 100 + 1

            while page <= pages:
                data = response.json().get("data")
                result.append(data)

                page += 1
                self._set_timers(response.headers["X-Rate-Limit-Remaining"],
                                 response.headers["X-Rate-Limit-Reset"])
                response = None

        return result


class VeracrossAPIResult:
    """   """

    __slots__ = ("fields",)

    def __init__(self):
        pass
