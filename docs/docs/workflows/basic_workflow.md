---
sidebar_position: 1
sidebar_label: Basic Workflow
title: Basic Workflow
---

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

    In case the `index.yaml` was already present, it will be updated with new interactions, otherwise new file will be created.

__Note__

    Cornell doesn't record interactions with an erroneous response, by default (i.e response with 404, will omitted). If you wish to enable this option, run cornell with --record-errors flag

In this specific example, we can see that the 2 requests are mapped to the saved cassettes:

![Index file](https://imgur.com/IYjiJx6.gif)
