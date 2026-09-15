from config import tb, BOTH
from database import get_conn
from datetime import datetime
import tkintermapview


class MapFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tb.Label(
            self, text="🗺 Carte OpenStreetMap",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=10)

        self.map_widget = tkintermapview.TkinterMapView(
            self, width=1000, height=550, corner_radius=10
        )
        self.map_widget.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Position initiale (Kinshasa)
        self.map_widget.set_position(-4.325, 15.322)
        self.map_widget.set_zoom(12)

        self.map_widget.add_left_click_map_command(self.add_marker)

    def load_points(self):
        self.map_widget.delete_all_marker()

        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT latitude, longitude FROM map_points WHERE user_id=%s",
            (self.app.current_user_id,)
        )

        for lat, lon in c.fetchall():
            self.map_widget.set_marker(lat, lon, text="📍 Point")

        conn.close()

    def add_marker(self, coords):
        lat, lon = coords

        self.map_widget.set_marker(lat, lon, text="📍 Nouveau point")
        conn = get_conn()
        c = conn.cursor()
        # Conserver la table map_points pour usage local (compatibilité)
        try:
            c.execute(
                "INSERT INTO map_points(user_id, latitude, longitude, created_at) "
                "VALUES (%s,%s,%s,%s)",
                (self.app.current_user_id, lat, lon, datetime.now().isoformat())
            )
        except Exception:
            # Si la table map_points n'existe pas ou si l'insertion échoue, continuer
            pass

        # Insérer aussi dans `items` afin que la carte web (map_server) affiche le marqueur
        try:
            title = f"Point desktop - {self.app.current_user or 'user'}"
            color = '#ff0000'
            c.execute(
                "INSERT INTO items (user_id, title, description, created_at, lat, lng, color) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (self.app.current_user_id, title, '', datetime.now().isoformat(), lat, lon, color)
            )
        except Exception:
            # Si la table 'items' n'existe pas ou si l'insertion échoue, logger ou ignorer pour l'instant
            pass

        conn.commit()
        conn.close()