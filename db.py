import mysql.connector
import os
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'app'
}

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            image VARCHAR(255),
            created_at DATETIME,
            photo VARCHAR(255)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            title VARCHAR(255),
            description TEXT,
            created_at DATETIME,
            lat FLOAT,
            lng FLOAT,
            color VARCHAR(255),
            likes INT DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    # Veiller à ce que les installations existantes obtiennent une colonne 'likes' si elle manque
    try:
        c.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS likes INT DEFAULT 0")
    except Exception:
        # Les anciennes versions de MySQL peuvent ne pas supporter IF NOT EXISTS ; tenter une approche plus sûre
        try:
            c.execute("SHOW COLUMNS FROM items LIKE 'likes'")
            if not c.fetchone():
                c.execute("ALTER TABLE items ADD COLUMN likes INT DEFAULT 0")
        except Exception:
            pass
    conn.commit()
    conn.close()

    # Créer les tables 'news' et 'bills' pour les fonctionnalités du site électrique national
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                body TEXT,
                created_by INT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
        ''')
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
        # ajouter la colonne si manquante (compatibilité)
        try:
            c.execute("ALTER TABLE bills ADD COLUMN user_nom VARCHAR(255)")
        except Exception:
            pass
        conn.commit()
        conn.close()
    except Exception:
        # Non fatal : si la BD n'est pas disponible lors de l'initialisation, ignorer.
        try:
            conn.close()
        except Exception:
            pass

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)
