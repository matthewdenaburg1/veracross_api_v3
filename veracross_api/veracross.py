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
            self.token = response.json()
        except requests.exceptions.HTTPError:
            # TODO some sort of log
            raise SystemExit(f"{response.headers['Status']}: Count not create "
                             "OAuth2 access token.")

    ###############

    def pull(self, endpoint: str, record_id: int = None, **query_parameters):
        """Get Veracross data with pagination.

        If `record_id` is provided, `query_parameters` is ignored.

        :param endpoint: which endpoint to pull data from.
        :param record_id: an optional record id to retrieve
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

        result = {
            "data": [],
            "value_lists": None,
        }
        page = 1

        try:
            while True:
                # make a data request
                response = requests.get(url, headers=headers,
                                        params=query_parameters)
                # if there was an HTTP error, raise it
                response.raise_for_status()

                # only retrieve value lists once
                if page == 1 and "X-API-Value-Lists" in headers:
                    headers.pop("X-API-Value-Lists")
                    result["value_lists"] = response.json().get("value_lists")

                # extract the data as json
                data = response.json().get("data")
                if len(data) == 1:
                    result["data"].append(data)
                    break

                result["data"].extend(data)

                # if we have fewer results than the requested page size, we're
                # done.
                if len(data) < int(headers["X-Page-Size"]):
                    break

                # increment page size and update header
                page += 1
                headers["X-Page-Number"] = str(page)

                # make sure we don't flood the api
                limit_remaining = response.headers.get("x-rate-limit-remaining")
                if limit_remaining is not None and int(limit_remaining) == 1:
                    time.sleep(int(response.headers.get("x-rate-limit-reset")) -
                               int(time.time()))

        except requests.exceptions.HTTPError:
            # TODO log that there was an HTTP error
            pass

        return result


class VeracrossAPIResult:
    """   """

    __slots__ = ("fields", "data",)

    def __init__(self):
        pass
