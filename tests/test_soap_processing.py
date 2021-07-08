from unittest import mock
from unittest.mock import MagicMock

import xmltodict
from toolz import get_in

from cornell.cornell_helpers import replace_locations_in_xml, get_paths_in_nested_dict_by_condition, strip_soap_namespaces_from_body
from .conftest import TEST_URL

TEST_XML = '<SOAP-ENV:Envelope xmlns:SOAP-ENV=' \
           '"http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:' \
           'wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:ns0=' \
           '"http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="urn:com.monday.report/HiredScore_Candidate_History" xmlns:' \
           'cus="urn:com.monday/tenants/ochsner/data/custom"><wsse:Test location=' \
           '"http://another/location/address"></wsse:Test><SOAP-ENV:Header><wsse:Security mustUnderstand="true">' \
           '<wsse:UsernameToken><wsse:Username>ISU_HiredScore@ochsner</wsse:Username><wsse:Password>pass!' \
           '</wsse:Password></wsse:UsernameToken></wsse:Security><wsse:Test location=' \
           '"http://stam.com/address"></wsse:Test></SOAP-ENV:Header><ns0:Body><ns1:Execute_Report><ns1:' \
           'Report_Parameters><ns1:Candidate_ID>CAN_504434</ns1:Candidate_ID></ns1:Report_Parameters>' \
           '</ns1:Execute_Report></ns0:Body></SOAP-ENV:Envelope>'


def test_replace_locations_in_xml():
    with mock.patch("cornell.cornell_helpers.request", MagicMock()) as flask_request_mock:
        flask_request_mock.url = f"{TEST_URL}?wsdl"
        updated_xml = replace_locations_in_xml(TEST_XML)
    xml_dict = xmltodict.parse(updated_xml)
    paths = get_paths_in_nested_dict_by_condition(xml_dict, lambda key, value: key == "@location")
    for path in paths:
        assert get_in(path, xml_dict) == TEST_URL


def test_strip_namespaces_from_xml():
    xml_body = strip_soap_namespaces_from_body(TEST_XML)
    assert xml_body == '<?xml version="1.0" encoding="utf-8"?>\n<Execute_Report><Report_Parameters>' \
                       '<Candidate_ID>CAN_504434</Candidate_ID></Report_Parameters></Execute_Report>'


def test_strip_namespaces_from_xml_no_namespaces():
    no_namespaces_xml = '<Hey><Body><ID>666</ID></Body></Hey>'
    assert strip_soap_namespaces_from_body(no_namespaces_xml) == no_namespaces_xml
