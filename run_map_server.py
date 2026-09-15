"""Petit utilitaire pour lancer le serveur de carte localement.

Exécute : python run_map_server.py
Puis ouvrez http://127.0.0.1:5001/
"""
from map_server import start_map_server
import time

if __name__ == '__main__':
    start_map_server()
    print('Map server démarré sur http://127.0.0.1:5001')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print('Arrêt demandé')
