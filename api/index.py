# api/index.py

from Zeno.wsgi import application  # Adjust path to your actual wsgi.py
from django.core.wsgi import get_wsgi_application
from io import BytesIO
import sys

# Initialize WSGI application
app = application

def handler(event, context):
    environ = {
        "REQUEST_METHOD": event.get("method", "GET"),
        "PATH_INFO": event.get("path", "/"),
        "QUERY_STRING": event.get("query", ""),
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8000",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": BytesIO(event.get("body", "").encode("utf-8")),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": True,
    }

    headers_set = []
    body = BytesIO()

    def start_response(status, headers, exc_info=None):
        headers_set[:] = [status, headers]
        return body.write

    result = app(environ, start_response)
    for data in result:
        if data:
            body.write(data)

    body.seek(0)
    status_code = int(headers_set[0].split()[0])

    return {
        "statusCode": status_code,
        "headers": dict(headers_set[1]),
        "body": body.read().decode("utf-8"),
    }
