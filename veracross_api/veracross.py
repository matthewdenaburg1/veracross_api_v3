"""
A Veracross API class for the v3 API

This class provides an easy interface to the Veracross API for python.

Rate limiting and pagination will be handled automatically.

Based on: https://gist.github.com/kiwidamien/09bb2d4a55c9fb3b265697ba12c1ff8e
See also: https://kiwidamien.github.io/getting-data-with-oauth.html
"""

__author__ = "Matthew Denaburg"


from typing import List
import time

import requests


class Veracross:
    """A Veracross V3 API wrapper."""

    def __init__(self, school_short_name: str, client_id: str,
                 client_secret: str, scope: List[str]) -> None:

        self.rate_limit_remaining = 300
        self.rate_limit_reset = 0

        self.school_short_name = school_short_name

        token_url = "https://accounts.veracross.com/{}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": " ".join(scope)
        }

        try:
            response = requests.post(token_url.format(school_short_name),
                                     headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            # TODO some sort of log
            raise SystemExit(f"{response.headers['Status']}: Count not create "
                             "OAuth2 access token.")

        self.token = response.json()

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
            sleep_for = self.rate_limit_reset - int(time.time())
            time.sleep(sleep_for)

    def pull(self, endpoint: str, record_id: int = None, **query_parameters):
        """Get Veracross data with pagination.

        If `record_id` is provided, `query_parameters` is ignored.

        :endpoint: which endpoint to pull data from.
        :record_id: an optional record id to attach to the end of the endpoint.
        """

        headers = {
            "Authorization": f"Bearer {self.token['access_token']!s}",
            "X-API-Value-Lists": "include",
            "X-Page-Size": "100",
        }

        data_url = f"https://api.veracross.com/{self.school_short_name}/v3"
        url = f"{data_url}/{endpoint}"
        if isinstance(record_id, int):
            url = url + f"/{record_id!s}"

        try:
            response = requests.get(url, headers=headers,
                                    params=query_parameters)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # TODO some sort of log
            raise SystemExit(err)

        # only retrieve value lists once
        if "X-API-Value-Lists" in headers:
            headers.pop("X-API-Value-Lists")

        result = {
            "data": [],
            "value_lists": response.json().get("value_lists")
        }

        page = 1
        while True:
            data = response.json().get("data")
            if isinstance(data, dict):
                result["data"].append(data)
                break

            result["data"].extend(data)

            # if we have fewer results than the requested page size, we're done.
            if len(data) < int(headers["X-Page-Size"]):
                break

            headers["X-Page-Number"] = str(page)
            page += 1
            self._set_timers(response.headers["x-rate-limit-remaining"],
                             response.headers["x-rate-limit-reset"])
            response = requests.get(url, headers=headers,
                                    params=query_parameters)

        return result


class VeracrossAPIResult:
    """   """

    __slots__ = ("fields", "data",)

    def __init__(self):
        pass
