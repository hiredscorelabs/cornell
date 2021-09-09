import requests

from cornell.cornell_server import _processes_headers


def test_process_headers_should_keep_content_type_on_ok_request():
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"

    _processes_headers(response)
    assert "Content-Type" in response.headers


def test_process_headers_should_remove_content_type_on_temporary_redirection():
    response = requests.Response()
    response.status_code = 307
    response.headers["Content-Type"] = "application/json"

    _processes_headers(response)
    assert "Content-Type" not in response.headers


def test_process_headers_should_remove_content_type_on_permanent_redirection():
    response = requests.Response()
    response.status_code = 308
    response.headers["Content-Type"] = "application/json"

    _processes_headers(response)
    assert "Content-Type" not in response.headers
