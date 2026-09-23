"""Point d'entrée pour gunicorn (Railway).

Lancé avec :  gunicorn wsgi:app
Ne doit importer AUCUN module Tkinter (app.py, main.py, dashboard_frame.py...).
"""
from map_server_pkg import create_app

app = create_app()
