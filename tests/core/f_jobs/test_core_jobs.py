import pytest
import logging
from tests.utils import default_check, check_response
from .core_jobs_dataset import (
    get_jobs_dataset,
    add_job_dataset,
    pause_job_dataset,
    resume_job_dataset,
    reschedule_job_dataset,
    delete_job_dataset
)

log = logging.getLogger(__name__)


@pytest.fixture
def client(get_mis_client):
    return get_mis_client


@pytest.mark.parametrize("params, expected", get_jobs_dataset)
def test_get_tasks(client, params, expected):
    response = client.get("/jobs", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("request_data , expected", add_job_dataset)
def test_add_job(client, request_data, expected):
    response = client.post("/jobs/add", json=request_data)
    assert default_check(response)
    assert check_response(response, expected, ["next_run_time"])


# @pytest.mark.parametrize("params,expected", resume_job_dataset)
# def test_resume_job(client, params, expected):
#     response = client.post("/jobs/resume", params=params)
#     assert default_check(response)
#     assert check_response(response, expected)
#
#
# @pytest.mark.parametrize("params,expected", pause_job_dataset)
# def test_pause_job(client, params, expected):
#     response = client.post("/jobs/pause", params=params)
#     assert default_check(response)
#     assert check_response(response, expected)
#
#
# @pytest.mark.parametrize("request_data, params, expected", reschedule_job_dataset)
# def test_reschedule_job(client, request_data, params, expected):
#     response = client.post("/jobs/reschedule", params=params, json=request_data)
#     assert default_check(response)
#     assert check_response(response, expected)
#
#
# @pytest.mark.parametrize("params,expected", delete_job_dataset)
# def test_delete_job(client, params, expected):
#     response = client.delete("/jobs/remove", params=params)
#     assert default_check(response)
#     assert check_response(response, expected)
