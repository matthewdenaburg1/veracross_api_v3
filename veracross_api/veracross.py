"""
A Veracross API class for the v3 API

This class provides an easy interface to the Veracross API for python.

Rate limiting and pagination will be handled automatically.
"""

__author__ = "Matthew Denaburg"


from typing import List, Dict, NewType
import time

import requests

StrOrInt = NewType("StrOrInt", [str, int])


class Veracross:
    """A Veracross V3 API wrapper."""

    def __init__(self, school_short_name: str, client_id: str,
                 client_secret: str, scopes: List[str]) -> None:

        self.school_short_name = school_short_name

        token_url = "https://accounts.veracross.com/{}/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": " ".join(scopes)
        }

        try:
            response = requests.post(token_url.format(school_short_name),
                                     headers=headers, params=params)

            response.raise_for_status()
            self._token = response.json()
        except requests.exceptions.HTTPError:
            raise

    ###############

    def pull(self, endpoint: str, record_id: int = None, **query_parameters):
        """Get Veracross data with pagination.

        If `record_id` is provided, `query_parameters` is ignored.

        :param endpoint: which endpoint to pull data from.
        :param record_id: an optional record id to retrieve
        """
        headers = {
            "Authorization": f"Bearer {self._token['access_token']!s}",
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

        return _insert_from_value_list(**result)


def _insert_from_value_list(value_lists, data) -> List[Dict[str, StrOrInt]]:
    """
    Iterate through the value list and change any matching fields in `data` to
    use the value from the value list instead.
    """

    # if no data was provided, return an empty list
    if len(data) == 0:
        return []

    # first build a better data structure from the value_lists object
    value_lists_d = dict()
    for typ in value_lists:
        obj = dict()
        # if we have categories, insert them too
        for item in typ["items"]:
            if "category" in item:
                # find the desired category
                for cat in typ["categories"]:
                    if item["category"] == cat["id"]:
                        item["category"] = cat["description"]

            id_ = item.pop("id", None)
            obj[id_] = item

        # add the items to the new structure
        for field in typ["fields"]:
            # value_lists_d[field] = typ["items"]
            value_lists_d[field] = obj

    # iterate through the data and update the values of keys.
    for data_point in data:
        for field, value in data_point.items():
            # skip the id field
            if field == "id":
                continue

            # if the field is something we need to change out
            if field in value_lists_d:
                # do so
                data_point[field] = value_lists_d[field][value]["description"]

    return data
