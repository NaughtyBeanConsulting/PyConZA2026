"""
WSGI config — the production entry point (gunicorn app.wsgi).

Defaults to production settings; .env or the environment can override
DJANGO_SETTINGS_MODULE.
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.production")

application = get_wsgi_application()
