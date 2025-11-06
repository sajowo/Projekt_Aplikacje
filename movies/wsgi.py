import os

from django.core.wsgi import get_wsgi_application

# Zmień ścieżkę: "movies.movies.settings" na "movies.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings")

application = get_wsgi_application()
