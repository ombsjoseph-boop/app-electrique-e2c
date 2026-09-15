import mysql.connector
from mysql.connector import errorcode

# Configuration pour se connecter à MySQL (sans base de données spécifique)
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
}


def create_databases():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Créer la base de données 'app' pour main.py
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS app")
            print("✓ Base de données 'app' créée ou déjà existante")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la création de 'app': {err}")

        # Créer la base de données 'app_data' pour le serveur web
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS app_data")
            print("✓ Base de données 'app_data' créée ou déjà existante")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la création de 'app_data': {err}")

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur d'accès : vérifiez votre nom d'utilisateur et mot de passe")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données n'existe pas")
        else:
            print(f"Erreur MySQL : {err}")
        return False

    return True


def init_app_database():
    db_config = config.copy()
    db_config['database'] = 'app'

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Tables pour main.py
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                password VARCHAR(255)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items(
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(255),
                description TEXT,
                created_at DATETIME
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map_points(
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                latitude FLOAT,
                longitude FLOAT,
                created_at DATETIME
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Tables de 'app' initialisées")

    except mysql.connector.Error as err:
        print(f"Erreur lors de l'initialisation de 'app': {err}")
        return False

    return True


def init_app_data_database():
    db_config = config.copy()
    db_config['database'] = 'app_data'

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Tables pour le serveur web
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                image VARCHAR(255),
                created_at DATETIME,
                photo VARCHAR(255)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(255),
                description TEXT,
                created_at DATETIME,
                lat FLOAT,
                lng FLOAT,
                color VARCHAR(255),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Tables de 'app_data' initialisées")

    except mysql.connector.Error as err:
        print(f"Erreur lors de l'initialisation de 'app_data': {err}")
        return False

    return True


if __name__ == "__main__":
    print("Initialisation des bases de données MySQL...")
    print("Assurez-vous que XAMPP est démarré et que MySQL fonctionne sur localhost:3306")
    print()

    if create_databases():
        if init_app_database() and init_app_data_database():
            print("\n✓ Toutes les bases de données et tables ont été créées avec succès!")
            print("\nPour migrer les données existantes de SQLite vers MySQL, vous devrez:")
            print("1. Exporter les données de vos fichiers .db SQLite")
            print("2. Les importer dans les nouvelles bases MySQL")
            print("3. Supprimer les anciens fichiers .db si nécessaire")
        else:
            print("\n❌ Erreur lors de l'initialisation des tables")
    else:
        print("\n❌ Erreur lors de la création des bases de données")