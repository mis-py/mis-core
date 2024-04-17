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


def _sorted(json_data, ignore_keys: list = None):
    def check_key(key):
        if ignore_keys is None:
            return True

        if ignore_keys is not None and key in ignore_keys:
            return False
        else:
            return True

    if isinstance(json_data, dict):
        return sorted((k, _sorted(v, ignore_keys)) for k, v in json_data.items() if check_key(k))
    if isinstance(json_data, list):
        return sorted(_sorted(x, ignore_keys) for x in json_data if check_key(x))
    else:
        return json_data


def compare_json(json1, json2, ignore_keys: list = None):
    return _sorted(json1, ignore_keys) == _sorted(json2, ignore_keys)


# default check for get queries
def default_check(response):
    return response.status_code == 200 and is_valid_json(response.text)


def pretty_json(json_data):
    return json.dumps(json_data, indent=4)


def check_response(response, expected, ignore_keys:list = None):
    response_json = response.json()

    log.info(pretty_json(response_json))
    log.info(pretty_json(expected))

    return compare_json(response_json, expected, ignore_keys)
