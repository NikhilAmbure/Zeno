from django.core.wsgi import get_wsgi_application
import os
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Zeno.settings')
django_application = get_wsgi_application()

def handler(event, context):
    if event.get('httpMethod', '') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': ''
        }

    environ = {
        'REQUEST_METHOD': event.get('httpMethod', ''),
        'SCRIPT_NAME': '',
        'PATH_INFO': event.get('path', ''),
        'QUERY_STRING': event.get('queryStringParameters', ''),
        'SERVER_NAME': 'vercel',
        'SERVER_PORT': '443',
        'HTTP_HOST': event.get('headers', {}).get('host', ''),
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(event.get('body', '').encode('utf-8')),
        'wsgi.errors': BytesIO(),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers
    for key, value in event.get('headers', {}).items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value

    response = {}
    def start_response(status, headers, exc_info=None):
        status_code = int(status.split(' ')[0])
        response['statusCode'] = status_code
        response['headers'] = dict(headers)

    response_body = b''
    for data in django_application(environ, start_response):
        response_body += data

    response['body'] = response_body.decode('utf-8')
    return response 