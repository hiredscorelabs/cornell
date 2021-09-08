#!/usr/bin/env python
# pylint: disable=no-member
import atexit
import logging
from collections import defaultdict
from contextlib import contextmanager, nullcontext
from functools import partial
from http import HTTPStatus
from os import environ
from pathlib import Path
import signal

import click
import requests
import yaml
from flask import Flask, request
from structlog import get_logger
from toolz import get_in
from werkzeug.exceptions import NotFound
from werkzeug.utils import secure_filename
from yarl import URL

from cornell.vcr_settings import get_custom_vcr, request_has_matches
from cornell.cornell_helpers import (get_vcr_dir_from_request, replace_locations_in_xml, xml_in_headers,
                                     set_underlying_vcr_logging_level, saved_data_to_yaml)
from cornell.signals import on_cornell_exit, signal_context


app = Flask("CornellMock")
DUMMY_URL = "http://cornell-proxy/"
SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
ROOT_NAME = "root"


class CassetteFileMissing(NotFound):
    pass


@app.route("/ping", methods=["GET"])
def ping():
    return "Pong!"


@app.route('/', defaults={'path': '', }, methods=SUPPORTED_METHODS)
@app.route('/<path:path>', methods=SUPPORTED_METHODS)
def handle_requests(path):
    app.logger.info("Got request", url=request.url, method=request.method, args=request.args, body=request.get_data())
    with _cassette_url_player_context(path) as updated_path:
        initial_request = _build_initial_request(updated_path)
        resp = requests.Session().send(initial_request.prepare(), stream=True)
        response_body = _process_response_body(resp)
        _processes_headers(resp)
    return response_body, resp.status_code, resp.headers.items()


def _build_initial_request(path):
    headers = dict(request.headers)
    headers.pop("Host")
    url = URL(app.config.base_uri) / path
    if 'wsdl' in request.args:
        url = url.with_query("wsdl")
        request.args = None # pylint: disable=assigning-non-slot
    return requests.Request(request.method, url=url, headers=headers, data=request.data, params=request.args)


def _process_response_body(response):
    response_body = response.raw.read()
    if app.config.record and xml_in_headers(response):
        response_body = replace_locations_in_xml(response_body)
    return response_body


def _processes_headers(resp):
    if resp.status_code not in (HTTPStatus.TEMPORARY_REDIRECT, HTTPStatus.PERMANENT_REDIRECT):
        # https://github.com/psf/requests/issues/3490
        for header in ('Content-Length', 'Content-Type', 'Transfer-Encoding'):
            resp.headers.pop(header, None)


@contextmanager
def _cassette_url_player_context(url_path):
    vcr_dir = ROOT_NAME
    if not app.config.fixed_path:
        vcr_dir = get_vcr_dir_from_request()
        url_path = "/".join(URL(url_path).parts[1:])
        app.logger.info(f"url path updated to {url_path}")
    saved_cassette_name = get_in([vcr_dir, f"/{url_path}"], app.config.cassette_paths)
    cassette_file_path = _determine_cassette_path(saved_cassette_name, vcr_dir)

    with signal_context("process_cassette_file", cassette_file_path) as cassette_file:
        cassette_file = cassette_file or cassette_file_path
        cassette_path = _determine_cassette_path(cassette_file, vcr_dir)

    if not cassette_path or not cassette_path.exists():
        if not app.config.record:
            raise CassetteFileMissing(description=f"Cassette file for {url_path} is missing."
                                                  f" Did you forget to record it?")
        cassette_path = _generate_cassette_path(vcr_dir, url_path)
        app.logger.info(f"Cassette file will be recorded to {cassette_path}")
        player_context = partial(app.config.vcr.use_cassette, cassette_path)
    else:
        player_context = _obtain_player_context(str(cassette_path))

    with set_underlying_vcr_logging_level(), player_context():
        yield url_path
    added_path = {f"/{url_path}": Path(cassette_file).name if cassette_file else Path(cassette_path).name}
    app.config.cassette_paths.setdefault(vcr_dir, {}).update(added_path)


def _determine_cassette_path(cassette_file, vcr_dir):
    if not cassette_file:
        return
    if app.config.fixed_path:
        return (Path(app.config.cassettes_dir)/cassette_file).absolute()
    return (Path(app.config.cassettes_dir)/vcr_dir/cassette_file).absolute()


def _obtain_player_context(cassette_path):
    app.logger.info("Using cassette", cassette_path=cassette_path)
    if app.config.record and app.config.record_once and request_has_matches(cassette_path, request):
        app.logger.info("Request already found in cassette, not recording", cassette_path=cassette_path, url=request.url)
        return nullcontext
    return partial(app.config.vcr.use_cassette, cassette_path, record_mode="new_episodes")


def _generate_cassette_path(vcr_dir, url_path):
    file_path = f'{secure_filename(url_path)}.yaml' if url_path else "null"
    record_path = app.config.cassettes_dir if app.config.fixed_path else _get_vcr_dir(vcr_dir)
    return str((record_path / file_path).absolute())


