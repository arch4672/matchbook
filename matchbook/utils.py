import datetime
import requests

from typing import Any, List, Dict

from matchbook.exceptions import ApiError


def clean_time(col):
    """
    Parse a UTC time column to datetime.

    :param col: column to be parsed.
    :returns: datetime column
    :rtype: series

    """
    return col.apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))


def filter_dicts(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter dict to remove None values.

    :param d: data to filter
    :type d: dict
    :returns: filtered data
    :rtype: dict

    """
    return {k: v for k, v in d.items() if v is not None}


def clean_locals(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean up locals dict, remove empty and self params.

    :params params: locals dicts from a function.
    :type params: dict
    :returns: cleaned locals dict to use as params for functions
    :rtype: dict
    """
    clean_params = {
        k: v
        for k, v in params.items()
        if v is not None and k != "self" and k != "session"
    }

    return {k.replace("_", "-"): v for k, v in clean_params.items()}


def check_call_complete(response: requests.Response):
    return response.get("total", 0) < (
        response.get("per-page", 20) + response.get("offset", 0)
    )


def check_status_code(response: requests.Response, codes: List[int] = None):
    """Checks response.status_code is in codes
    :param response: Requests response
    :param codes: List of accepted codes or callable
    :raises: StatusCodeError if code invalid
    """
    codes = codes or [200]
    if response.status_code not in codes:
        raise ApiError(response)
