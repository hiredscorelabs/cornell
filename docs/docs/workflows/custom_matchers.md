---
sidebar_position: 2
sidebar_label: Adding Custom Matchers
title: Adding Custom Matchers
---

In some cases you'd want to add [custom request macthers](https://vcrpy.readthedocs.io/en/latest/advanced.html#register-your-own-request-matcher) to Cornell.
This can be easily done using the wrapper we created in the above example, with the `additional_vcr_matchers` param:

```python
#!/usr/bin/env python

import click
import json
from vcr.util import read_body
from cornell.cornell_server import CornellCmdOptions, start_cornell
from cornell.cornell_helpers import json_in_headers
from cornell.custom_matchers import requests_match_conditions


# Custom Matcher
@requests_match_conditions(json_in_headers, lambda request: request.body)
def vcr_json_custom_body_matcher(received_request, cassette_request):
    received_request_dict = json.loads(read_body(received_request))
    cassette_request_dict = json.loads(read_body(cassette_request))
    if received_request_dict == cassette_request_dict or "special_params" not in received_request_dict:
        return True
    return is_specially_matched(received_request_dict, cassette_request_dict)


@click.command(cls=CornellCmdOptions)
def start_mock_service(**kwargs):
    start_cornell(additional_vcr_matchers=[vcr_json_custom_body_matcher], **kwargs)


if __name__ == "__main__":
    start_mock_service()
```

In this example, we've added `vcr_json_custom_body_matcher` as an `additional_vcr_matchers`.
Notice that Cornell also provides the `requests_match_conditions` decorator, in case you'd want to activate your matcher only under specific circumstances.

**Note**: If you're adding a custom matcher that actually implements standard protocols that can be widely used, kindly consider adding it as PR to Cornell.
 Your contribution will be really appreciated! 

### Subscribing to Hooks

During runtime, Cornell triggers [blinker signals](https://pythonhosted.org/blinker/) that 
will allow you to modify or extend some of the out-of-the-box functionality, at this point,
 the following is available:
 * Replacing default logging service
 * Modifying the listed cassette path (for example, if you prefer not to save your cassettes locally)

List of signal can be found in [cornell/signals.py](https://github.com/hiredscorelabs/cornell/blob/master/cornell/signals.py)

Example:
```python
from cornell.signals import logging_setup, process_cassette_file

@logging_setup.connect
def setup_logging_service(_):
    return logging_service


@process_cassette_file.connect
def download_cassette_file(cassette_file_path):
    storage = CornellCassettesStorage(logging_service)
    return storage.download(cassette_file_path)


@click.command(cls=CornellCmdOptions)
def start_mock_service(**kwargs):
    start_cornell(**kwargs)


if __name__ == "__main__":
    start_mock_service()

```
In the above example, we're replacing the default logging service with our own and in addition, every time Cornell requires a cassette file in runtime, we're downloading it from our dedicated storage.

**Note**: Additional signals can be easily added, please feel free to open a PR or an Issue!
