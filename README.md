# WebTricount

This project provides a web frontend for Tricount that only supports iOS and Android applications.

## Getting started

To install the project, you will need [Python](https://www.python.org/) and [uv](https://docs.astral.sh/uv/).

Run the project (this will automatically install the dependencies):

```shell
uv run manage.py runserver
```

## Deploy on a server

To deploy this project on a remote location, you should use `production_settings.py` settings file.
This is done automatically if you are running an ASGI server.
Then, expose the following environment variables:
- `SECRET_KEY`: a secret key used by Django to manage the sessions (you can generate one by running `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `HOST`: the domain hosting your website
