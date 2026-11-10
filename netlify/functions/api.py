import serverless_wsgi
from app import app

# Adaptador que traduz requisições do Netlify para o Flask WSGI
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)