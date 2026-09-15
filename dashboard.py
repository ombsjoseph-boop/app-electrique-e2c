"""
Tableau de bord HTML (Flask) avec Bootstrap 5
Accède à la même base de données MySQL que l'application Tkinter
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
# repli optionnel vers bcrypt pour les hash de style $2*
try:
    import bcrypt
except Exception:
    bcrypt = None
import mysql.connector
import os
from flask_socketio import SocketIO
import logging

logger = logging.getLogger(__name__)

DB_CONFIG_APP_DATA = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'app_data'  # Pour le tableau de bord web
}

DB_CONFIG_APP = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'app'  # Pour l'application principale
}

FACES_DIR = os.path.join(os.getcwd(), 'faces')

app = Flask(__name__, static_folder='faces', static_url_path='/faces')
app.config['SECRET_KEY'] = 'secret_key_for_sessions'
socketio = SocketIO(app)


@socketio.on('connect')
def handle_connect(sid):
    emit_dashboard_update()


@app.before_request
def require_dashboard_auth():
    """Protéger les pages du tableau de bord et les API administratives par une connexion stockée dans `admin_dsh` (base de données `app`)."""
    path = request.path
    # Autoriser les assets et les endpoints publics
    if path.startswith('/static') or path.startswith('/faces') or path.startswith('/public'):
        return
    # Autoriser les endpoints de connexion/déconnexion
    if path in ('/login', '/logout'):
        return
    # Protéger les pages du tableau de bord ainsi que les API d'administration et les routes '/admin'
    protect_ui = path == '/' or path.startswith('/dashboard') or path.startswith('/admin')
    protect_api = path.startswith('/api/db') or path == '/api/refresh' or path.startswith('/api/users') or path.startswith('/api/items' or path.startswith('/api/info'))
    if protect_ui or protect_api:
        if not session.get('admin_logged_in'):
            if path.startswith('/api/'):
                return jsonify({'error': 'unauthorized'}), 401
            return redirect(url_for('login', next=path))


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next') or '/'
    if request.method == 'GET':
        return render_template('login.html', next=next_url)

    username = (request.form.get('username') or '').strip()
    password = request.form.get('password') or ''
    if not username or not password:
        flash('Nom d\'utilisateur et mot de passe requis', 'danger')
        return render_template('login.html', next=next_url)

    # Tenter d'abord la connexion et fournir des erreurs exploitables
    try:
        conn = get_conn('app')
    except mysql.connector.Error as e:
        logger.exception('DB connection error during login: %s', e)
        msg = getattr(e, 'msg', None) or str(e)
        flash(f"Impossible de se connecter à la base de données 'app': {msg}", 'danger')
        return render_template('login.html', next=next_url)

    try:
        c = conn.cursor()
        # Détecter la colonne nom d'utilisateur dans admin_dsh (supporte 'username' ou 'nom')
        cols = []
        try:
            c.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s", ('app', 'admin_dsh'))
            cols = [r[0].lower() for r in c.fetchall()]
        except mysql.connector.Error:
            try:
                c.execute("SHOW COLUMNS FROM admin_dsh")
                cols = [r[0].lower() for r in c.fetchall()]
            except Exception:
                cols = []

        user_col = None
        for candidate in ('username', 'nom', 'name', 'user'):
            if candidate in cols:
                user_col = candidate
                break
        if not user_col:
            for col in cols:
                if col not in ('id', 'password'):
                    user_col = col
                    break
        if not user_col:
            flash("Impossible : table 'admin_dsh' ne contient pas de colonne nom d'utilisateur", 'danger')
            try: c.close()
            except: pass
            try: conn.close()
            except: pass
            return render_template('login.html', next=next_url)

        q = f"SELECT password FROM admin_dsh WHERE `{user_col}` = %s LIMIT 1"
        c.execute(q, (username,))
        row = c.fetchone()
    except mysql.connector.Error as e:
        logger.exception('DB query error during login: %s', e)
        msg = getattr(e, 'msg', None) or str(e)
        flash(f"Erreur lors de la lecture des comptes administrateurs : {msg}", 'danger')
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return render_template('login.html', next=next_url)

    if not row:
        flash('Utilisateur inconnu', 'danger')
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return render_template('login.html', next=next_url)

    stored = row[0]

    # normaliser la valeur stockée (bytes -> str) et supprimer les espaces
    try:
        if isinstance(stored, (bytes, bytearray)):
            stored_str = stored.decode('utf-8', errors='ignore').strip()
        else:
            stored_str = str(stored).strip()
    except Exception:
        stored_str = str(stored)

    def _seems_hashed(s):
        if not s: return False
        s = str(s)
        return s.startswith('pbkdf2:') or s.startswith('argon2:') or s.startswith('$2') or s.startswith('sha256$')

    is_plain_guess = False
    ok = False

    # Journal de débogage pour aider à diagnostiquer un mismatch de hash (sans exposer le hash complet)
    try:
        logger.debug("Login attempt: user=%s column=%s stored_prefix=%s len=%d", username, user_col, stored_str[:10], len(stored_str))
    except Exception:
        pass

    # Vérification principale utilisant werkzeug
    try:
        ok = check_password_hash(stored_str, password)
    except Exception as e:
        logger.exception('check_password_hash raised an exception: %s', e)
        ok = False
        # Repli : si bcrypt est disponible et que le hash ressemble à bcrypt ($2...), tenter bcrypt
        if bcrypt and stored_str.startswith('$2'):
            try:
                ok = bcrypt.checkpw(password.encode('utf-8'), stored_str.encode('utf-8'))
            except Exception as e2:
                logger.exception('bcrypt.checkpw failed: %s', e2)
                ok = False

    # repli vers comparaison en clair uniquement en cas de correspondance exacte
    if not ok and stored_str == password:
        ok = True
        is_plain_guess = True

    if not ok:
        # fournir des diagnostics plus clairs pour aider à corriger les erreurs courantes
        prefix = (stored_str[:10] + '...') if stored_str else '<empty>'
        # Problème courant : le champ 'password' contient accidentellement le nom d'utilisateur
        if stored_str == username:
            flash("Erreur d\'installation : la colonne 'password' contient le nom d'utilisateur. Réinitialisez le mot de passe via 'Gérer comptes admin'.", 'danger')
        elif not _seems_hashed(stored_str):
            flash(f"Mot de passe incorrect. Le mot de passe en base ne semble pas être un hash reconnu (ex: '{prefix}'). Utilisez 'Gérer comptes admin' pour remplacer le mot de passe par un hash.", 'danger')
        else:
            flash(f"Mot de passe incorrect (format du hash stocké: {prefix}). Vérifiez que le hash est compatible (Werkzeug, bcrypt, argon2).", 'danger')
        logger.warning("Failed login for %s: stored_prefix=%s len=%d", username, prefix, len(stored_str))
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return render_template('login.html', next=next_url)

    # Avertir si le mot de passe stocké semble être en clair
    if is_plain_guess or (not _seems_hashed(stored_str) and stored_str == password):
        flash('Attention : mot de passe stocké en clair ; pensez à le hacher', 'warning')
    # Succès
    session['admin_logged_in'] = True
    session['admin_user'] = username
    try:
        c.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass
    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    return redirect(url_for('login'))


@app.route('/admin/set_password', methods=['GET', 'POST'])
def admin_set_password():
    """Simple admin UI to set/hash password for an admin account in `admin_dsh` (db `app`)."""
    if request.method == 'GET':
        return render_template('admin_set_password.html')

    username = (request.form.get('username') or '').strip()
    password = request.form.get('password') or ''
    create_if_missing = (request.form.get('create') == 'on')
    if not username or not password:
        flash('Nom d\'utilisateur et mot de passe requis', 'danger')
        return render_template('admin_set_password.html')

    try:
        conn = get_conn('app')
        c = conn.cursor()
    except mysql.connector.Error as e:
        logger.exception('DB connection error in admin_set_password: %s', e)
        flash(f"Impossible de se connecter à la base 'app': {e}" , 'danger')
        return render_template('admin_set_password.html')

    try:
        # détecter la colonne nom d'utilisateur
        cols = []
        try:
            c.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s", ('app', 'admin_dsh'))
            cols = [r[0].lower() for r in c.fetchall()]
        except Exception:
            try: c.execute("SHOW COLUMNS FROM admin_dsh"); cols = [r[0].lower() for r in c.fetchall()]
            except Exception:
                cols = []
        user_col = None
        for candidate in ('username', 'nom', 'name', 'user'):
            if candidate in cols:
                user_col = candidate
                break
        if not user_col:
            for col in cols:
                if col not in ('id', 'password'):
                    user_col = col
                    break
        if not user_col:
            flash("Impossible : table 'admin_dsh' ne contient pas de colonne nom d'utilisateur", 'danger')
            return render_template('admin_set_password.html')

        # vérifier l'existence
        c.execute(f"SELECT 1 FROM admin_dsh WHERE `{user_col}` = %s LIMIT 1", (username,))
        exists = c.fetchone() is not None
        hashed = generate_password_hash(password)
        if exists:
            c.execute(f"UPDATE admin_dsh SET password = %s WHERE `{user_col}` = %s", (hashed, username))
            conn.commit()
            flash('Mot de passe mis à jour (hashé)', 'success')
        else:
            if not create_if_missing:
                flash('Utilisateur introuvable — cochez "Créer si manquant" pour l\'ajouter', 'warning')
                return render_template('admin_set_password.html')
            # insérer
            c.execute(f"INSERT INTO admin_dsh (`{user_col}`, password) VALUES (%s, %s)", (username, hashed))
            conn.commit()
            flash('Compte admin créé avec mot de passe haché', 'success')
    except mysql.connector.Error as e:
        logger.exception('DB error in admin_set_password: %s', e)
        flash(f"Erreur base de données : {e}", 'danger')
    finally:
        try: c.close()
        except: pass
        try: conn.close()
        except: pass
    return render_template('admin_set_password.html')


def get_conn(db='app_data'):
    if db == 'app_data':
        return mysql.connector.connect(**DB_CONFIG_APP_DATA)
    elif db == 'app':
        return mysql.connector.connect(**DB_CONFIG_APP)
    else:
        raise ValueError("Invalid database")


def get_users_from_db(db):
    try:
        conn = get_conn(db)
        c = conn.cursor()
    except mysql.connector.Error as e:
        logger.warning("Cannot connect to database '%s': %s", db, e)
        return []

    try:
        if db == 'app_data':
            c.execute('SELECT id, username, password, created_at, photo FROM users')
            users = []
            for r in c.fetchall():
                photo_url = (f'/faces/{r[4]}' if r[4] and
                             os.path.exists(os.path.join(FACES_DIR, r[4])) else None)
                users.append({
                    'id': f"{db}_{r[0]}",  # Préfixe pour éviter les conflits d'ID
                    'username': r[1],
                    'password': r[2],
                    'created_at': str(r[3]) if r[3] else None,
                    'photo': photo_url,
                    'source': db
                })
        elif db == 'app':
            c.execute('SELECT id, username, password FROM users')
            users = []
            for r in c.fetchall():
                users.append({
                    'id': f"{db}_{r[0]}",
                    'username': r[1],
                    'password': r[2],
                    'created_at': None,  # Pas de created_at dans 'app'
                    'photo': None,
                    'source': db
                })
    except mysql.connector.Error as e:
        logger.warning("Error while querying database '%s': %s", db, e)
        return []
    finally:
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return users


def get_items_from_db(db):
    try:
        conn = get_conn(db)
        c = conn.cursor()
    except mysql.connector.Error as e:
        logger.warning("Cannot connect to database '%s': %s", db, e)
        return []

    try:
        if db == 'app_data':
            c.execute('''SELECT i.id, i.user_id, i.title, i.description, i.created_at,
                                u.username, u.photo
                         FROM items i
                         JOIN users u ON i.user_id = u.id
                         ORDER BY i.created_at DESC''')
            items = []
            for r in c.fetchall():
                items.append({
                    'id': f"{db}_{r[0]}",
                    'user_id': f"{db}_{r[1]}",
                    'title': r[2],
                    'description': r[3],
                    'created_at': str(r[4]) if r[4] else None,
                    'username': r[5],
                    'user_photo': (f'/faces/{r[6]}' if r[6] and
                                   os.path.exists(os.path.join(FACES_DIR, r[6]))
                                   else None),
                    'source': db
                })
        elif db == 'app':
            c.execute('''SELECT i.id, i.user_id, i.title, i.description, i.created_at,
                                u.username
                         FROM items i
                         JOIN users u ON i.user_id = u.id
                         ORDER BY i.created_at DESC''')
            items = []
            for r in c.fetchall():
                items.append({
                    'id': f"{db}_{r[0]}",
                    'user_id': f"{db}_{r[1]}",
                    'title': r[2],
                    'description': r[3],
                    'created_at': str(r[4]) if r[4] else None,
                    'username': r[5],
                    'user_photo': None,
                    'source': db
                })
    except mysql.connector.Error as e:
        logger.warning("Error while querying database '%s': %s", db, e)
        return []
    finally:
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return items


# --- Aides à l'exploration de la base de données / APIs ---

def get_tables(db):
    """Retourne la liste des noms de tables dans la base de données fournie"""
    try:
        conn = get_conn(db)
        c = conn.cursor()
    except mysql.connector.Error as e:
        logger.warning("Cannot connect to database '%s': %s", db, e)
        return []
    try:
        c.execute('SHOW TABLES')
        rows = [r[0] for r in c.fetchall()]
        return rows
    except mysql.connector.Error as e:
        logger.warning("Error listing tables for db '%s': %s", db, e)
        return []
    finally:
        try: c.close()
        except: pass
        try: conn.close()
        except: pass


def get_primary_key(db, table):
    """Retourne le nom de la colonne clé primaire pour la table, ou None"""
    try:
        conn = get_conn(db)
        c = conn.cursor()
    except mysql.connector.Error as e:
        logger.warning("Cannot connect to database '%s' for pk lookup: %s", db, e)
        return None
    try:
        c.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_KEY='PRI' ORDER BY ORDINAL_POSITION", (db, table))
        r = c.fetchone()
        if r:
            return r[0]
        # repli vers le nom de la première colonne
        c.execute(f"SELECT * FROM `{table}` LIMIT 1")
        cols = [d[0] for d in c.description] if c.description else []
        return cols[0] if cols else None
    except mysql.connector.Error as e:
        logger.warning("Error finding primary key for %s.%s: %s", db, table, e)
        return None
    finally:
        try: c.close()
        except: pass
        try: conn.close()
        except: pass


@app.route('/api/db/<db>/tables')
def api_db_tables(db):
    if db not in ('app', 'app_data'):
        return jsonify({'error': 'invalid database'}), 400
    tables = get_tables(db)
    return jsonify(tables)


@app.route('/api/db/<db>/tables/<table>')
def api_db_table_rows(db, table):
    if db not in ('app', 'app_data'):
        return jsonify({'error': 'invalid database'}), 400
    tables = get_tables(db)
    if table not in tables:
        return jsonify({'error': 'unknown table'}), 404
    try:
        conn = get_conn(db)
        c = conn.cursor()
        c.execute(f"SELECT * FROM `{table}`")
        cols = [d[0] for d in c.description]
        rows = [dict(zip(cols, r)) for r in c.fetchall()]
    except mysql.connector.Error as e:
        logger.warning("Error fetching rows for %s.%s: %s", db, table, e)
        return jsonify({'error': str(e)}), 500
    finally:
        try: c.close()
        except: pass
        try: conn.close()
        except: pass
    return jsonify(rows)


@app.route('/api/db/<db>/tables/<table>/pk')
def api_db_table_pk(db, table):
    if db not in ('app', 'app_data'):
        return jsonify({'error': 'invalid database'}), 400
    pk = get_primary_key(db, table)
    if not pk:
        return jsonify({'error': 'no_primary_key'}), 404
    return jsonify({'pk': pk})


@app.route('/api/db/<db>/tables/<table>/row/<pk_value>', methods=['GET', 'PUT', 'DELETE'])
def api_db_row(db, table, pk_value):
    """GET : retourner une ligne ; PUT : mettre à jour la ligne avec le corps JSON ; DELETE : supprimer la ligne"""
    if db not in ('app', 'app_data'):
        return jsonify({'error': 'invalid database'}), 400
    tables = get_tables(db)
    if table not in tables:
        return jsonify({'error': 'unknown table'}), 404
    pk = get_primary_key(db, table)
    if not pk:
        return jsonify({'error': 'no_primary_key'}), 400

    try:
        conn = get_conn(db)
        c = conn.cursor()
    except mysql.connector.Error as e:
        logger.warning("DB connection error for %s.%s: %s", db, table, e)
        return jsonify({'error': 'db_connection'}), 500

    if request.method == 'GET':
        try:
            c.execute(f"SELECT * FROM `{table}` WHERE `{pk}` = %s", (pk_value,))
            cols = [d[0] for d in c.description]
            r = c.fetchone()
            if not r:
                return jsonify({'error': 'not_found'}), 404
            return jsonify(dict(zip(cols, r)))
        except mysql.connector.Error as e:
            logger.warning("Error fetching row %s from %s.%s: %s", pk_value, db, table, e)
            return jsonify({'error': str(e)}), 500
        finally:
            try: c.close()
            except: pass
            try: conn.close()
            except: pass

    if request.method == 'DELETE':
        # Prendre en charge une option de suppression en cascade explicite : ?cascade=true
        cascade = str(request.args.get('cascade', '')).lower() in ('1', 'true', 'yes')
        try:
            c.execute(f"DELETE FROM `{table}` WHERE `{pk}` = %s", (pk_value,))
            conn.commit()
            if getattr(c, 'rowcount', None) == 0:
                return jsonify({'error': 'not_found'}), 404
            return '', 204
        except mysql.connector.Error as e:
            # Gérer la contrainte de clé étrangère (impossible de supprimer le parent si des enfants existent)
            if getattr(e, 'errno', None) == 1451 or '1451' in str(e):
                # Trouver les contraintes/tables référentes et compter les lignes référencées
                refs = []
                try:
                    rc = conn.cursor()
                    rc.execute(
                        """SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME
                           FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                           WHERE REFERENCED_TABLE_SCHEMA=%s AND REFERENCED_TABLE_NAME=%s AND REFERENCED_COLUMN_NAME=%s""",
                        (db, table, pk)
                    )
                    for r in rc.fetchall():
                        constraint, ref_table, ref_col = r[0], r[1], r[2]
                        # tenter d'obtenir le compte des lignes référencées
                        count = None
                        try:
                            cc = conn.cursor()
                            cc.execute(f"SELECT COUNT(*) FROM `{ref_table}` WHERE `{ref_col}` = %s", (pk_value,))
                            cres = cc.fetchone()
                            count = int(cres[0]) if cres and cres[0] is not None else 0
                        except Exception:
                            count = None
                        finally:
                            try: cc.close()
                            except: pass
                        refs.append({'constraint': constraint, 'table': ref_table, 'column': ref_col, 'count': count})
                except Exception:
                    # Si nous n'avons pas pu lire information_schema, continuer avec une liste vide
                    pass
                finally:
                    try: rc.close()
                    except: pass

                if not cascade:
                    return jsonify({'error': 'foreign_key_violation', 'message': str(e), 'references': refs}), 409

                # Tenter la suppression en cascade à l'intérieur d'une transaction
                try:
                    conn.start_transaction()
                    # Supprimer les lignes référencées pour chaque FK trouvé
                    for ref in refs:
                        ref_table = ref['table']
                        ref_col = ref['column']
                        c2 = conn.cursor()
                        try:
                            c2.execute(f"DELETE FROM `{ref_table}` WHERE `{ref_col}` = %s", (pk_value,))
                        finally:
                            try: c2.close()
                            except: pass
                    # Maintenant supprimer la ligne parente
                    c.execute(f"DELETE FROM `{table}` WHERE `{pk}` = %s", (pk_value,))
                    if getattr(c, 'rowcount', None) == 0:
                        conn.rollback()
                        return jsonify({'error': 'not_found'}), 404
                    conn.commit()
                    return '', 204
                except mysql.connector.Error as e2:
                    conn.rollback()
                    logger.warning("Error during cascade delete for %s.%s: %s", db, table, e2)
                    return jsonify({'error': 'cascade_failed', 'message': str(e2)}), 500
            # Autres erreurs MySQL
            logger.warning("Error deleting row %s from %s.%s: %s", pk_value, db, table, e)
            return jsonify({'error': str(e)}), 500
        finally:
            try: c.close()
            except: pass
            try: conn.close()
            except: pass

    if request.method == 'PUT':
        data = request.json or {}
        # Retirer la clé primaire de la mise à jour si présente
        if pk in data:
            data.pop(pk)
        if not data:
            return jsonify({'error': 'no_fields'}), 400
        cols = list(data.keys())
        vals = [data[col] for col in cols]
        set_clause = ', '.join([f"`{c}` = %s" for c in cols])
        try:
            c.execute(f"UPDATE `{table}` SET {set_clause} WHERE `{pk}` = %s", tuple(vals) + (pk_value,))
            conn.commit()
            if getattr(c, 'rowcount', None) == 0:
                return jsonify({'error': 'not_found'}), 404
            return '', 204
        except mysql.connector.Error as e:
            logger.warning("Error updating row %s in %s.%s: %s", pk_value, db, table, e)
            return jsonify({'error': str(e)}), 500
        finally:
            try: c.close()
            except: pass
            try: conn.close()
            except: pass


@app.route('/dashboard/db')
def dashboard_db():
    """Page permettant d'explorer les bases `app` et `app_data`"""
    return render_template('db.html')


