# map_server_pkg

Structure du package créé à partir de `map_server.py` :

- `__init__.py` : point d'entrée, contient `start_map_server()` et démarre le serveur Flask en thread.
- `templates.py` : templates HTML pour Google Maps et Leaflet.
- `helpers.py` : fonctions utilitaires (ex. `notify_dashboard`, `get_google_api_key`).
- `routes_markers.py` : routes `/api/markers`, `/api/map_points`, `/api/electric_zones`.
- `routes_bills.py` : routes liées aux factures (`/api/bills` etc.).
- `routes_news.py` : routes `/api/news`.
- `routes_auth.py` : routes d'authentification (`/api/register`, `/api/login`, `/api/logout`, `/api/session`).

Démarrage rapide :

```python
from map_server_pkg import start_map_server
app = start_map_server()
```

Notes :
- Le paquet assume l'existence d'une base de données compatible et des tables attendues (`items`, `bills`, etc.).
- Les routes conservent la logique originale ; des ajustements peuvent être nécessaires si votre schéma DB a changé.
