from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Zeno.settings')
app = get_wsgi_application()

def handler(request):
    """Handle incoming HTTP requests."""
    return app