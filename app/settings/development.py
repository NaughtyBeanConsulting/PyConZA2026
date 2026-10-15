"""Local development: DEBUG on, console email, a throwaway secret key if none is set."""

from .base import *  # noqa: F403
from .base import env, env_bool, env_list

DEBUG = env_bool("DEBUG", True)
SECRET_KEY = env("DJANGO_SECRET_KEY") or "django-insecure-development-only"
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
INTERNAL_IPS = ["127.0.0.1"]

# Serve straight from static/ and app dirs (no collectstatic) even when DEBUG is
# off, as it is under the test runner.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
