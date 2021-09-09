import logging
from collections.abc import Iterable
from contextlib import contextmanager
from urllib.parse import urlparse

import xmltodict
import yaml
from flask import request, current_app
from toolz import get_in
from yarl import URL


ODATA_EXPEND_FILTER = "$expand"


def get_vcr_dir_from_request():
    return URL(request.path.lstrip("/")).parts[0]


def get_localhost_uri():
    if current_app.config.fixed_path:
        return URL(request.host_url)
    return str(URL(request.host_url) / get_vcr_dir_from_request())


def get_paths_in_nested_dict_by_condition(response_body, condition, path=None):
    path = path or []
    if isinstance(response_body, Iterable) and not isinstance(
        response_body, (str, int, bool)
    ):
        items = (
            enumerate(response_body)
            if isinstance(response_body, list)
            else response_body.items()
        )
        for index_or_key, value in items:
            new_path = list(path)
            new_path.append(index_or_key)
            for result in get_paths_in_nested_dict_by_condition(
                value, condition, path=new_path
            ):
                yield result
            if isinstance(response_body, dict) and condition(index_or_key, value):
                new_path = list(path)
                new_path.append(index_or_key)
                yield new_path


def update_nested_dict_value(original_dict, old_value, new_value):
    if isinstance(original_dict, dict):
        for key, value in original_dict.copy().items():
            original_dict[key] = update_nested_dict_value(value, old_value, new_value)
        return original_dict
    elif isinstance(original_dict, list):
        for index in original_dict.copy():
            original_dict.append(update_nested_dict_value(index, old_value, new_value))
        return original_dict
    return original_dict if original_dict != old_value else new_value


def replace_locations_in_xml(response_body):
    def match_location_with_uri(key, value):
        if key == "@location":
            url = urlparse(value)
            return all([url.scheme, url.netloc, url.path])

    response_body_dict = xmltodict.parse(response_body)
    for location_paths in get_paths_in_nested_dict_by_condition(
        response_body_dict, match_location_with_uri
    ):
        old_location = get_in(location_paths, response_body_dict)
        new_location = request.url.split("?wsdl")[0]
        response_body_dict = update_nested_dict_value(
            response_body_dict, old_location, new_location
        )
    return xmltodict.unparse(response_body_dict)


def strip_soap_namespaces_from_body(request_data):
    processed_data = xmltodict.parse(request_data, process_namespaces=True)
    namespace_paths = sum(
        list(
            get_paths_in_nested_dict_by_condition(
                processed_data, condition=lambda key, _: key == "@xmlns"
            )
        ),
        [],
    )
    if not namespace_paths:
        processed_body = request_data
    else:
        body = _get_xml_body_without_namespaces(
            namespace_paths=namespace_paths,
            processed_data=processed_data,
            request_data=request_data,
        )
        processed_body = xmltodict.unparse(body)
    return (
        processed_body.decode() if isinstance(processed_body, bytes) else processed_body
    )


def _get_xml_body_without_namespaces(*, namespace_paths, processed_data, request_data):
    namespaces = get_in(namespace_paths, processed_data)
    stripped_namespaces = {value: None for value in namespaces.values()}
    without_namespaces = xmltodict.parse(
        request_data, process_namespaces=True, namespaces=stripped_namespaces
    )
    body_path = sum(
        list(
            get_paths_in_nested_dict_by_condition(
                without_namespaces, condition=lambda key, _: key == "Body"
            )
        ),
        [],
    )
    return get_in(body_path, without_namespaces)


def xml_in_headers(entity):
    return "/xml" in entity.headers.get("Content-Type", "")


def json_in_headers(entity):
    return "application/json" in entity.headers.get("Content-Type", "")


def expand_in_query(entity):
    return (
        entity.query
        and isinstance(entity.query, list)
        and [items for items in entity.query if ODATA_EXPEND_FILTER in items]
    )


@contextmanager
def set_underlying_vcr_logging_level(logging_level=logging.WARNING):
    vcr_logger = logging.getLogger("vcr.cassette")
    orig_level = vcr_logger.level
    vcr_logger.setLevel(logging_level)
    try:
        yield
    finally:
        vcr_logger.setLevel(orig_level)


def saved_data_to_yaml(data, yaml_path):
    yaml.safe_dump(
        dict(data), open(yaml_path, "w", encoding="utf-8"), encoding="utf-8", allow_unicode=True
    )
