from flask import request, jsonify
from db import get_conn
from datetime import datetime
from .helpers import notify_dashboard


def register_routes(app):
    @app.route('/api/news', methods=['GET', 'POST'])
    def news_list():
        if request.method == 'GET':
            conn = get_conn()
            c = conn.cursor()
            c.execute('SELECT id, title, body, created_by, created_at FROM news ORDER BY created_at DESC LIMIT 100')
            rows = c.fetchall()
            conn.close()
            return jsonify([{'id': r[0], 'title': r[1], 'body': r[2], 'created_by': r[3], 'created_at': r[4].isoformat() if hasattr(r[4], 'isoformat') else str(r[4])} for r in rows])
        else:
            data = request.json or {}
            title = data.get('title')
            body = data.get('body')
            created_by = data.get('created_by')
            conn = get_conn()
            c = conn.cursor()
            c.execute('INSERT INTO news (title, body, created_by, created_at) VALUES (%s,%s,%s,%s)', (title, body, created_by, datetime.now().isoformat()))
            conn.commit()
            nid = c.lastrowid
            conn.close()
            notify_dashboard()
            return jsonify({'id': nid}), 201
