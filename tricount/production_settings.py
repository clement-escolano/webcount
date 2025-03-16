from .settings import *  # noqa: F403
from os import environ

SECRET_KEY = environ["SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = [environ["HOST"]]

# Verbose logs for errors
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
