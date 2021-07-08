---
sidebar_position: 3
sidebar_label: Starting Cornell from your own module
title: Starting Cornell from your own module
---

In order to extend Cornell with additional matchers, or register to its hooks,
 you first will need to start the cornell service from your own internal module.
 This can be easily done by inheriting `CornellCmdOptions` [click](https://click.palletsprojects.com/en/8.0.x/) from `cornell.cornell_server`
 
 For example: 
 In a separate module (i.e. `cornell_wrapper.py`), create the following:
 
```python
#!/usr/bin/env python

import click
from pathlib import Path
from cornell.cornell_server import CornellCmdOptions, start_cornell

@click.command(cls=CornellCmdOptions)
@click.option('--hello', default=False, is_flag=True, help="Say hello")
def start_mock_service(hello, **kwargs):
    cassettes_dir = Path(__file__).absolute().parent/"mock_service"
    if hello:
        print("Hello from Cornell :)")
        return
    start_cornell(cassettes_dir=cassettes_dir, **kwargs)


if __name__ == "__main__":
    start_mock_service()
```
In this example, we modified the following:

* Set a default `cassettes_dir`, so when the wrapper is executed it will be used instead of a default one
* Added another command argument, to extend possible functionality

Running:

 ` ./tasks_worker/tests/cornell_wrapper.py --hello`

 will result in:

 `Hello from Cornell :)`

Running the same command without arguments, will start Cornell, with with a default cassettes_dir.
