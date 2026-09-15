import os
import json
import requests


def notify_dashboard():
    """Notify the dashboard to refresh data"""
    try:
        requests.get('http://127.0.0.1:5000/api/refresh', timeout=1)
    except:
        pass


def get_google_api_key():
    cfg_file = os.path.join(os.getcwd(), 'config.json')
    try:
        if os.path.exists(cfg_file):
            with open(cfg_file, 'r', encoding='utf-8') as cf:
                cfg = json.load(cf)
                return cfg.get('google_api_key')
    except Exception:
        return None
    return None