def _load_cassette_paths(parent_dir):
    if app.config.index_file.exists():
        return yaml.safe_load(app.config.index_file.read_text())
    app.logger.info("Could not find index file. Creating new file", parent_dir=parent_dir)
    cassette_paths = {}
    for file_path in parent_dir.glob("**/*.yaml"):
        cassette_data = yaml.safe_load(file_path.read_text())
        for interaction in cassette_data.get("interactions", []):
            relative_url = URL(get_in(["request", "uri"], interaction)).relative().raw_path
            cassette_paths.setdefault(relative_url, str(file_path))
    return _generate_index_yaml(parent_dir, cassette_paths)


def _generate_index_yaml(parent_dir, cassette_paths):
    index_dict = defaultdict(dict)
    for url, cassette_path in cassette_paths.items():
        parent = Path(cassette_path).relative_to(parent_dir).parent
        file_name = Path(cassette_path).relative_to(parent_dir).name
        parent = parent if parent.stem else "root"
        index_dict[str(parent)].update({url: file_name})

    saved_data_to_yaml(index_dict, app.config.index_file)
    app.logger.info("Index file was created", parent_dir=parent_dir, index_file_path=app.config.index_file)
    return index_dict


def _get_vcr_dir(cassettes_dir):
    record_path = app.config.cassettes_dir / Path(cassettes_dir).expanduser()
    return create_cassettes_dir(record_path)


def create_cassettes_dir(cassettes_dir):
    home_dir = cassettes_dir or Path(__file__).absolute().parent / "cassettes"
    Path(home_dir).mkdir(parents=True, exist_ok=True)
    return Path(home_dir)


def _setup_app_config(*, app, cassettes_dir, fixed_path, forward_uri, record, record_once, additional_vcr_matchers):
    environ["FLASK_ENV"] = environ.get("FLASK_ENV") or "local"
    app.config.cassettes_dir = create_cassettes_dir(cassettes_dir)
    app.config.record = record
    app.config.record_once = record_once
    app.config.base_uri = forward_uri if record else DUMMY_URL
    app.config.fixed_path = fixed_path
    app.config.index_file = (Path(app.config.cassettes_dir)/"index.yaml").absolute()
    app.config.cassette_paths = _load_cassette_paths(app.config.cassettes_dir)
    app.config.vcr = get_custom_vcr(app.config.base_uri, DUMMY_URL, *additional_vcr_matchers)


def _get_logging_service():
    logger = get_logger()
    logger.level = logging.INFO
    return logger


class CornellCmdOptions(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = [click.core.Option(("-cd", "--cassettes-dir"), required=False,
                                     help="Cassettes parent directory, If not specified, Cornell parent dir will be used"),
                   click.core.Option(("-fp", "--fixed-path"), required=False, default=False, is_flag=True,
                                     help="Fixed cassettes path. If enabled, Cornell will support only one server for recording"),
                   click.core.Option(("-r", "--record"), default=False, is_flag=True,
                                     help="Start server in record mode"),
                   click.core.Option(("-", "--record-once/--record-all"), default=True, is_flag=True,
                                     help="Record each scenario only once, ignore the rest"),
                   click.core.Option(("-ff", "--forward_uri"), help="Must be provided in case of recording mode"),
                   click.core.Option(("-p", "--port"), default=9000)]
        for option in options:
            self.params.insert(0, option)


@click.command(cls=CornellCmdOptions)
def start_mock_service(cassettes_dir, fixed_path, record, record_once, forward_uri, port):
    """
    Usage Examples:
    Record mode: `cornell --forward_uri="https://remote_server/api" --record -cd custom_cassette_dir`
    Replay mode: `cornell -cd custom_cassette_dir
    """
    start_cornell(cassettes_dir=cassettes_dir, forward_uri=forward_uri, port=port, record=record,
                  record_once=record_once, fixed_path=fixed_path)


def start_cornell(*, cassettes_dir, forward_uri, port, record, record_once, fixed_path, additional_vcr_matchers=()):
    app.config.update(PROPAGATE_EXCEPTIONS=True)
    if record and not forward_uri:
        raise click.ClickException("Record mode requires forward URI")

    with signal_context("logging_setup") as logging_service:
        app.logger = logging_service or _get_logging_service()

    _setup_app_config(app=app, cassettes_dir=cassettes_dir, fixed_path=fixed_path, forward_uri=forward_uri,
                      record=record, record_once=record_once, additional_vcr_matchers=additional_vcr_matchers)
    app.logger.info("Starting Cornell", app_name=app.name, port=port, record=record, record_once=record_once,
                    fixed_path=fixed_path, forward_uri=forward_uri, cassettes_dir=str(cassettes_dir))
    atexit.register(on_cornell_exit, app=app)
    signal.signal(signal.SIGTERM, lambda: on_cornell_exit(app))
    app.run(port=port, threaded=False)


if __name__ == "__main__":
    start_mock_service()  # pylint: disable=no-value-for-parameter
