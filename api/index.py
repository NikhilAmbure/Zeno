# api/index.py

import os
from django.core.wsgi import get_wsgi_application
from wsgi_handler import handler

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Zeno.settings')

# Initialize Django WSGI application
application = get_wsgi_application()

# Export the handler function
app = handler

def handler(event, context):
    return application(event['body'], event['headers'])
