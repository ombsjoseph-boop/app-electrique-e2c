from config import DB_CONFIG
import mysql.connector
import requests


def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()

    # Table existante pour les utilisateurs
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')

    # Table pour les agents
    c.execute('''
        CREATE TABLE IF NOT EXISTS agent (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table existante pour les items
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(255),
            description TEXT,
            created_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Table existante pour les points de carte
    c.execute('''
        CREATE TABLE IF NOT EXISTS map_points (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            latitude FLOAT,
            longitude FLOAT,
            created_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Nouvelle table pour les zones électriques
    c.execute('''
        CREATE TABLE IF NOT EXISTS electric_zones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(100),
            latitude FLOAT,
            longitude FLOAT,
            city VARCHAR(100),
            voltage VARCHAR(50),
            status VARCHAR(50),
            description TEXT,
            created_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(created_by) REFERENCES users(id)
        )
    ''')

    # Ensure bills table exists (used by desktop and web server)
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            user_nom VARCHAR(255),
            reference VARCHAR(255),
            amount DECIMAL(10,2) NOT NULL,
            due_date DATETIME,
            status VARCHAR(50) DEFAULT 'unpaid',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at DATETIME NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Ensure 'user_nom' column exists for compatibility with older installs
    try:
        c.execute("ALTER TABLE bills ADD COLUMN user_nom VARCHAR(255)")
    except Exception:
        pass

    # Add detailed billing columns if missing (subscription, consumption, breakdown and taxes)
    try:
        c.execute("ALTER TABLE bills ADD COLUMN subscription_fee DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN consumption_kwh DECIMAL(10,3) DEFAULT 0.000")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN unit_price DECIMAL(10,4) DEFAULT 0.0000")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN consumption_cost DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN fourniture_cost DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN acheminement_cost DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN tcfe_pct DECIMAL(5,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN tcfe_amount DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN cta_pct DECIMAL(5,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN cta_amount DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN tva_pct DECIMAL(5,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN tva_amount DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE bills ADD COLUMN total_amount DECIMAL(10,2) DEFAULT 0.00")
    except Exception:
        pass


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def notify_dashboard():
    """Notifier le tableau de bord pour actualiser les données"""
    try:
        requests.get('http://127.0.0.1:5000/api/refresh', timeout=1)
    except:
        pass  # Ignorer si le tableau de bord n'est pas en cours d'exécution


def save_bill(user_identifier, amount=None, due_date=None, reference=None, send_remote=True, user_nom=None, subscription_fee=0.0, consumption_kwh=0.0, unit_price=0.0, fourniture_cost=0.0, acheminement_cost=0.0, tcfe_pct=0.0, cta_pct=0.0, tva_pct=0.0):
    """Enregistrer une facture localement avec des champs détaillés.

    Nouveaux champs optionnels :
      - subscription_fee : frais fixes (float)
      - consumption_kwh : consommation en kWh (float)
      - unit_price : prix par kWh (float)
      - fourniture_cost : coût explicite d'approvisionnement (float)
      - acheminement_cost : coût explicite de réseau/transport (float)
      - tcfe_pct, cta_pct, tva_pct : pourcentages appliqués au sous-total

    Si amount est None, il sera calculé à partir des champs détaillés.
    Retourne l'id local de la facture (int).
    """
    from datetime import datetime as _dt
    # Calculer les coûts
    try:
        subscription_fee = float(subscription_fee or 0)
        consumption_kwh = float(consumption_kwh or 0)
        unit_price = float(unit_price or 0)
        fourniture_cost = float(fourniture_cost or 0)
        acheminement_cost = float(acheminement_cost or 0)
        tcfe_pct = float(tcfe_pct or 0)
        cta_pct = float(cta_pct or 0)
        tva_pct = float(tva_pct or 0)
    except Exception:
        # Repli sur zéro en cas d'entrées invalides
        subscription_fee = subscription_fee or 0.0
        consumption_kwh = consumption_kwh or 0.0
        unit_price = unit_price or 0.0
        fourniture_cost = fourniture_cost or 0.0
        acheminement_cost = acheminement_cost or 0.0
        tcfe_pct = tcfe_pct or 0.0
        cta_pct = cta_pct or 0.0
        tva_pct = tva_pct or 0.0

    consumption_cost = consumption_kwh * unit_price
    subtotal = subscription_fee + consumption_cost + fourniture_cost + acheminement_cost
    tcfe_amount = round(subtotal * (tcfe_pct / 100.0), 2)
    cta_amount = round(subtotal * (cta_pct / 100.0), 2)
    tva_amount = round(subtotal * (tva_pct / 100.0), 2)
    total_amount = round(subtotal + tcfe_amount + cta_amount + tva_amount, 2)

    if amount is None:
        amount = total_amount

    conn = get_conn()
    c = conn.cursor()
    uid = None
    try:
        if user_identifier:
            # Si numérique, traiter comme un id
            try:
                uid_candidate = int(user_identifier)
                c.execute('SELECT id FROM users WHERE id=%s', (uid_candidate,))
                r = c.fetchone()
                if r:
                    uid = r[0]
            except Exception:
                # Pas un entier -> traiter comme nom d'utilisateur
                c.execute('SELECT id FROM users WHERE username=%s', (user_identifier,))
                r = c.fetchone()
                if r:
                    uid = r[0]
                else:
                    # Créer un enregistrement utilisateur minimal pour satisfaire la FK. Insérer sans created_at
                    # pour compatibilité avec différents schémas.
                    c.execute('INSERT INTO users (username, password) VALUES (%s,%s)', (user_identifier, 'changeme'))
                    conn.commit()
                    uid = c.lastrowid
        # Insérer la facture localement (stocker user_nom si disponible) avec les champs détaillés
        ref = reference or f'BILL-{int(_dt.now().timestamp())}'
        c.execute('''INSERT INTO bills (user_id, user_nom, reference, amount, due_date, status, created_at,
            subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
            tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ''', (uid, (user_identifier if isinstance(user_identifier, str) else None), ref, amount, due_date, 'unpaid', _dt.now(),
              subscription_fee, consumption_kwh, unit_price, consumption_cost, fourniture_cost, acheminement_cost,
              tcfe_pct, tcfe_amount, cta_pct, cta_amount, tva_pct, tva_amount, total_amount))
        conn.commit()
        bill_id = c.lastrowid
    finally:
        try:
            c.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    # Tenter d'envoyer au serveur de carte distant (meilleur-effort)
    if send_remote:
        try:
            import requests as _requests
            # Préférer envoyer 'username' et 'user_nom' si disponibles pour que le serveur puisse créer/résoudre l'utilisateur
            payload = {
                'user': user_identifier if user_identifier else uid,
                'amount': amount,
                'subscription_fee': subscription_fee,
                'consumption_kwh': consumption_kwh,
                'unit_price': unit_price,
                'consumption_cost': consumption_cost,
                'fourniture_cost': fourniture_cost,
                'acheminement_cost': acheminement_cost,
                'tcfe_pct': tcfe_pct,
                'tcfe_amount': tcfe_amount,
                'cta_pct': cta_pct,
                'cta_amount': cta_amount,
                'tva_pct': tva_pct,
                'tva_amount': tva_amount,
                'total_amount': total_amount
            }
            if user_nom:
                payload['user_nom'] = user_nom
            elif isinstance(user_identifier, str):
                payload['user_nom'] = user_identifier
            if due_date:
                payload['due_date'] = due_date
            if reference:
                payload['reference'] = reference
            _requests.post('http://127.0.0.1:5001/api/bills/create', json=payload, timeout=5)
        except Exception:
            pass

    return bill_id