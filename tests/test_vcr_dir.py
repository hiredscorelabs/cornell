NESTED_URL = '/parent/hi'


def test_dir_from_path(cornell_proxy):
    cornell_proxy.application.config.fixed_path = False
    res = cornell_proxy.get(NESTED_URL)
    assert res.status_code == 200
    assert res.get_data().decode() == 'hi'
    assert cornell_proxy.application.config.cassette_paths == {"parent": {'/hi': 'hi.yaml'}}


def test_fixed_vcr_path(cornell_proxy):
    res = cornell_proxy.get(NESTED_URL)
    assert res.status_code == 200
    assert res.get_data().decode() == "parent/hi"
    assert cornell_proxy.application.config.cassette_paths == {"root": {NESTED_URL: 'parent_hi.yaml'}}
