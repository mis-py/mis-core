
import json


# function to check for JSON String validity
def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False


# compare two json objects with ignore_key possibility
def compare_json(file_1, file_2, ignored_keys):
    ignored = set(ignored_keys)
    for k1, v1 in file_1.iteritems():
        if k1 not in ignored and (k1 not in file_2 or file_2[k1] != v1):
            return False

    for k2, v2 in file_2.iteritems():
        if k2 not in ignored and k2 not in file_1:
            return False

    return True


# default check for get queries
def default_check(response):
    assert response.status_code == 200
    assert is_valid_json(response.text)

    json = response.json()

    # assert json.status

    return True
