import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'app_data'
}
conn = mysql.connector.connect(**DB_CONFIG)
c = conn.cursor()
c.execute("DESCRIBE items")
cols = [r[0] for r in c.fetchall()]
print('before cols:', cols)
if 'color' not in cols:
    try:
        c.execute('ALTER TABLE items ADD COLUMN color VARCHAR(255)')
        conn.commit()
        print('color column added')
    except Exception as e:
        print('failed to add color:', e)
else:
    print('color already present')
conn.close()
