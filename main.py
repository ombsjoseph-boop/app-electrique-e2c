#  app.py est le point d'entrer et contient ensemble des ongles et options

import os
import requests
from dotenv import load_dotenv
load_dotenv()

from app import App
from database import init_db

# En local (pas de .env / API_URL) : http://127.0.0.1:5001 par défaut
# Sur le PC de l'admin en production : mettez API_URL=https://<url-admin>.up.railway.app dans le .env
SERVER_BASE = os.environ.get('API_URL', 'http://127.0.0.1:5001')


def send_marker(user_id, title, lat, lng, color='#ff0000'):
    payload = {
        'user_id': user_id,
        'title': title,
        'lat': lat,
        'lng': lng,
        'color': color
    }
    url = SERVER_BASE + '/api/markers'
    r = requests.post(url, json=payload, timeout=5)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":

    init_db()

    # Ne démarrer le serveur Flask local que si on travaille encore en local.
    # Si API_URL pointe vers Railway, le vrai serveur tourne déjà là-bas,
    # inutile (et source de confusion) d'en relancer un second sur le PC.
    if SERVER_BASE.startswith('http://127.0.0.1') or SERVER_BASE.startswith('http://localhost'):
        try:
            from map_server import start_map_server
            start_map_server()
        except Exception:
            pass

    app = App()
    app.mainloop()