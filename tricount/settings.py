from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-fnf%xwmomp@$r!d1a+sjoce^q56&6i6tek3od=re$*i))m-t_2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "tricount_proxy",
]

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "tricount.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tricount.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True
USE_L10N = True

USE_THOUSAND_SEPARATOR = True

USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
]

LOCALE_PATHS = [BASE_DIR / "tricount_proxy/locale"]

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

TRICOUNT_API = "https://api.tricount.bunq.com"
TRICOUNT_USER_AGENT = "com.bunq.tricount.android:RELEASE:7.2.1:3260:ANDROID:9:C"
