from .settings import *  # noqa: F403
from os import environ

SECRET_KEY = environ["SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = [environ["HOST"]]
