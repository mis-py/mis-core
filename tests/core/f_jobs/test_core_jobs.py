import pytest
import logging
from tests.utils import default_check, check_response, pretty_json
from .core_jobs_dataset import (
    get_jobs_dataset,
    add_job_dataset,
    pause_job_dataset,
    resume_job_dataset,
    reschedule_job_dataset,
    delete_job_dataset,
    positive_reschedule_job,
    negative_reschedule_job
)

log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def client(get_mis_client):
    get_mis_client.post('/modules/init', params={
        "module_id": 2
    })
    get_mis_client.post('/modules/start', params={
        "module_id": 2
    })

    yield get_mis_client

    get_mis_client.post('/modules/stop', params={
        "module_id": 2
    })
    get_mis_client.post('/modules/shutdown', params={
        "module_id": 2
    })


@pytest.mark.parametrize("request_data , expected", add_job_dataset)
def test_add_job(client, request_data, expected):
    response = client.post("/jobs/add", json=request_data)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, expected", get_jobs_dataset)
def test_get_jobs(client, params, expected):
    response = client.get("/jobs", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params,expected", resume_job_dataset)
def test_resume_job(client, params, expected):
    response = client.post("/jobs/resume", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params,expected", pause_job_dataset)
def test_pause_job(client, params, expected):
    response = client.post("/jobs/pause", params=params)
    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params, request_data, expected", positive_reschedule_job)
def test_reschedule_job(client, params, request_data, expected):
    response = client.post("/jobs/reschedule", params=params, json=request_data)

    # responsenew = client.get("/jobs/get_scheduler_jobs")
    # log.info(pretty_json(responsenew.json()))

    assert default_check(response)
    assert check_response(response, expected)


@pytest.mark.parametrize("params,expected", delete_job_dataset)
def test_delete_job(client, params, expected):
    response = client.delete("/jobs/remove", params=params)
    assert default_check(response)
    assert check_response(response, expected)

