import pytest
import yaml
from vcr.serializers import yamlserializer
from vcr.request import Request
from cornell.vcr_settings import CustomPersister


@pytest.mark.parametrize("record_errors", (True, False))
def test_record_errors_toggle(cornell_proxy, record_errors):
    cornell_proxy.application.config.record_errors = record_errors
    cornell_proxy.get("not_found")
    assert (cornell_proxy.application.config.cassette_paths["root"] == {}) != record_errors


@pytest.mark.parametrize("record_errors", (True, False))
def test_record_errors_to_cassette(temp_yaml_file, record_errors):
    custom_persister = CustomPersister()

    cassette_request = Request(
        **{'method': 'GET', 'uri': 'http://127.0.0.1:8080/test',
           'body': None,
           'headers': {'User-Agent': 'python-requests/2.26.0', 'Accept-Encoding': 'gzip, deflate',
                       'Accept': '*/*', 'Connection': 'keep-alive'}})
    cassette_response = {'status': {'code': 401, 'message': 'Unauthorized'},
                         'headers': {'Server': ['http-kit'], 'Content-Length': ['19'],
                                     'Date': ['Fri, 15 Oct 2021 10:41:06 GMT']},
                         'body': {'string': b'Unauthorized access'}}

    cassette_request.uri = 'http://127.0.0.1:8080/test'
    cassette_dict = {"requests": [cassette_request],
                     "responses": [cassette_response]}
    CustomPersister.record_errors = record_errors
    CustomPersister.base_uri = "http://127.0.0.1:8080"
    CustomPersister.mock_url = "http://cornell"
    custom_persister.save_cassette(temp_yaml_file, cassette_dict, yamlserializer)
    output = open(temp_yaml_file, encoding="utf-8")
    if record_errors:
        assert yaml.safe_load(output)["interactions"] == [{"request": cassette_request._to_dict(), # pylint: disable=protected-access
                                                           "response": cassette_response}]
    else:
        assert output.read() == "0"
