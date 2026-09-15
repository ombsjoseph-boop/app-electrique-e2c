from flask import request, jsonify
from db import get_conn
from datetime import datetime
from .helpers import notify_dashboard


def register_routes(app):
    @app.route('/api/markers', methods=['GET', 'POST'])
    def markers():
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            conn = get_conn()
            c = conn.cursor()
            if user_id:
                c.execute('SELECT id, title, lat, lng, color, COALESCE(likes,0) FROM items WHERE user_id=%s AND lat IS NOT NULL AND lng IS NOT NULL', (user_id,))
            else:
                c.execute('SELECT id, title, lat, lng, color, COALESCE(likes,0) FROM items WHERE lat IS NOT NULL AND lng IS NOT NULL')
            rows = c.fetchall()
            conn.close()
            return jsonify([{'id': r[0], 'title': r[1], 'lat': r[2], 'lng': r[3], 'color': r[4], 'likes': int(r[5] or 0)} for r in rows])
        else:
            data = request.json or {}
            user_id = data.get('user_id')
            title = data.get('title')
            lat = data.get('lat')
            lng = data.get('lng')
            color = data.get('color') or '#ff0000'
            conn = get_conn()
            c = conn.cursor()
            c.execute('INSERT INTO items (user_id, title, description, created_at, lat, lng, color) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (user_id, title, '', datetime.now().isoformat(), lat, lng, color))
            conn.commit()
            item_id = c.lastrowid
            conn.close()
            notify_dashboard()
            return jsonify({'id': item_id}), 201

    @app.route('/api/map_points', methods=['GET'])
    def map_points():
        conn = get_conn()
        c = conn.cursor()
        c.execute('SELECT id, user_id, latitude, longitude, created_at FROM map_points WHERE latitude IS NOT NULL AND longitude IS NOT NULL')
        rows = c.fetchall()
        conn.close()
        def fmt(dt):
            try:
                return dt.isoformat()
            except Exception:
                return str(dt)
        return jsonify([{'id': r[0], 'user_id': r[1], 'lat': float(r[2]), 'lng': float(r[3]), 'created_at': fmt(r[4])} for r in rows])

    @app.route('/api/electric_zones', methods=['GET'])
    def electric_zones():
        conn = get_conn()
        c = conn.cursor()
        c.execute('SELECT id, name, type, latitude, longitude, city, voltage, status, description, created_at FROM electric_zones')
        rows = c.fetchall()
        conn.close()
        def fmt(dt):
            try:
                return dt.isoformat()
            except Exception:
                return str(dt)
        return jsonify([{
            'id': r[0], 'name': r[1], 'type': r[2], 'lat': float(r[3]) if r[3] is not None else None, 'lng': float(r[4]) if r[4] is not None else None,
            'city': r[5], 'voltage': r[6], 'status': r[7], 'description': r[8], 'created_at': fmt(r[9])
        } for r in rows])

    @app.route('/api/markers/<int:item_id>', methods=['PUT', 'DELETE'])
    def marker_item(item_id):
        if request.method == 'PUT':
            data = request.json or {}
            color = data.get('color')
            title = data.get('title')
            lat = data.get('lat')
            lng = data.get('lng')
            conn = get_conn()
            c = conn.cursor()
            c.execute('UPDATE items SET title=%s, lat=%s, lng=%s, color=%s WHERE id=%s', (title, lat, lng, color, item_id))
            conn.commit()
            conn.close()
            return '', 204
        else:
            conn = get_conn()
            c = conn.cursor()
            c.execute('DELETE FROM items WHERE id=%s', (item_id,))
            conn.commit()
            conn.close()
            return '', 204

    @app.route('/api/markers/<int:item_id>/like', methods=['POST'])
    def like_marker(item_id):
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute('UPDATE items SET likes = COALESCE(likes,0) + 1 WHERE id=%s', (item_id,))
            conn.commit()
            c.execute('SELECT COALESCE(likes,0) FROM items WHERE id=%s', (item_id,))
            row = c.fetchone()
            likes = int(row[0]) if row else 0
            conn.close()
            notify_dashboard()
            return jsonify({'id': item_id, 'likes': likes}), 200
        except Exception:
            conn.close()
            return jsonify({'error': 'failed'}), 500
