
# TODO Notifications tests temporarily disabled coz currently system don't have any events without initialized modules

# import pytest
# import logging
# from tests.utils import default_check, check_response
# from .core_notifications_dataset import (
#     get_notifications_dataset,
#     edit_notifications_dataset
# )
#
# log = logging.getLogger(__name__)
#
#
# @pytest.fixture
# def client(get_mis_client):
#     return get_mis_client
#
#
# @pytest.mark.parametrize("params, expected", get_notifications_dataset)
# def test_get_notifications(client, params, expected):
#     response = client.get("/notifications", params=params)
#     assert default_check(response)
#     assert check_response(response, expected)
#
#
# @pytest.mark.parametrize("params,expected", edit_notifications_dataset)
# def test_edit_notifications(client, params, expected):
#     response = client.edit("/notifications/edit", params=params)
#     assert default_check(response)
#     assert check_response(response, expected)