def emit_dashboard_update():
    """Émettre des mises à jour en temps réel à tous les clients connectés"""
    # Récupérer les données des deux bases
    users_app_data = get_users_from_db('app_data')
    users_app = get_users_from_db('app')
    users = users_app_data + users_app
    
    items_app_data = get_items_from_db('app_data')
    items_app = get_items_from_db('app')
    items = items_app_data + items_app
    
    # Calculer les totaux
    user_count = len(users)
    item_count = len(items)
    active_users = len(set(item['user_id'] for item in items))
    
    socketio.emit('dashboard_update', {
        'user_count': user_count,
        'item_count': item_count,
        'active_users': active_users,
        'users': users,
        'items': items
    })


@app.route('/api/refresh')
def api_refresh():
    """Déclencher une mise à jour en temps réel"""
    emit_dashboard_update()
    return jsonify({'status': 'updated'})


@app.route('/')
def index():
    """Page d'accueil du dashboard"""
    users_app_data = get_users_from_db('app_data')
    users_app = get_users_from_db('app')
    user_count = len(users_app_data) + len(users_app)
    
    items_app_data = get_items_from_db('app_data')
    items_app = get_items_from_db('app')
    item_count = len(items_app_data) + len(items_app)
    
    return render_template('index.html',
                           user_count=user_count, item_count=item_count)


