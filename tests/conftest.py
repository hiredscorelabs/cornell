from unittest.mock import MagicMock
import pytest
from cornell.cornell_server import app, _setup_app_config
from cornell.signals import process_cassette_file

TEST_URL = "http://some-address.com/some/path"


@pytest.fixture
def cornell_proxy(tmpdir, monkeypatch):
    _setup_app_config(app=app, cassettes_dir=tmpdir, forward_uri=TEST_URL, record=True, record_once=True,
                      fixed_path=True, additional_vcr_matchers=())
    cornell_proxy = app.test_client()
    monkeypatch.setattr(app.config.vcr, "use_cassette", MagicMock()) # pylint: disable=no-member
    return cornell_proxy


@pytest.fixture(autouse=True)
def mock_requests(requests_mock):
    mocked_requests_data = {"hi": "hi", "account_id/hi": "hi", "bye": "bye", "account_id/bye": "bye",
                            "parent/hi": "parent/hi", "hi?wsdl": "with_wsdl"}
    for url_path, output in mocked_requests_data.items():
        requests_mock.get(f"{TEST_URL}/{url_path}", text=output)


@pytest.fixture
def temp_yaml_file(tmpdir):
    expected_file = tmpdir/"hi.yaml"
    expected_file.write("0")
    return expected_file


@process_cassette_file.connect
def download_cassette_file(cassette_file):
    return cassette_file
