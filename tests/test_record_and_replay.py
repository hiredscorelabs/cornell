from pathlib import Path

import pytest
from werkzeug.exceptions import NotFound


def test_record_once_new(tmpdir, cornell_proxy, temp_yaml_file):
    for _ in range(2):
        cornell_proxy.get('hi')
        cornell_proxy.application.config.vcr.use_cassette.assert_called_once_with(temp_yaml_file)
        assert cornell_proxy.application.config.cassette_paths == {'root': {'/hi': temp_yaml_file.basename}}
    cornell_proxy.get('bye')
    assert cornell_proxy.application.config.vcr.use_cassette.call_count == 2
    cornell_proxy.application.config.vcr.use_cassette.assert_called_with(tmpdir/"bye.yaml")
    assert cornell_proxy.application.config.cassette_paths == {"root": {'/hi': temp_yaml_file.basename, '/bye': "bye.yaml"}}


@pytest.mark.parametrize("fixed_path, root_path, saved_path, cassette_path", ((True, "root", "/account_id/hi", "account_id_hi"),
                                                                   (False, "account_id", "/hi", "account_id/hi")),
                         ids=("fixed_path", "not_fixed_path"))
def test_fixed_path(tmpdir, cornell_proxy, fixed_path, root_path, saved_path, cassette_path):
    cornell_proxy.application.config.fixed_path = fixed_path
    cornell_proxy.get('account_id/hi')
    args, *_ = cornell_proxy.application.config.vcr.use_cassette.call_args
    assert args == (str(tmpdir / f"{cassette_path}.yaml"),)
    assert cornell_proxy.application.config.cassette_paths == {root_path: {saved_path: f"{Path(cassette_path).name}.yaml"}}


def test_record_all_scenarios(cornell_proxy, temp_yaml_file):
    cornell_proxy.application.config.record_once = False
    cornell_proxy.get('hi')
    cornell_proxy.application.config.vcr.use_cassette.assert_called_once_with(temp_yaml_file)
    cornell_proxy.get('hi')
    assert cornell_proxy.application.config.vcr.use_cassette.call_count == 2
    cornell_proxy.get('bye')
    assert cornell_proxy.application.config.vcr.use_cassette.call_count == 3


def test_play_missing_cassette(cornell_proxy):
    cornell_proxy.application.config.record = False
    res = cornell_proxy.get('hi')
    assert res.status_code == NotFound.code
    cornell_proxy.application.config.vcr.use_cassette.assert_not_called()


def test_play_cassette_exists(cornell_proxy, temp_yaml_file):
    cornell_proxy.application.config.record = False
    cornell_proxy.application.config.cassette_paths = {"root": {'/hi': temp_yaml_file}}
    cornell_proxy.get('hi')
    cornell_proxy.application.config.vcr.use_cassette.assert_called_once_with(temp_yaml_file, record_mode='new_episodes')
