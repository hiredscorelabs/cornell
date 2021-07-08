import functools

from vcr.matchers import query, body
from vcr.util import read_body

from cornell.cornell_helpers import expand_in_query, ODATA_EXPEND_FILTER, xml_in_headers, \
    strip_soap_namespaces_from_body


def requests_match_conditions(*conditions):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(received_request, cassette_request):
            if all([condition(received_request) and condition(cassette_request) for condition in conditions]):
                return func(received_request, cassette_request)
            # Condition unmet, return True to skip the matcher
            return True
        return wrapper
    return decorator


def replace_matchers(custom_matcher, *conditions):
    """
    If conditions are met, replace matcher with custom matcher
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(received_request, cassette_request):
            if all([condition(received_request) and condition(cassette_request) for condition in conditions]):
                return custom_matcher(received_request, cassette_request)
            return func(received_request, cassette_request)
        return wrapper
    return decorator


def _vcr_odata_query_matcher(received_request, cassette_request):
    received_request_query, cassette_request_query = dict(received_request.query), dict(cassette_request.query)

    received_expand_query = received_request_query[ODATA_EXPEND_FILTER]
    cassette_expand_query = cassette_request_query[ODATA_EXPEND_FILTER]

    received_request_query.pop(ODATA_EXPEND_FILTER)
    cassette_request_query.pop(ODATA_EXPEND_FILTER)

    assert received_request_query == cassette_request_query, "OData queries don't match"
    assert set(received_expand_query.split(",")) == set(cassette_expand_query.split(",")), f"Odata {ODATA_EXPEND_FILTER} don't match"


@replace_matchers(_vcr_odata_query_matcher, expand_in_query, lambda request: request.query)
def extended_query_matcher(received_request, cassette_request):
    query(received_request, cassette_request)


def _vcr_xml_body_matcher(cassette_request, received_request):
    received_request_body = read_body(received_request)
    cassette_request_body = read_body(cassette_request)
    assert strip_soap_namespaces_from_body(received_request_body) == strip_soap_namespaces_from_body(cassette_request_body)


@replace_matchers(_vcr_xml_body_matcher, xml_in_headers, lambda request: request.body)
def extended_vcr_body_matcher(received_request, cassette_request):
    body(cassette_request, received_request)
