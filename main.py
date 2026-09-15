#  app.py est le point d'entrer et contient ensemble des ongles et options

import requests
from app import App
from database import init_db

# Fonctions utilitaires pour envoyer des données au serveur web (appelées par l'application de bureau)
SERVER_BASE = 'http://127.0.0.1:5001'


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
    # Démarrer le serveur de carte afin que l'application de bureau puisse appeler les endpoints /api/...
    try:
        from map_server import start_map_server
        start_map_server()
    except Exception:
        # Si le serveur de carte ne peut pas être démarré ici (par ex. port déjà utilisé), il peut
        # tourner séparément ; continuer pour permettre le démarrage de l'application de bureau.
        pass

    app = App()
    app.mainloop()
