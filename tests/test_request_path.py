import pytest


@pytest.mark.parametrize(("query_string", "expected"), [({"wsdl": ""}, "with_wsdl"), ({"no_wsdl": "no_wsdl"}, "hi")])
def test_wsdl(cornell_proxy, query_string, expected):
    resp = cornell_proxy.get('hi', query_string=query_string)
    assert resp.data.decode() == expected
