from config import tb, W, BOTH, END, X, TOP, LEFT, RIGHT, Y, messagebox
from database import get_conn
from db import get_conn as get_conn_app
import requests
from datetime import datetime
import tkintermapview

class DashboardFrames(tb.Frame):
    
    def create_map_tab(self):
            tab = tb.Frame(self.notebook, padding=30)
            self.notebook.add(tab, text="🗺️ Carte Interactive")

            # Titre
            tb.Label(tab, text="Carte des Zones Électriques",
                    font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=(0, 30))

            # Conteneur principal
            map_container = tb.Frame(tab)
            map_container.pack(fill=BOTH, expand=True)

            # Panneau de contrôle (gauche)
            control_panel = tb.Frame(map_container, bootstyle="light", padding=20, width=300)
            control_panel.pack(side=LEFT, fill=Y, padx=(0, 15))
            control_panel.pack_propagate(False)

            tb.Label(control_panel, text="🎛️ Contrôles",
                    font=("Segoe UI", 14, "bold")).pack(anchor=W, pady=(0, 20))

            # Liste des zones avec checkboxes
            zones_list_frame = tb.Frame(control_panel)
            zones_list_frame.pack(fill=BOTH, expand=True)

            tb.Label(zones_list_frame, text="📍 Zones à afficher:",
                    font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(0, 10))

            # Scrollable frame pour les checkboxes
            canvas = tb.Canvas(zones_list_frame, height=300)
            scrollbar = tb.Scrollbar(zones_list_frame, orient="vertical", command=canvas.yview)
            self.zone_checkboxes_frame = tb.Frame(canvas)

            self.zone_checkboxes_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=self.zone_checkboxes_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)

            self.zone_checkboxes = {}
            self.load_zones_checkboxes(self.zone_checkboxes_frame)

            # Boutons d'action
            actions_frame = tb.Frame(control_panel)
            actions_frame.pack(fill=X, pady=20)

            tb.Button(actions_frame, text="✅ Tout cocher",
                    bootstyle="success", width=12,
                    command=self.check_all_zones).pack(pady=3)

            tb.Button(actions_frame, text="❌ Tout décocher",
                    bootstyle="danger", width=12,
                    command=self.uncheck_all_zones).pack(pady=3)

            tb.Button(actions_frame, text="📤 Envoyer Sélection",
                    bootstyle="info", width=12,
                    command=self.send_selected_zones).pack(pady=8)

            # Carte (droite)
            map_panel = tb.Frame(map_container, bootstyle="light", padding=10)
            map_panel.pack(side=RIGHT, fill=BOTH, expand=True)

            # Carte OpenStreetMap interactive
            self.map_widget = tkintermapview.TkinterMapView(map_panel, width=600, height=400)
            self.map_widget.pack(fill=BOTH, expand=True, padx=5, pady=5)

            # Centrer sur Kinshasa par défaut
            self.map_widget.set_position(-4.325, 15.322)
            self.map_widget.set_zoom(12)

            # Ajouter les marqueurs des zones existantes
            self.update_map_markers()

            # Événement de clic sur la carte pour ajouter une zone
            self.map_widget.add_right_click_menu_command(label="📍 Ajouter Zone Électrique",
                                                    command=self.add_zone_from_map,
                                                    pass_coords=True)

            # Boutons de navigation carte
            map_buttons = tb.Frame(map_panel)
            map_buttons.pack(fill=X, pady=10)

            # Première ligne de boutons
            nav_buttons1 = tb.Frame(map_buttons)
            nav_buttons1.pack(fill=X, pady=2)

            tb.Button(nav_buttons1, text="📍 Centrer Brazzavile",
                    bootstyle="primary",
                    command=self.center_map_Brazzaville).pack(side=LEFT, padx=(0, 8))

            tb.Button(nav_buttons1, text="🔍 +",
                    bootstyle="secondary",
                    command=self.zoom_in).pack(side=LEFT, padx=(0, 8))

            tb.Button(nav_buttons1, text="🔍 -",
                    bootstyle="secondary",
                    command=self.zoom_out).pack(side=LEFT, padx=(0, 8))

            tb.Button(nav_buttons1, text="🔄 Actualiser",
                    bootstyle="info",
                    command=self.update_map_markers).pack(side=LEFT, padx=(0, 8))

            tb.Button(nav_buttons1, text="🗺️ Envoyer Carte",
                    bootstyle="warning",
                    command=self.send_map_image).pack(side=LEFT, padx=(0, 8))

            tb.Button(nav_buttons1, text="🗑️ Effacer Marqueurs",
                    bootstyle="danger",
                    command=self.clear_all_markers).pack(side=LEFT)

            # Deuxième ligne de boutons - Ajout rapide de zones
            add_buttons = tb.Frame(map_buttons)
            add_buttons.pack(fill=X, pady=2)

            tb.Label(add_buttons, text="⚡ Ajouter Zone:",
                    font=("Segoe UI", 9, "bold")).pack(side=LEFT, padx=(0, 8))

            tb.Button(add_buttons, text="🏭 Poste",
                    bootstyle="success", width=8,
                    command=lambda: self.quick_add_zone("Poste de transformation")).pack(side=LEFT, padx=(0, 4))

            tb.Button(add_buttons, text="⚡ Ligne BT",
                    bootstyle="info", width=8,
                    command=lambda: self.quick_add_zone("Ligne BT")).pack(side=LEFT, padx=(0, 4))

            tb.Button(add_buttons, text="🔌 Branchement",
                    bootstyle="warning", width=10,
                    command=lambda: self.quick_add_zone("Branchement")).pack(side=LEFT, padx=(0, 4))

            tb.Button(add_buttons, text="📍 Autre",
                    bootstyle="secondary", width=6,
                    command=lambda: self.quick_add_zone("Autre")).pack(side=LEFT)
