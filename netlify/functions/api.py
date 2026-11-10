import sys
import os

# Adiciona a raiz do projeto ao path para importar o app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app
from serverless_wsgi import handle_handler

def handler(event, context):
    return handle_handler(app, event, context)
