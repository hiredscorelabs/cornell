from unittest.mock import MagicMock

import cornell.vcr_settings
from cornell.vcr_settings import get_custom_vcr


def test_get_custom_vcr(monkeypatch):
    def custom_matcher():
        return

    vcr_mock = MagicMock()
    monkeypatch.setattr(cornell.vcr_settings, "vcr", vcr_mock)
    custom_vcr = get_custom_vcr(base_uri="base_uri", mock_uri="mock_uri", record_errors=True,
                                *[lambda x: x, custom_matcher])
    vcr_mock.VCR.assert_called_with(decode_compressed_response=True)
    assert sorted(custom_vcr.match_on) == sorted(('port', 'host', 'extended_vcr_body_matcher', 'scheme',
                                                  'extended_query_matcher', 'custom_matcher', '<lambda>', 'path',
                                                  'method'))
