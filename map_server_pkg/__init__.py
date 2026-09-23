import threading
import os
import json
from flask import Flask, render_template, render_template_string
from db import get_conn, init_db
from datetime import datetime
from . import templates
from . import helpers
from .routes_markers import register_routes as register_routes_markers
from .routes_bills import register_routes as register_routes_bills
from .routes_news import register_routes as register_routes_news
from .routes_auth import register_routes as register_routes_auth
from .routes_auth import register_routes_info as register_routes_infos

MAP_SERVER = None
MAP_SERVER_THREAD = None
MAP_SERVER_PORT = 5001


# Dossier racine du projet (là où se trouvent db.py, webapps/, etc.)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    """Construit l'application Flask SANS la lancer.

    - En production (Railway) : gunicorn l'utilise via wsgi.py
    - En local (Tkinter)      : start_map_server() la lance dans un thread
    """
    global MAP_SERVER
    # Vérifier que les tables de la BD existent avant de démarrer le serveur
    try:
        init_db()
    except Exception:
        pass

    static_folder = os.path.join(BASE_DIR, 'webapps')
    # Utiliser le dossier `webapps` comme dossier de templates afin que Jinja traite
    # les `{% include %}` présents dans les pages HTML. Ne pas laisser Flask
    # gérer automatiquement les fichiers statiques au niveau racine (static_url_path='')
    # car cela peut empêcher le rendu Jinja pour '/'. Nous désactivons le static
    # automatique et ajoutons un gestionnaire manuel plus bas.
    app = Flask('map_server', template_folder=static_folder, static_folder=None, static_url_path=None)
    app.secret_key = os.environ.get('SECRET_KEY', 'secret_key_for_sessions')

    # En-têtes CORS simples
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

    @app.route('/')
    def index_root():
        # Rendre via l'environnement Jinja directement pour éviter des erreurs
        # potentielles liées au contexte de render_template dans certaines config.
        try:
            tpl = app.jinja_env.get_template('index.html')
            return tpl.render()
        except Exception:
            # Fallback à send_static_file si rendu échoue
            try:
                return app.send_static_file('index.html')
            except Exception:
                return 'Index not found', 404
            
    
    @app.route('/services')
    def services_page():
        # Rendre via l'environnement Jinja directement pour éviter des erreurs
        # potentielles liées au contexte de render_template dans certaines config.
        try:
            tpl = app.jinja_env.get_template('services.html')
            return tpl.render()
        except Exception:
            # Fallback à send_static_file si rendu échoue
            try:
                return app.send_static_file('services.html')
            except Exception:
                return 'Index not found', 404

    
    @app.route('/about')
    def about_page():
        try:
            tpl = app.jinja_env.get_template('about.html')
            return tpl.render()
        except Exception:
            try:
                return app.send_static_file('about.html')
            except Exception:
                return 'About not found', 404

    
    @app.route('/contact')
    def contact_page():
        try:
            tpl = app.jinja_env.get_template('contact.html')
            return tpl.render()
        except Exception:
            try:
                return app.send_static_file('contact.html')
            except Exception:
                return 'Contact not found', 404

   
    @app.route('/bills')
    def bills_page():
        try:
            tpl = app.jinja_env.get_template('bills.html')
            return tpl.render()
        except Exception:
            try:
                return app.send_static_file('bills.html')
            except Exception:
                return 'Bills not found', 404

    
    @app.route('/news')
    def news_page():
        try:
            tpl = app.jinja_env.get_template('news.html')
            return tpl.render()
        except Exception:
            try:
                return app.send_static_file('news.html')
            except Exception:
                return 'News not found', 404

    
    @app.route('/projects')
    def projects_page():
        try:
            tpl = app.jinja_env.get_template('projects.html')
            return tpl.render()
        except Exception:
            try:
                return app.send_static_file('projects.html')
            except Exception:
                return 'Projects not found', 404

    # Le route de la page carte utilise des templates
    @app.route('/map')
    def map_page():
        from flask import request
        user_id = request.args.get('user_id', '')
        api_key = helpers.get_google_api_key()
        template = templates.GOOGLE_MAP_HTML if api_key else templates.LEAFLET_MAP_HTML
        return render_template_string(template, api_key=api_key or '', user_id=user_id, server_port=MAP_SERVER_PORT)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    # Enregistrer les groupes de routes fonctionnelles
    register_routes_markers(app)
    register_routes_bills(app)
    register_routes_news(app)
    register_routes_auth(app)
    register_routes_infos(app)

    MAP_SERVER = app

    # Créer la vue 'factures' pour compatibilité
    try:
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute("CREATE OR REPLACE VIEW factures AS SELECT * FROM bills")
            conn.commit()
        except Exception:
            try:
                c.execute("DROP VIEW IF EXISTS factures")
                c.execute("CREATE VIEW factures AS SELECT * FROM bills")
                conn.commit()
            except Exception:
                pass
        try: c.close()
        except: pass
        try: conn.close()
        except: pass
    except Exception:
        pass

    # Route générique pour servir les fichiers statiques depuis webapps si le fichier existe.
    # Ajoutée après l'enregistrement des routes fonctionnelles pour éviter d'écraser
    # les endpoints API/HTML définis ci-dessus.
    from flask import send_from_directory, abort

    @app.route('/<path:filename>')
    def _serve_static(filename):
        full = os.path.join(static_folder, filename)
        if os.path.isfile(full):
            # Si c'est un fichier HTML, le rendre via Jinja pour traiter les includes
            if filename.endswith('.html'):
                try:
                    tpl = app.jinja_env.get_template(filename)
                    return tpl.render()
                except Exception:
                    # Fallback : servir le fichier statique brut si Jinja échoue
                    return send_from_directory(static_folder, filename)
            else:
                # Pour les autres fichiers (CSS, JS, images), servir statiquement
                return send_from_directory(static_folder, filename)
        return abort(404)

    return app


def start_map_server(port: int = None):
    """Démarrer le serveur de carte en arrière-plan (usage local / Tkinter)."""
    global MAP_SERVER, MAP_SERVER_THREAD, MAP_SERVER_PORT
    if MAP_SERVER is not None:
        return MAP_SERVER
    if port is not None:
        try:
            MAP_SERVER_PORT = int(port)
        except Exception:
            pass

    app = create_app()

    def run_app():
        try:
            app.run(host='127.0.0.1', port=MAP_SERVER_PORT, debug=False, use_reloader=False)
        except Exception:
            pass

    t = threading.Thread(target=run_app, daemon=True)
    t.start()
    MAP_SERVER_THREAD = t

    return app
