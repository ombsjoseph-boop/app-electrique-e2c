from flask import request, jsonify, session

try:
    from werkzeug.security import generate_password_hash, check_password_hash
except Exception:
    def generate_password_hash(p): return p
    def check_password_hash(h, p): return h == p

from db import get_conn
from datetime import datetime


def register_routes(app):
    @app.route('/api/register', methods=['POST'])
    def api_register():
        data = request.json or {}
        
        username = (data.get('username') or data.get('email') or '').strip()
        password = data.get('password') 
        email = data.get('email') 
        if not username or not password or not email:
            return jsonify({'error': 'insert username, password and email'}), 400
        conn = get_conn()
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=%s OR email=%s', (username, email))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'user_exists'}), 409
        try:
            hashed = generate_password_hash(password)
            c.execute('INSERT INTO users (username, password, email, created_at) VALUES (%s, %s, %s, %s)', (username, hashed, email, datetime.now().isoformat()))
            conn.commit()
            uid = c.lastrowid
        finally:
            try: c.close()
            except: pass
            try: conn.close()
            except: pass
        session['user_id'] = uid
        session['username'] = username
        session['email'] = email
        return jsonify({'id': uid, 'username': username, 'email': email}), 201
    

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.json or {}
        username = ( data.get('username') or data.get('email') or'').strip()
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'missing_fields'}), 400
        conn = get_conn()
        c = conn.cursor()
        c.execute('SELECT id, password, email FROM users WHERE username=%s OR email=%s', (username, username))
        row = c.fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'invalid_credentials'}), 401
        uid, hashed, email = row[0], row[1], row[2]
        try:
            pw_ok = check_password_hash(hashed, password)
        except Exception:
            pw_ok = (hashed == password)
        if not pw_ok:
            return jsonify({'error': 'invalid_credentials'}), 401
        session['user_id'] = uid
        session['username'] = username
        session['email'] = email
        return jsonify({'id': uid, 'username': username, 'email': email}), 200

    @app.route('/api/logout', methods=['POST'])
    def api_logout():
        session.pop('user_id', None)
        session.pop('username', None)
        return '', 204

    @app.route('/api/session', methods=['GET'])
    def api_session():
        user_id = session.get('user_id')
        username = session.get('username')
        email = session.get('email')
        
        if user_id:
            return jsonify({
                'user_id': user_id,
                'username': username,
                'email': email,
                'authenticated': True
            }), 200
        
        return jsonify({
            'authenticated': False,
            'user_id': None,
            'username': None,
            'email': None
        }), 200


from flask import request, jsonify

def register_routes_info(app):


    @app.route('/api/contact', methods=['POST'])
    def api_contact():

        if not request.is_json:
            return jsonify({'error': 'Requête invalide (JSON attendu)'}), 415

        data = request.get_json(force=True)

        nom = data.get('nom')
        email = data.get('email')
        num_tel = data.get('numero')
        message = data.get('message')

        if not nom or not email or not num_tel or not message:
            return jsonify({'error': 'Veuillez remplir tous les champs'}), 400

        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "INSERT INTO info (nom, email, numero, message) VALUES (%s,%s,%s,%s)",
                (nom, email, num_tel, message)
            )
            conn.commit()
        except Exception as e:
            print("ERREUR SQL :", e)
            return jsonify({'error': 'Erreur base de données'}), 500
        finally:
            c.close()
            conn.close()

        return jsonify({'success': True})







# def register_routes_info(app):
#     @app.route('/api/registers', methods=['POST'])
#     def api_registers():
#         data = request.json or {}
#         nom =  data.get('nom') or ''
#         email = data.get('email') or None
#         num_tel = data.get('num_tel') or None
#         message = data.get('message') or None
#         if not nom or not email or not num_tel or not message:
#             return jsonify({'error': 'remplicer les champs'}), 400
#         conn = get_conn()
#         c = conn.cursor()
#         try:
#             c.execute('INSERT INTO info (nom, email, num_tel,message) VALUES (%s,%s,%s,%s)', (nom, email, num_tel,message))
#             conn.commit()
#             uid = c.lastrowid
#         finally:
#             try: c.close()
#             except: pass
          
          
            
#def api_registers():
        # data = request.json or {}
        # nom =  data.get('nom') or ''
        # email = data.get('email') or None
        # num_tel = data.get('num_tel') or None
        # message = data.get('message') or None
        # password = data.get('password')
        # name = data.get('name') or None
        # if not nom or not password or not email or not num_tel or not message:
        #     return jsonify({'error': 'remplicer les champs'}), 400
        # conn = get_conn()
        # c = conn.cursor()
        # c.execute('SELECT id FROM users WHERE nom=%s', (nom,))
        # if c.fetchone():
        #     conn.close()
        #     return jsonify({'error': 'user_exists'}), 409
        # try:
            
        #     c.execute('INSERT INTO info (nom, email, num_tel,message) VALUES (%s,%s,%s,%s)', (nom, email, num_tel,message))
        #     conn.commit()
        #     uid = c.lastrowid
        # finally:
        #     try: c.close()
        #     except: pass
        #     try: conn.close()
        #     except: pass
        # session['id'] = uid
        # session['nom'] = nom
        # return jsonify({'id': uid, 'nom': nom}), 201