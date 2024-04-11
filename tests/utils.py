import logging
import json

log = logging.getLogger(__name__)


# function to check for JSON String validity
def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False


# compare two json objects with ignore_key possibility
def compare_json_with_ignore_keys(file_1, file_2, ignored_keys):
    ignored = set(ignored_keys)
    for k1, v1 in file_1.iteritems():
        if k1 not in ignored and (k1 not in file_2 or file_2[k1] != v1):
            return False

    for k2, v2 in file_2.iteritems():
        if k2 not in ignored and k2 not in file_1:
            return False

    return True


def _sorted(json_data):
    if isinstance(json_data, dict):
        return sorted((k, _sorted(v)) for k, v in json_data.items())
    if isinstance(json_data, list):
        return sorted(_sorted(x) for x in json_data)
    else:
        return json_data


def compare_json(json1, json2):

    return _sorted(json1) == _sorted(json2)


# default check for get queries
def default_check(response):
    return response.status_code == 200 and is_valid_json(response.text)


def pretty_json(json_data):
    return json.dumps(json_data, indent=4)
