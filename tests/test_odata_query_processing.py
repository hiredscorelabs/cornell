import random
import copy
from unittest.mock import MagicMock
import pytest

from cornell.cornell_helpers import ODATA_EXPEND_FILTER
from cornell.custom_matchers import extended_query_matcher


@pytest.fixture
def odata_query():
    return {'$expand':
                'veteranStatus/picklistLabels,QueryQuestionResponse,item/state/picklistLabels,'
                'resume,workAuth/picklistLabels,referralSource/picklistLabels,item/education/degreeNav/picklistLabels,'
                'education,item/mobility/willingnessNav/picklistLabels,item/outsideWorkExperience,Requisition,AppStatus,'
                'QueryStatusAuditTrail/AppStatus,highestEducation/picklistLabels,coverLetter,race/picklistLabels,'
                'item/ReqFwditems,item/mobility/locationNav/picklistLabels,supportingDoc',
            '$filter': "QueryId eq '666'",
            '$format': 'json',
            '$inlinecount': 'allpages'}


def test_odata_expand_identical(odata_query):
    cassette_request, received_request = MagicMock(), MagicMock()
    received_odata_query = copy.deepcopy(odata_query)
    query = odata_query[ODATA_EXPEND_FILTER].split(",")
    received_odata_query[ODATA_EXPEND_FILTER] = ",".join(random.sample(query, len(query)))
    cassette_request.query = list(received_odata_query.items())
    received_request.query = list(odata_query.items())
    extended_query_matcher(received_request, cassette_request)


def test_odata_expand_different_content(odata_query):
    cassette_request, received_request = MagicMock(), MagicMock()
    received_odata_query = copy.deepcopy(odata_query)
    odata_query[ODATA_EXPEND_FILTER] += ",more,items"
    cassette_request.query, received_request.query = list(received_odata_query.items()), list(odata_query.items())
    with pytest.raises(AssertionError) as err:
        extended_query_matcher(received_request, cassette_request)
    err.match(f"Odata \\{ODATA_EXPEND_FILTER} don't match")


def test_odata_expand_different_query(odata_query):
    cassette_request, received_request = MagicMock(), MagicMock()
    received_odata_query = copy.deepcopy(odata_query)
    odata_query["$filter"] = "different query"
    cassette_request.query, received_request.query = list(received_odata_query.items()), list(odata_query.items())
    with pytest.raises(AssertionError) as err:
        extended_query_matcher(received_request, cassette_request)
    err.match("OData queries don't match")


def test_odata_identical_without_expend(odata_query):
    cassette_request, received_request = MagicMock(), MagicMock()
    odata_query.pop(ODATA_EXPEND_FILTER)
    cassette_request.query, received_request.query = list(odata_query.items()), list(odata_query.items())
    extended_query_matcher(received_request, cassette_request)


def test_odata_different_without_expend(odata_query):
    cassette_request, received_request = MagicMock(), MagicMock()
    odata_query.pop(ODATA_EXPEND_FILTER)
    received_odata_query = copy.deepcopy(odata_query)
    odata_query["$format"] = "different format"
    cassette_request.query, received_request.query = list(received_odata_query.items()), list(odata_query.items())
    with pytest.raises(AssertionError) as err:
        extended_query_matcher(received_request, cassette_request)
    err.match("!=")
