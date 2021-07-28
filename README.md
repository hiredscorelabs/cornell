# Cornell: record & replay mock server

[![Build Status](https://travis-ci.com/hiredscorelabs/cornell.svg?branch=master)](https://travis-ci.com/hiredscorelabs/cornell)
[![Python Version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue)](https://www.python.org/downloads/release/python-390/)


<p align="center">
  <img src="https://imgur.com/ShxP4AI.png" alt="Cornell Logo">
</p>


> Cornell makes it dead simple, via its record and replay features to perform end-to-end testing in a fast and isolated testing environment.

When your application integrates with multiple web-based services, end-to-end testing is crucial before deploying to production.
Mocking is often a tedious task. It becomes even more tiresome when working with multiple APIs from multiple vendors.

[vcrpy](https://github.com/kevin1024/vcrpy) is an awesome library that records and replays HTTP interactions for unit tests. Its output is saved to reusable "cassette" files.

By wrapping vcrpy with Flask, Cornell provides a lightweight record and replay server that can be easily used during distributed system testing and simulate all HTTP traffic needed for your tests.

## Basic Use Case

When you're working with distributed systems, the test client entry point triggers a cascade of events that eventually send HTTP requests to an external server

![System in test](https://imgur.com/OlDNTiD.jpg) 

With Cornell server started, it will act as a proxy (**record mode**) between the outgoing HTTP requests and the external server and will record all relevant interactions.
Once interactions are recorded, Cornell can work in replay mode, replacing the external server entirely, short-circuiting the calls and instead, replying back instantly with the previously recorded response.

![System in test](https://imgur.com/ZXTFgaP.jpg) 


## Installation 

To install from [PyPI](https://pypi.org/project/cornell/), all you need to do is this:

```bash 
  pip install cornell
```

## Usage

```bash
Usage: cornell_server.py [OPTIONS]

  Usage Examples: Record mode: `cornell --forward_uri="https://remote_server/api" --record -cd custom_cassette_dir`
  Replay mode: `cornell -cd custom_cassette_dir

Options:
  -p, --port INTEGER
  -ff, --forward_uri TEXT         Must be provided in case of recording mode
  -, --record-once / --record-all
                                  Record each scenario only once, ignore the
                                  rest

  -r, --record                    Start server in record mode
  -fp, --fixed-path               Fixed cassettes path. If enabled, Cornell
                                  will support only one server for recording

  -cd, --cassettes-dir TEXT       Cassettes parent directory, If not
                                  specified, Cornell parent dir will be used

  --help                          Show this message and exit.
```

## Demo - Full Example


Staring Cornell in record mode:

```
cornell -ff https://api.github.com/ --record -cd cassettes
```

This will start the server in record-proxy mode on port `9000`, and will forward all requests to `https://api.github.com/`

![Cornell demo](https://imgur.com/ky5NBPf.gif)

When cornell is in record mode, it will forward all request to the specified forwarding URL, for example:

```
requests.get("http://127.0.0.1:9000/github/repos/kevin1024/vcrpy/license").json()
```
or
```
requests.get("http://127.0.0.1:9000/github/repos/kevin1024/vcrpy/contents").json()
```

or you can browse to the URL using your browser

![Browser](https://imgur.com/GMgF6Cx.gif)

Cornell will forward the request to the specified URL and will record both the request and the response.


The yaml cassettes will be recorded to a dedicated directory (by default, `cassettes` in the root dir)

For example:

![Cassette dir](https://imgur.com/cZExEpu.gif)


__Note__

    By default, `cassettes` directory will be created in cornell's root dir and will contain the cassette by destination hierarchy.
    Use `-cd` to specify custom directory for your cassettes.
    Mind that `-cd <custom_dir> should match for both record and replay modes

Once all the necessary interactions were recorded, stop cornell server using *ctrl+c*.
Once stopped, all interactions will be mapped via an auto-generated `index.yaml` file.

__Note__

    In case the `index.yaml` is already present, it will be updated with new interactions. Otherwise, a new file will be created.

In this specific example, we can see that the 2 requests are mapped to the saved cassettes:

![Index file](https://imgur.com/IYjiJx6.gif)


## Features

### Request Matchers

In addition to the [vcrpy matchers](https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching), cornell provides the following custom request matchers:

- [OData](https://www.odata.org/getting-started/basic-tutorial/) request query matcher
- [SOAP](https://stoplight.io/api-types/soap-api/) request body matcher


### Environment Variables

Since Cornell is a testing server it's executed by default with `FLASK_ENV=local`.
You can modify this as described in [flask configuration](https://flask.palletsprojects.com/en/2.0.x/config/#configuration-handling)

### Advanced Features

Can be found in the [documentation](https://hiredscorelabs.github.io/cornell/docs/examples/)

## Contributing

Yes please! contributions are more than welcome!

Please follow [PEP8](https://www.python.org/dev/peps/pep-0008/) and the [Python Naming Conventions](https://pep8.org/#prescriptive-naming-conventions)

Add tests when you're adding new functionality and make sure all the existing tests are happy and green :)

To set up development environment:
```sh
  python -m venv venv
  source venv/bin/activate
  make configure
```


## Running Tests

To run tests, run the following command

```bash
  python -m venv venv
  source venv/bin/activate
  make test
```
