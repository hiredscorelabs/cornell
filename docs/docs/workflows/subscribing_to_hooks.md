---
sidebar_position: 4
sidebar_label: Subscribing to Hooks
title: Subscribing to Hooks
---

During runtime, Cornell triggers [blinker signals](https://pythonhosted.org/blinker/) that 
will allow you to modify or extend some of the out-of-the-box functionality. At this point,
 the following is available:
 * Replacing default logging service
 * Modifying the listed cassette path (for example, if you prefer not to save your cassettes locally)

The list of signals can be found in [cornell/signals.py](https://github.com/hiredscorelabs/cornell/blob/master/cornell/signals.py#L11)

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
In the above example:
 * We're replacing the default logging service with our own.
 * Every time Cornell requires a cassette file in runtime, we're downloading it from our dedicated storage.

**Note**: Additional signals can be easily added. Please feel free to open a [PR](https://github.com/hiredscorelabs/cornell) or an [Issue](https://github.com/hiredscorelabs/cornell/issues)!