@app.route('/api/users')
def api_users():
    """API: Récupérer tous les utilisateurs avec photos et mots de passe"""
    users_app_data = get_users_from_db('app_data')
    users_app = get_users_from_db('app')
    users = users_app_data + users_app
    return jsonify(users)


@app.route('/api/items')
def api_items():
    """API: Récupérer tous les items avec infos utilisateur"""
    items_app_data = get_items_from_db('app_data')
    items_app = get_items_from_db('app')
    items = items_app_data + items_app
    return jsonify(items)


@app.route('/api/user/<user_id>/items')
def api_user_items(user_id):
    """API: Récupérer les items d'un utilisateur"""
    if '_' in user_id:
        db, real_id = user_id.split('_', 1)
        real_id = int(real_id)
    else:
        db = 'app_data'  # par défaut
        real_id = int(user_id)

    try:
        conn = get_conn(db)
        c = conn.cursor()
        c.execute('''SELECT id, title, description, created_at FROM items
                     WHERE user_id=%s ORDER BY created_at DESC''', (real_id,))
        items = [{'id': f"{db}_{r[0]}", 'title': r[1], 'description': r[2],
                  'created_at': str(r[3]) if r[3] else None} for r in c.fetchall()]
    except mysql.connector.Error as e:
        logger.warning("Error while fetching items for user %s in db %s: %s", real_id, db, e)
        items = []
    finally:
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return jsonify(items)


@app.route('/dashboard/users')
def dashboard_users():
    """Page affichant la liste des utilisateurs"""
    return render_template('users.html')


@app.route('/dashboard/items')
def dashboard_items():
    """Page affichant la liste des items"""
    return render_template('items.html')


@app.route('/dashboard/analytics')
def dashboard_analytics():
    """Page avec statistiques et graphiques"""
    users_app_data = get_users_from_db('app_data')
    users_app = get_users_from_db('app')
    user_count = len(users_app_data) + len(users_app)
    
    items_app_data = get_items_from_db('app_data')
    items_app = get_items_from_db('app')
    item_count = len(items_app_data) + len(items_app)
    
    all_items = items_app_data + items_app
    active_users = len(set(item['user_id'] for item in all_items))
    
    return render_template('analytics.html',
                           user_count=user_count,
                           item_count=item_count,
                           active_users=active_users)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
