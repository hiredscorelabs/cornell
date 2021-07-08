import vcr
from flask import request
from vcr.cassette import Cassette
from vcr.request import Request
from vcr.matchers import method
from vcr.persisters.filesystem import FilesystemPersister

from cornell.cornell_helpers import (replace_locations_in_xml, xml_in_headers, strip_soap_namespaces_from_body,
                                     set_underlying_vcr_logging_level)
from cornell.custom_matchers import extended_query_matcher, extended_vcr_body_matcher

MATCHERS = {'host', 'method', 'path', 'port', 'scheme'}


class CustomPersister(FilesystemPersister):
    base_uri = None
    mock_url = None

    @classmethod
    def save_cassette(cls, cassette_path, cassette_dict, serializer):
        for cassette_request in cassette_dict["requests"]:
            cassette_request.uri = cassette_request.uri.replace(cls.base_uri, cls.mock_url)
            if cassette_request.body and xml_in_headers(cassette_request):
                cassette_request.body = strip_soap_namespaces_from_body(cassette_request.body)

        for cassette_response in cassette_dict["responses"]:
            if any("xml" in content_type for content_type in cassette_response["headers"].get('Content-Type', [])):
                cassette_response["body"]["string"] = replace_locations_in_xml(cassette_response["body"]["string"])
        FilesystemPersister.save_cassette(cassette_path, cassette_dict, serializer)


def get_custom_vcr(base_uri, mock_uri, *additional_vcr_matchers):
    custom_vcr = vcr.VCR(decode_compressed_response=True)
    CustomPersister.base_uri = base_uri.rstrip("/")
    CustomPersister.mock_url = mock_uri.rstrip("/")
    custom_vcr.register_persister(CustomPersister)
    match_on_list = MATCHERS
    match_on_list.update(_register_additional_matchers(custom_vcr, *additional_vcr_matchers, extended_vcr_body_matcher,
                                                       extended_query_matcher))
    custom_vcr.match_on = tuple(match_on_list)
    return custom_vcr


def _register_additional_matchers(custom_vcr, *additional_vcr_matchers):
    matchers = set()
    for matcher in additional_vcr_matchers:
        assert callable(matcher), f"VCR matcher must be callable, for {type(matcher)} instead"
        custom_vcr.register_matcher(matcher.__name__, matcher)
        matchers.add(matcher.__name__)
    return matchers


def request_has_matches(cassette_path, flask_request):
    cassette_requests = Request(method=flask_request.method, uri=request.url, body=flask_request.data, headers=flask_request.headers)
    with set_underlying_vcr_logging_level():
        cassette = Cassette.load(path=cassette_path, match_on=(extended_vcr_body_matcher, extended_query_matcher,
                                                               method, extended_vcr_body_matcher))
    for matches in cassette.find_requests_with_most_matches(cassette_requests):
        *_, failure = matches
        if not failure:
            return True
    return False
