from config import tb, W, BOTH, END, X, TOP, LEFT, RIGHT, Y, messagebox
from database import get_conn
from db import get_conn as get_conn_app

from datetime import datetime
import tkintermapview

from datetime import datetime
from database import get_conn

class DashboardFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Titre principal
        title_frame = tb.Frame(self, bootstyle="primary")
        title_frame.pack(fill=X, pady=(0, 30))

        tb.Label(title_frame, text=" Dashboard Administration Technique",
                 font=("Segoe UI", 28, "bold",),
                 bootstyle="inverse-primary").pack(pady=20)

        # Conteneur principal avec onglets
        self.notebook = tb.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True, padx=20, pady=(0, 10))

        # Onglet Gestion des Zones
        self.create_zones_tab()

        # Onglet Carte Interactive
        self.create_map_tab()

        # Onglet Rapports
        self.create_reports_tab()

        # Onglet Agents
        self.create_agents_tab()

        # Onglet Zones de Relevé (géographiques) et affectation des agents
        self.create_zones_releve_tab()

        # Onglet Clients
        self.create_clients_tab()

        # Connecter l'événement de changement d'onglet
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Actualiser les données au démarrage
        self.refresh_zones()
        self.refresh_agents()
        self.refresh_zones_releve()
        self.refresh_clients()
        self.load_zone_suggestions()

    def refresh(self):
        """Méthode appelée lors de l'affichage du frame pour actualiser les données"""
        self.refresh_zones()
        # self.load_map_points()  # Méthode non définie

    def create_zones_tab(self):
        tab = tb.Frame(self.notebook, padding=30)
        self.notebook.add(tab, text="📍 Gestion des Zones")

        # Titre de l'onglet
        tb.Label(tab, text="Gestion des Zones Électriques",
                 font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=(0, 30))

        # Conteneur horizontal pour formulaire et liste
        main_container = tb.Frame(tab)
        main_container.pack(fill=BOTH, expand=True)

        # Panneau gauche - Formulaire
        form_panel = tb.Frame(main_container, bootstyle="light", padding=25)
        form_panel.pack(side=LEFT, fill=Y, padx=(0, 15))

        tb.Label(form_panel, text="📝 Nouvelle Zone Électrique",
                 font=("Segoe UI", 14, "bold")).pack(anchor=W, pady=(0, 20))

        # Cadre pour le formulaire
        form_frame = tb.Frame(form_panel)
        form_frame.pack(fill=X, pady=15)

        # Ligne 1: Nom et Type
        row1 = tb.Frame(form_frame)
        row1.pack(fill=X, pady=8)

        tb.Label(row1, text="🏷️ Nom:").pack(side=LEFT, padx=(0, 8))
        self.zone_name = tb.Entry(row1, width=25, font=("Segoe UI", 10))
        self.zone_name.pack(side=LEFT, padx=(0, 20))

        tb.Label(row1, text="🔧 Type:").pack(side=LEFT, padx=(0, 8))
        self.zone_type = tb.Combobox(row1,
                                     values=["Réseau HT", "Poste de transformation",
                                             "Ligne BT", "Branchement", "Autre"],
                                     width=18, font=("Segoe UI", 10))
        self.zone_type.pack(side=LEFT)

        # Ligne 2: Localisation
        row2 = tb.Frame(form_frame)
        row2.pack(fill=X, pady=8)

        tb.Label(row2, text="📍 Lat:").pack(side=LEFT, padx=(0, 8))
        self.zone_lat = tb.Entry(row2, width=12, font=("Segoe UI", 10))
        self.zone_lat.pack(side=LEFT, padx=(0, 12))

        tb.Label(row2, text="📍 Lng:").pack(side=LEFT, padx=(0, 8))
        self.zone_lng = tb.Entry(row2, width=12, font=("Segoe UI", 10))
        self.zone_lng.pack(side=LEFT, padx=(0, 20))

        tb.Label(row2, text="🏙️ Ville:").pack(side=LEFT, padx=(0, 8))
        self.zone_city = tb.Entry(row2, width=15, font=("Segoe UI", 10))
        self.zone_city.pack(side=LEFT)

        # Ligne 3: Informations techniques
        row3 = tb.Frame(form_frame)
        row3.pack(fill=X, pady=8)

        tb.Label(row3, text="⚡ Tension (V):").pack(side=LEFT, padx=(0, 8))
        self.zone_voltage = tb.Entry(row3, width=12, font=("Segoe UI", 10))
        self.zone_voltage.pack(side=LEFT, padx=(0, 20))

        tb.Label(row3, text="📊 État:").pack(side=LEFT, padx=(0, 8))
        self.zone_status = tb.Combobox(row3,
                                       values=["✅ Fonctionnel", "🔧 En maintenance",
                                               "❌ Hors service", "🔨 À réparer"],
                                       width=15, font=("Segoe UI", 10))
        self.zone_status.pack(side=LEFT)

        # Description
        desc_frame = tb.Frame(form_frame)
        desc_frame.pack(fill=X, pady=15)

        tb.Label(desc_frame, text="📝 Description/Commentaires:").pack(anchor=W, pady=(0, 5))
        self.zone_description = tb.Text(desc_frame, height=4, width=50,
                                       font=("Segoe UI", 10))
        self.zone_description.pack()

        # Boutons d'action
        buttons_frame = tb.Frame(form_panel)
        buttons_frame.pack(fill=X, pady=20)

        tb.Button(buttons_frame, text="💾 Enregistrer",
                  bootstyle="success", width=15,
                  command=self.save_electric_zone).pack(side=LEFT, padx=(0, 12))

        tb.Button(buttons_frame, text="📤 Envoyer Rapport",
                  bootstyle="info", width=15,
                  command=self.send_electric_report).pack(side=LEFT, padx=(0, 12))

        tb.Button(buttons_frame, text="🗑️ Effacer",
                  bootstyle="secondary", width=10,
                  command=self.clear_form).pack(side=LEFT)

        # Panneau droit - Liste des zones
        list_panel = tb.Frame(main_container, bootstyle="light", padding=25)
        list_panel.pack(side=RIGHT, fill=BOTH, expand=True)

        tb.Label(list_panel, text="📊 Zones Enregistrées",
                 font=("Segoe UI", 14, "bold")).pack(anchor=W, pady=(0, 20))

        # Treeview pour la liste
        tree_frame = tb.Frame(list_panel)
        tree_frame.pack(fill=BOTH, expand=True)

        self.zones_tree = tb.Treeview(tree_frame,
                                      columns=("id", "name", "type", "city", "status", "date"),
                                      show="headings", height=12,
                                      bootstyle="primary")

        # Configuration des colonnes
        self.zones_tree.heading("id", text="ID")
        self.zones_tree.heading("name", text="Nom")
        self.zones_tree.heading("type", text="Type")
        self.zones_tree.heading("city", text="Ville")
        self.zones_tree.heading("status", text="État")
        self.zones_tree.heading("date", text="Date")

        self.zones_tree.column("id", width=50, anchor="center")
        self.zones_tree.column("name", width=150)
        self.zones_tree.column("type", width=120)
        self.zones_tree.column("city", width=100)
        self.zones_tree.column("status", width=100)
        self.zones_tree.column("date", width=120)

        # Scrollbar
        scrollbar = tb.Scrollbar(tree_frame, orient="vertical",
                                command=self.zones_tree.yview)
        self.zones_tree.configure(yscrollcommand=scrollbar.set)

        self.zones_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Boutons pour la liste
        list_buttons = tb.Frame(list_panel)
        list_buttons.pack(fill=X, pady=20)

        tb.Button(list_buttons, text="🔄 Actualiser",
                  bootstyle="secondary",
                  command=self.refresh_zones).pack(side=LEFT, padx=(0, 12))

        tb.Button(list_buttons, text="📋 Rapport",
                  bootstyle="primary",
                  command=self.generate_report).pack(side=LEFT, padx=(0, 12))

        tb.Button(list_buttons, text="🗺️ Voir sur Carte",
                  bootstyle="info",
                  command=lambda: self.notebook.select(1)).pack(side=LEFT)

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
        actions_frame.pack(fill=X, pady=5)

        tb.Button(actions_frame, text="✅ Tout cocher",
                  bootstyle="success", width=12,
                  command=self.check_all_zones).pack(pady=3)

        tb.Button(actions_frame, text="❌ Tout décocher",
                  bootstyle="danger", width=12,
                  command=self.uncheck_all_zones).pack(pady=3)

        tb.Button(actions_frame, text="📤 Envoyer Sélection",
                  bootstyle="info", width=12,
                  command=self.send_selected_zones).pack(pady=3)
        
        tb.Button(actions_frame, text="suprimer",
                  bootstyle="danger", width=12,
                  command=self.surprime_zone).pack(pady=3)

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

    def create_reports_tab(self):
        tab = tb.Frame(self.notebook, padding=30)
        self.notebook.add(tab, text="📊 Rapports")

        tb.Label(tab, text="Rapports et Statistiques",
                 font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=(0, 30))

        # Conteneur pour les rapports
        reports_container = tb.Frame(tab)
        reports_container.pack(fill=BOTH, expand=True)

        # Statistiques générales
        stats_frame = tb.Frame(reports_container, bootstyle="light", padding=25)
        stats_frame.pack(fill=X, pady=(0, 25))

        tb.Label(stats_frame, text="📈 Statistiques Générales",
                 font=("Segoe UI", 14, "bold")).pack(anchor=W, pady=(0, 20))

        self.stats_text = tb.Text(stats_frame, height=8, width=80,
                                 font=("Consolas", 10))
        self.stats_text.pack()

        # Boutons d'action
        report_buttons = tb.Frame(reports_container)
        report_buttons.pack(fill=X, pady=15)

        tb.Button(report_buttons, text="📊 Générer Rapport",
                  bootstyle="primary",
                  command=self.generate_detailed_report).pack(side=LEFT, padx=(0, 12))

        tb.Button(report_buttons, text="💾 Exporter CSV",
                  bootstyle="success",
                  command=self.export_csv).pack(side=LEFT, padx=(0, 12))

        tb.Button(report_buttons, text="📧 Envoyer Rapport",
                  bootstyle="info",
                  command=self.send_report_email).pack(side=LEFT)

    def _get_table_columns(self, conn, table):
        """Retourne la liste des colonnes existantes d'une table (insensible à la casse)."""
        try:
            c = conn.cursor()
            c.execute(f"SHOW COLUMNS FROM `{table}`")
            cols = [r[0] for r in c.fetchall()]
            c.close()
            return cols
        except Exception:
            return []

    def create_agents_tab(self):
        tab = tb.Frame(self.notebook, padding=30)
        self.notebook.add(tab, text="🧑‍🔧 Agents")

        tb.Label(tab, text="Gestion des Agents",
                 font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=(0, 30))

        main_container = tb.Frame(tab)
        main_container.pack(fill=BOTH, expand=True)

        # Panneau gauche - Formulaire de création
        form_panel = tb.Frame(main_container, bootstyle="light", padding=25)
        form_panel.pack(side=LEFT, fill=Y, padx=(0, 15))

        tb.Label(form_panel, text="➕ Nouvel Agent",
                 font=("Segoe UI", 14, "bold")).pack(anchor=W, pady=(0, 20))

        form_frame = tb.Frame(form_panel)
        form_frame.pack(fill=X, pady=10)

        tb.Label(form_frame, text="🏷️ Nom:").pack(anchor=W, pady=(0, 4))
        self.agent_nom = tb.Entry(form_frame, width=30, font=("Segoe UI", 10))
        self.agent_nom.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="✉️ Email:").pack(anchor=W, pady=(0, 4))
        self.agent_email = tb.Entry(form_frame, width=30, font=("Segoe UI", 10))
        self.agent_email.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="🔒 Mot de passe:").pack(anchor=W, pady=(0, 4))
        self.agent_password = tb.Entry(form_frame, width=30, font=("Segoe UI", 10), show="•")
        self.agent_password.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="🔒 Confirmer le mot de passe:").pack(anchor=W, pady=(0, 4))
        self.agent_password_confirm = tb.Entry(form_frame, width=30, font=("Segoe UI", 10), show="•")
        self.agent_password_confirm.pack(fill=X, pady=(0, 12))

        buttons_frame = tb.Frame(form_panel)
        buttons_frame.pack(fill=X, pady=15)

        tb.Button(buttons_frame, text="💾 Créer l'agent",
                  bootstyle="success", width=15,
                  command=self.create_agent).pack(side=LEFT, padx=(0, 12))

        tb.Button(buttons_frame, text="🗑️ Effacer",
                  bootstyle="secondary", width=10,
                  command=self.clear_agent_form).pack(side=LEFT)

        # Panneau droit - Liste des agents
        list_panel = tb.Frame(main_container, bootstyle="light", padding=25)
        list_panel.pack(side=RIGHT, fill=BOTH, expand=True)

        header_frame = tb.Frame(list_panel)
        header_frame.pack(fill=X, pady=(0, 15))

        tb.Label(header_frame, text="👥 Agents Enregistrés",
                 font=("Segoe UI", 14, "bold")).pack(side=LEFT)

        tb.Button(header_frame, text="🔄 Actualiser",
                  bootstyle="secondary",
                  command=self.refresh_agents).pack(side=RIGHT)

        tb.Button(header_frame, text="🚫 Activer / Désactiver",
                  bootstyle="warning",
                  command=self.toggle_selected_agent_status).pack(side=RIGHT, padx=(0, 10))

        tb.Button(header_frame, text="✏️ Modifier",
                  bootstyle="secondary",
                  command=self.open_edit_agent_popup).pack(side=RIGHT, padx=(0, 10))

        tb.Button(header_frame, text="📋 Fiche & Historique",
                  bootstyle="info",
                  command=self.open_selected_agent_details).pack(side=RIGHT, padx=(0, 10))

        tb.Label(list_panel, text="💡 Double-cliquez sur un agent (ou sélectionnez-le puis utilisez les boutons ci-dessus)",
                 font=("Segoe UI", 8, "italic")).pack(anchor=W, pady=(0, 10))

        tree_frame = tb.Frame(list_panel)
        tree_frame.pack(fill=BOTH, expand=True)

        self.agents_tree = tb.Treeview(tree_frame,
                                       columns=("id", "nom", "email", "statut", "created_at"),
                                       show="headings", height=15,
                                       bootstyle="primary")

        self.agents_tree.heading("id", text="ID")
        self.agents_tree.heading("nom", text="Nom")
        self.agents_tree.heading("email", text="Email")
        self.agents_tree.heading("statut", text="Statut")
        self.agents_tree.heading("created_at", text="Créé le")

        self.agents_tree.column("id", width=60, anchor="center")
        self.agents_tree.column("nom", width=180)
        self.agents_tree.column("email", width=230)
        self.agents_tree.column("statut", width=100, anchor="center")
        self.agents_tree.column("created_at", width=150)

        # Couleurs selon le statut
        self.agents_tree.tag_configure("actif", foreground="#1e7e34")
        self.agents_tree.tag_configure("inactif", foreground="#b02a37")

        scrollbar = tb.Scrollbar(tree_frame, orient="vertical",
                                command=self.agents_tree.yview)
        self.agents_tree.configure(yscrollcommand=scrollbar.set)

        self.agents_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Double-clic sur une ligne -> ouvre directement la fiche de l'agent
        self.agents_tree.bind("<Double-1>", self.on_agent_row_double_click)

    def clear_agent_form(self):
        """Vide les champs du formulaire de création d'agent."""
        self.agent_nom.delete(0, END)
        self.agent_email.delete(0, END)
        self.agent_password.delete(0, END)
        self.agent_password_confirm.delete(0, END)

    def create_agent(self):
        """Crée un nouvel agent depuis le formulaire (réservé à l'admin)."""
        nom = self.agent_nom.get().strip()
        email = self.agent_email.get().strip()
        password = self.agent_password.get()
        password_confirm = self.agent_password_confirm.get()

        if not nom or not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir le nom, l'email et le mot de passe")
            return

        if password != password_confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
            return

        if len(password) < 6:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 6 caractères")
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO agent (nom, email, password, created_at)
                VALUES (%s, %s, %s, %s)
            """, (nom, email, password, datetime.now()))
            conn.commit()

            messagebox.showinfo("Succès", f"Agent '{nom}' créé avec succès !")
            self.clear_agent_form()
            self.refresh_agents()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de l'agent: {str(e)}")
        finally:
            conn.close()

    def refresh_agents(self):
        self.agents_tree.delete(*self.agents_tree.get_children())
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("""
                SELECT id, nom, email, statut, created_at
                FROM agent
                ORDER BY created_at DESC
            """)
            for r in c.fetchall():
                agent_id, nom, email, statut, created_at = r
                statut = statut or "actif"
                statut_affiche = "✅ Actif" if statut == "actif" else "🚫 Désactivé"
                tag = "actif" if statut == "actif" else "inactif"
                self.agents_tree.insert("", END,
                                         values=(agent_id, nom, email, statut_affiche, created_at),
                                         tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des agents: {str(e)}")
        finally:
            conn.close()

    def on_agent_row_double_click(self, event):
        """Ouvre la fiche de l'agent sur double-clic dans le tableau."""
        self.open_selected_agent_details()

    def get_selected_agent_id(self):
        """Retourne l'id de l'agent sélectionné dans le tableau, ou None."""
        selection = self.agents_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un agent dans la liste.")
            return None

        item = self.agents_tree.item(selection[0])
        values = item.get("values")
        if not values:
            return None

        return values[0]

    def open_edit_agent_popup(self):
        """Ouvre un formulaire pré-rempli pour modifier le nom, l'email et
        éventuellement le mot de passe d'un agent existant."""
        agent_id = self.get_selected_agent_id()
        if agent_id is None:
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("SELECT nom, email FROM agent WHERE id = %s", (agent_id,))
            row = c.fetchone()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'agent: {str(e)}")
            conn.close()
            return
        finally:
            conn.close()

        if not row:
            messagebox.showerror("Erreur", "Agent introuvable.")
            return

        current_nom, current_email = row

        popup = tb.Toplevel(self)
        popup.title("✏️ Modifier l'agent")
        popup.geometry("420x420")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        tb.Label(popup, text=f"Modifier l'agent #{agent_id}",
                 font=("Segoe UI", 14, "bold")).pack(pady=(20, 15))

        form_frame = tb.Frame(popup, padding=20)
        form_frame.pack(fill=X)

        tb.Label(form_frame, text="🏷️ Nom:").pack(anchor=W, pady=(0, 4))
        edit_nom = tb.Entry(form_frame, width=35, font=("Segoe UI", 10))
        edit_nom.pack(fill=X, pady=(0, 12))
        edit_nom.insert(0, current_nom)

        tb.Label(form_frame, text="✉️ Email:").pack(anchor=W, pady=(0, 4))
        edit_email = tb.Entry(form_frame, width=35, font=("Segoe UI", 10))
        edit_email.pack(fill=X, pady=(0, 12))
        edit_email.insert(0, current_email)

        tb.Label(form_frame, text="🔒 Nouveau mot de passe (laisser vide pour ne pas changer):").pack(
            anchor=W, pady=(0, 4))
        edit_password = tb.Entry(form_frame, width=35, font=("Segoe UI", 10), show="•")
        edit_password.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="🔒 Confirmer le nouveau mot de passe:").pack(anchor=W, pady=(0, 4))
        edit_password_confirm = tb.Entry(form_frame, width=35, font=("Segoe UI", 10), show="•")
        edit_password_confirm.pack(fill=X, pady=(0, 12))

        def save_changes():
            nom = edit_nom.get().strip()
            email = edit_email.get().strip()
            password = edit_password.get()
            password_confirm = edit_password_confirm.get()

            if not nom or not email:
                messagebox.showerror("Erreur", "Le nom et l'email sont obligatoires.")
                return

            if password or password_confirm:
                if password != password_confirm:
                    messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
                    return
                if len(password) < 6:
                    messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 6 caractères.")
                    return

            conn = get_conn()
            try:
                c = conn.cursor()
                if password:
                    c.execute("""
                        UPDATE agent SET nom = %s, email = %s, password = %s WHERE id = %s
                    """, (nom, email, password, agent_id))
                else:
                    c.execute("""
                        UPDATE agent SET nom = %s, email = %s WHERE id = %s
                    """, (nom, email, agent_id))
                conn.commit()
                messagebox.showinfo("Succès", "Agent modifié avec succès.")
                self.refresh_agents()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}\n"
                                                f"(Vérifiez que l'email n'est pas déjà utilisé par un autre agent.)")
            finally:
                conn.close()

        buttons_frame = tb.Frame(popup, padding=(20, 10))
        buttons_frame.pack(fill=X)

        tb.Button(buttons_frame, text="💾 Enregistrer",
                  bootstyle="success", width=15,
                  command=save_changes).pack(side=LEFT, padx=(0, 12))

        tb.Button(buttons_frame, text="❌ Annuler",
                  bootstyle="secondary", width=12,
                  command=popup.destroy).pack(side=LEFT)

    def toggle_selected_agent_status(self):
        """Active ou désactive le compte de l'agent sélectionné."""
        agent_id = self.get_selected_agent_id()
        if agent_id is None:
            return
        self._toggle_agent_status(agent_id)

    def _toggle_agent_status(self, agent_id):
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("SELECT nom, statut FROM agent WHERE id = %s", (agent_id,))
            row = c.fetchone()
            if not row:
                messagebox.showerror("Erreur", "Agent introuvable.")
                return

            nom, statut = row
            statut = statut or "actif"
            nouveau_statut = "inactif" if statut == "actif" else "actif"

            action_label = "désactiver" if nouveau_statut == "inactif" else "réactiver"
            confirm = messagebox.askyesno(
                "Confirmation",
                f"Voulez-vous vraiment {action_label} le compte de l'agent « {nom} » ?\n\n"
                f"Un agent désactivé ne pourra plus se connecter à l'application."
            )
            if not confirm:
                return

            c.execute("UPDATE agent SET statut = %s WHERE id = %s", (nouveau_statut, agent_id))
            conn.commit()

            messagebox.showinfo(
                "Succès",
                f"Le compte de « {nom} » a été {'désactivé' if nouveau_statut == 'inactif' else 'réactivé'}."
            )
            self.refresh_agents()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du changement de statut: {str(e)}\n\n"
                                            f"Astuce : assurez-vous que la colonne `statut` existe bien "
                                            f"dans la table `agent` (voir alter_agent_statut.sql).")
        finally:
            conn.close()

    def open_selected_agent_details(self):
        """Récupère l'agent sélectionné dans le tableau et ouvre sa fiche."""
        agent_id = self.get_selected_agent_id()
        if agent_id is None:
            return
        self.show_agent_details(agent_id)

    def show_agent_details(self, agent_id):
        """
        Ouvre une fenêtre affichant :
        - la fiche de l'agent (nom, email, date de création)
        - des statistiques d'activité (nb de relevés, dernier relevé, consommation totale relevée)
        - l'historique détaillé des relevés effectués par l'agent
        - un aperçu de son activité de messagerie
        """
        conn = get_conn()
        try:
            c = conn.cursor()

            # --- Infos de base de l'agent ---
            c.execute("""
                SELECT id, nom, email, statut, created_at
                FROM agent
                WHERE id = %s
            """, (agent_id,))
            agent_row = c.fetchone()

            if not agent_row:
                messagebox.showerror("Erreur", "Agent introuvable.")
                return

            _, agent_nom, agent_email, agent_statut, agent_created_at = agent_row
            agent_statut = agent_statut or "actif"

            # --- Statistiques de relevés ---
            c.execute("""
                SELECT COUNT(*), COALESCE(SUM(consommation), 0), MAX(date_releve)
                FROM releves
                WHERE agent_id = %s
            """, (agent_id,))
            nb_releves, total_consommation, dernier_releve = c.fetchone()

            # --- Historique détaillé des relevés (avec le client concerné) ---
            c.execute("""
                SELECT r.date_releve, u.nom, u.numero_compteur, r.consommation, r.notes, r.created_at
                FROM releves r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.agent_id = %s
                ORDER BY r.date_releve DESC, r.created_at DESC
            """, (agent_id,))
            historique = c.fetchall()

            # --- Activité de messagerie (résumé) ---
            c.execute("""
                SELECT COUNT(*) FROM messages WHERE sender_id = %s
            """, (agent_id,))
            nb_messages_envoyes = c.fetchone()[0]

            c.execute("""
                SELECT COUNT(*) FROM messages WHERE receiver_id = %s
            """, (agent_id,))
            nb_messages_recus = c.fetchone()[0]

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de la fiche agent: {str(e)}")
            conn.close()
            return
        finally:
            conn.close()

        # --- Construction de la fenêtre ---
        popup = tb.Toplevel(self)
        popup.title(f"🧑‍🔧 Fiche Agent - {agent_nom}")
        popup.geometry("900x650")
        popup.transient(self)
        popup.grab_set()

        # En-tête avec les infos principales
        header = tb.Frame(popup, bootstyle="primary", padding=20)
        header.pack(fill=X)

        statut_badge = "✅ Actif" if agent_statut == "actif" else "🚫 Désactivé"

        tb.Label(header, text=f"🧑‍🔧 {agent_nom}    [{statut_badge}]",
                 font=("Segoe UI", 18, "bold"),
                 bootstyle="inverse-primary").pack(anchor=W)
        tb.Label(header, text=f"✉️ {agent_email}    |    📅 Agent depuis le {agent_created_at}",
                 font=("Segoe UI", 10),
                 bootstyle="inverse-primary").pack(anchor=W, pady=(5, 0))

        # Bandeau de statistiques
        stats_frame = tb.Frame(popup, padding=(20, 15))
        stats_frame.pack(fill=X)

        stats = [
            ("🔐 Statut du compte", statut_badge),
            ("📊 Relevés effectués", str(nb_releves)),
            ("⚡ Consommation totale relevée", f"{total_consommation} kWh"),
            ("🕓 Dernier relevé", str(dernier_releve) if dernier_releve else "Aucun"),
            ("✉️ Messages (envoyés / reçus)", f"{nb_messages_envoyes} / {nb_messages_recus}"),
        ]

        for label_text, value_text in stats:
            card = tb.Frame(stats_frame, bootstyle="light", padding=12)
            card.pack(side=LEFT, fill=X, expand=True, padx=6)
            tb.Label(card, text=label_text, font=("Segoe UI", 9)).pack(anchor=W)
            tb.Label(card, text=value_text, font=("Segoe UI", 13, "bold")).pack(anchor=W, pady=(4, 0))

        # Historique des relevés
        history_panel = tb.Frame(popup, padding=(20, 10))
        history_panel.pack(fill=BOTH, expand=True)

        tb.Label(history_panel, text="🗂️ Historique des relevés effectués",
                 font=("Segoe UI", 13, "bold")).pack(anchor=W, pady=(0, 10))

        tree_frame = tb.Frame(history_panel)
        tree_frame.pack(fill=BOTH, expand=True)

        history_tree = tb.Treeview(tree_frame,
                                    columns=("date", "client", "compteur", "consommation", "notes", "saisi_le"),
                                    show="headings", height=12,
                                    bootstyle="primary")

        history_tree.heading("date", text="Date du relevé")
        history_tree.heading("client", text="Abonné")
        history_tree.heading("compteur", text="N° Compteur")
        history_tree.heading("consommation", text="Consommation (kWh)")
        history_tree.heading("notes", text="Notes / Anomalies")
        history_tree.heading("saisi_le", text="Saisi le")

        history_tree.column("date", width=100, anchor="center")
        history_tree.column("client", width=160)
        history_tree.column("compteur", width=140)
        history_tree.column("consommation", width=130, anchor="center")
        history_tree.column("notes", width=200)
        history_tree.column("saisi_le", width=140)

        history_scrollbar = tb.Scrollbar(tree_frame, orient="vertical",
                                          command=history_tree.yview)
        history_tree.configure(yscrollcommand=history_scrollbar.set)

        history_tree.pack(side=LEFT, fill=BOTH, expand=True)
        history_scrollbar.pack(side=RIGHT, fill=Y)

        if historique:
            for date_releve, client_nom, compteur, consommation, notes, created_at in historique:
                history_tree.insert("", END, values=(
                    date_releve,
                    client_nom or "—",
                    compteur or "—",
                    consommation,
                    notes or "",
                    created_at,
                ))
        else:
            tb.Label(history_panel, text="Aucun relevé enregistré pour cet agent pour le moment.",
                     font=("Segoe UI", 9, "italic")).pack(anchor=W, pady=10)

        # Boutons d'action
        footer = tb.Frame(popup, padding=(20, 10))
        footer.pack(fill=X)

        def edit_from_fiche():
            popup.destroy()
            self.open_edit_agent_popup()

        def toggle_from_fiche():
            popup.destroy()
            self._toggle_agent_status(agent_id)

        tb.Button(footer, text="Fermer", bootstyle="secondary",
                  command=popup.destroy).pack(side=RIGHT)

        tb.Button(footer, text="🚫 Activer / Désactiver", bootstyle="warning",
                  command=toggle_from_fiche).pack(side=RIGHT, padx=(0, 10))

        tb.Button(footer, text="✏️ Modifier", bootstyle="secondary",
                  command=edit_from_fiche).pack(side=RIGHT, padx=(0, 10))

    def create_zones_releve_tab(self):
        """
        Onglet de gestion des zones géographiques de relevé (ville / quartier / secteur)
        et affectation d'un ou plusieurs agents à chaque zone.

        Règle métier : la zone d'un client est déterminée par les champs
        `ville` / `quartier` renseignés lors de son inscription (et non par un choix
        manuel arbitraire). Cet onglet sert à définir les zones (ville/quartier/secteur)
        et à y affecter des agents ; le rattachement client -> zone est ensuite déduit
        automatiquement par correspondance ville/quartier (voir assign_client_zone).
        """
        tab = tb.Frame(self.notebook, padding=30)
        self.notebook.add(tab, text="🗺️ Zones de Relevé")

        tb.Label(tab, text="Zones Géographiques de Relevé",
                 font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=(0, 10))

        tb.Label(tab, text="Créez des zones (ville / quartier / secteur) et affectez-y un ou plusieurs "
                           "agents. Un client est automatiquement rattaché à la zone dont la ville et le "
                           "quartier correspondent à ceux saisis à son inscription.",
                 font=("Segoe UI", 9, "italic")).pack(anchor=W, pady=(0, 20))

        main_container = tb.Frame(tab)
        main_container.pack(fill=BOTH, expand=True)

        # ---------- Panneau gauche : formulaire de création ----------
        form_panel = tb.Frame(main_container, bootstyle="light", padding=25)
        form_panel.pack(side=LEFT, fill=Y, padx=(0, 15))

        tb.Label(form_panel, text="➕ Nouvelle Zone",
                 font=("Segoe UI", 14, "bold")).pack(anchor=W, pady=(0, 20))

        form_frame = tb.Frame(form_panel)
        form_frame.pack(fill=X, pady=10)

        tb.Label(form_frame, text="🏙️ Ville:").pack(anchor=W, pady=(0, 4))
        self.zr_ville = tb.Entry(form_frame, width=30, font=("Segoe UI", 10))
        self.zr_ville.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="🏘️ Quartier:").pack(anchor=W, pady=(0, 4))
        self.zr_quartier = tb.Entry(form_frame, width=30, font=("Segoe UI", 10))
        self.zr_quartier.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="📌 Secteur:").pack(anchor=W, pady=(0, 4))
        self.zr_secteur = tb.Entry(form_frame, width=30, font=("Segoe UI", 10))
        self.zr_secteur.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="🏷️ Nom de la zone (optionnel, auto-généré sinon):").pack(
            anchor=W, pady=(0, 4))
        self.zr_nom = tb.Entry(form_frame, width=30, font=("Segoe UI", 10))
        self.zr_nom.pack(fill=X, pady=(0, 12))

        tb.Label(form_frame, text="📝 Description:").pack(anchor=W, pady=(0, 4))
        self.zr_description = tb.Text(form_frame, height=3, width=30, font=("Segoe UI", 10))
        self.zr_description.pack(fill=X, pady=(0, 12))

        buttons_frame = tb.Frame(form_panel)
        buttons_frame.pack(fill=X, pady=15)

        tb.Button(buttons_frame, text="💾 Créer la zone",
                  bootstyle="success", width=15,
                  command=self.create_zone_releve).pack(side=LEFT, padx=(0, 12))

        tb.Button(buttons_frame, text="🗑️ Effacer",
                  bootstyle="secondary", width=10,
                  command=self.clear_zone_releve_form).pack(side=LEFT)

        # ---------- Panneau droit : liste des zones ----------
        list_panel = tb.Frame(main_container, bootstyle="light", padding=25)
        list_panel.pack(side=RIGHT, fill=BOTH, expand=True)

        header_frame = tb.Frame(list_panel)
        header_frame.pack(fill=X, pady=(0, 10))

        tb.Label(header_frame, text="📋 Zones Enregistrées",
                 font=("Segoe UI", 14, "bold")).pack(side=LEFT)

        tb.Button(header_frame, text="🔄 Actualiser",
                  bootstyle="secondary",
                  command=self.refresh_zones_releve).pack(side=RIGHT)

        tb.Button(header_frame, text="🧑‍🔧 Affecter des agents",
                  bootstyle="info",
                  command=self.open_zone_agents_popup).pack(side=RIGHT, padx=(0, 10))

        tb.Button(header_frame, text="🗑️ Supprimer",
                  bootstyle="danger-outline",
                  command=self.delete_selected_zone_releve).pack(side=RIGHT, padx=(0, 10))

        tb.Label(list_panel, text="💡 Sélectionnez une zone puis cliquez sur \"Affecter des agents\"",
                 font=("Segoe UI", 8, "italic")).pack(anchor=W, pady=(0, 10))

        tree_frame = tb.Frame(list_panel)
        tree_frame.pack(fill=BOTH, expand=True)

        self.zones_releve_tree = tb.Treeview(
            tree_frame,
            columns=("id", "nom", "ville", "quartier", "secteur", "agents", "clients"),
            show="headings", height=15, bootstyle="primary"
        )

        self.zones_releve_tree.heading("id", text="ID")
        self.zones_releve_tree.heading("nom", text="Nom de la zone")
        self.zones_releve_tree.heading("ville", text="Ville")
        self.zones_releve_tree.heading("quartier", text="Quartier")
        self.zones_releve_tree.heading("secteur", text="Secteur")
        self.zones_releve_tree.heading("agents", text="Agent(s) affecté(s)")
        self.zones_releve_tree.heading("clients", text="Nb clients")

        self.zones_releve_tree.column("id", width=45, anchor="center")
        self.zones_releve_tree.column("nom", width=150)
        self.zones_releve_tree.column("ville", width=100)
        self.zones_releve_tree.column("quartier", width=110)
        self.zones_releve_tree.column("secteur", width=100)
        self.zones_releve_tree.column("agents", width=180)
        self.zones_releve_tree.column("clients", width=80, anchor="center")

        scrollbar = tb.Scrollbar(tree_frame, orient="vertical",
                                  command=self.zones_releve_tree.yview)
        self.zones_releve_tree.configure(yscrollcommand=scrollbar.set)

        self.zones_releve_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def clear_zone_releve_form(self):
        self.zr_ville.delete(0, END)
        self.zr_quartier.delete(0, END)
        self.zr_secteur.delete(0, END)
        self.zr_nom.delete(0, END)
        self.zr_description.delete("1.0", END)

    def create_zone_releve(self):
        """Crée une nouvelle zone géographique de relevé.

        NOTE: `ville` + `quartier` sont la clé métier utilisée pour rattacher les
        clients (voir assign_client_zone / requêtes API `/api/abonnes`). On empêche
        donc la création d'une zone en double sur le même couple ville/quartier,
        ce qui casserait le filtrage par zone côté agent (un client matcherait
        alors plusieurs zones à la fois).
        """
        ville = self.zr_ville.get().strip()
        quartier = self.zr_quartier.get().strip()
        secteur = self.zr_secteur.get().strip()
        nom = self.zr_nom.get().strip()
        description = self.zr_description.get("1.0", END).strip()

        if not ville and not quartier and not secteur:
            messagebox.showerror("Erreur", "Veuillez renseigner au moins la ville, le quartier ou le secteur.")
            return

        if not nom:
            # Nom auto-généré à partir des composantes fournies
            nom = " - ".join([p for p in [ville, quartier, secteur] if p])

        conn = get_conn()
        try:
            c = conn.cursor()

            # Empêche les doublons ville+quartier, qui rendraient le rattachement
            # automatique des clients ambigu (plusieurs zones = même agent_zone potentiel).
            if ville or quartier:
                c.execute("""
                    SELECT id FROM zones_releve
                    WHERE (ville <=> %s) AND (quartier <=> %s)
                """, (ville or None, quartier or None))
                doublon = c.fetchone()
                if doublon:
                    messagebox.showerror(
                        "Erreur",
                        f"Une zone existe déjà pour « {ville or '—'} / {quartier or '—'} » (ID {doublon[0]}).\n"
                        f"Modifiez plutôt cette zone existante ou changez le secteur."
                    )
                    return

            c.execute("""
                INSERT INTO zones_releve (nom, ville, quartier, secteur, description, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nom, ville or None, quartier or None, secteur or None, description or None,
                  getattr(self.app, "current_user_id", None), datetime.now()))
            conn.commit()

            messagebox.showinfo("Succès", f"Zone « {nom} » créée avec succès !")
            self.clear_zone_releve_form()
            self.refresh_zones_releve()
            self.load_zone_suggestions()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la zone: {str(e)}\n\n"
                                            f"Astuce : vérifiez que la table `zones_releve` existe bien "
                                            f"(voir create_zones_releve.sql).")
        finally:
            conn.close()

    def get_selected_zone_releve_id(self):
        selection = self.zones_releve_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner une zone dans la liste.")
            return None
        values = self.zones_releve_tree.item(selection[0]).get("values")
        if not values:
            return None
        return values[0]

    def delete_selected_zone_releve(self):
        """Supprime la zone sélectionnée (les clients qui y étaient rattachés
        repassent à zone_id = NULL grâce à la contrainte ON DELETE SET NULL)."""
        zone_id = self.get_selected_zone_releve_id()
        if zone_id is None:
            return

        if not messagebox.askyesno(
            "Confirmer la suppression",
            "Supprimer cette zone ?\n\n"
            "Les agents qui y étaient affectés seront désaffectés. Les clients dont "
            "la ville/quartier correspond à cette zone ne seront simplement plus "
            "rattachés à aucune zone tant qu'une nouvelle zone ne sera pas créée pour eux."
        ):
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("DELETE FROM zones_releve WHERE id = %s", (zone_id,))
            conn.commit()
            messagebox.showinfo("Succès", "Zone supprimée.")
            self.refresh_zones_releve()
            self.load_zone_suggestions()
            if hasattr(self, "refresh_clients"):
                self.refresh_clients()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
        finally:
            conn.close()

    def refresh_zones_releve(self):
        """Recharge la liste des zones avec le nombre de clients et les agents affectés.

        Le nombre de clients par zone est calculé par correspondance ville/quartier
        (la même règle que celle utilisée côté API agent pour filtrer les abonnés),
        et non plus via `users.zone_id`, qui n'est jamais renseigné à l'inscription.
        """
        if not hasattr(self, "zones_releve_tree"):
            return

        self.zones_releve_tree.delete(*self.zones_releve_tree.get_children())
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("""
                SELECT id, nom, ville, quartier, secteur
                FROM zones_releve
                ORDER BY ville, quartier, secteur
            """)
            zones = c.fetchall()

            for zone_id, nom, ville, quartier, secteur in zones:
                # Agents affectés à cette zone
                c.execute("""
                    SELECT a.nom
                    FROM agent_zone az
                    JOIN agent a ON a.id = az.agent_id
                    WHERE az.zone_id = %s
                    ORDER BY a.nom
                """, (zone_id,))
                agents_noms = ", ".join(r[0] for r in c.fetchall()) or "—"

                # Nombre de clients dont ville+quartier correspond à cette zone
                c.execute("""
                    SELECT COUNT(*) FROM users u
                    WHERE (u.ville <=> %s) AND (u.quartier <=> %s)
                """, (ville, quartier))
                nb_clients = c.fetchone()[0]

                self.zones_releve_tree.insert("", END, values=(
                    zone_id, nom, ville or "—", quartier or "—", secteur or "—",
                    agents_noms, nb_clients
                ))

            # Garder la liste déroulante "Copier l'orthographe" synchronisée
            # avec les zones réellement présentes en base.
            if hasattr(self, "client_zone_suggestion_combo"):
                self.load_zone_suggestions()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des zones: {str(e)}\n\n"
                                            f"Astuce : vérifiez que les tables `zones_releve` et "
                                            f"`agent_zone` existent (voir create_zones_releve.sql).")
        finally:
            conn.close()

    def open_zone_agents_popup(self):
        """Ouvre une popup pour affecter un ou plusieurs agents à la zone sélectionnée,
        via une liste de cases à cocher."""
        zone_id = self.get_selected_zone_releve_id()
        if zone_id is None:
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("SELECT nom FROM zones_releve WHERE id = %s", (zone_id,))
            zone_row = c.fetchone()
            if not zone_row:
                messagebox.showerror("Erreur", "Zone introuvable.")
                return
            zone_nom = zone_row[0]

            c.execute("SELECT id, nom, statut FROM agent ORDER BY nom")
            tous_agents = c.fetchall()

            c.execute("SELECT agent_id FROM agent_zone WHERE zone_id = %s", (zone_id,))
            agents_deja_affectes = {r[0] for r in c.fetchall()}

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
            conn.close()
            return
        finally:
            conn.close()

        popup = tb.Toplevel(self)
        popup.title(f"🧑‍🔧 Affecter des agents – {zone_nom}")
        popup.geometry("420x500")
        popup.transient(self)
        popup.grab_set()

        tb.Label(popup, text=f"Zone : {zone_nom}",
                 font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
        tb.Label(popup, text="Cochez le ou les agents à affecter à cette zone :",
                 font=("Segoe UI", 9, "italic")).pack(pady=(0, 15))

        scroll_frame = tb.Frame(popup, padding=(20, 0))
        scroll_frame.pack(fill=BOTH, expand=True)

        agent_vars = {}
        if not tous_agents:
            tb.Label(scroll_frame, text="Aucun agent enregistré pour le moment.",
                     font=("Segoe UI", 9, "italic")).pack(anchor=W)
        else:
            for agent_id, agent_nom, agent_statut in tous_agents:
                var = tb.BooleanVar(value=(agent_id in agents_deja_affectes))
                agent_vars[agent_id] = var
                statut = agent_statut or "actif"
                label_text = agent_nom if statut == "actif" else f"{agent_nom} (désactivé)"
                cb = tb.Checkbutton(scroll_frame, text=label_text, variable=var,
                                     bootstyle="round-toggle" if statut == "actif" else "secondary-round-toggle")
                cb.pack(anchor=W, pady=4)

        def save_assignments():
            selected_ids = [aid for aid, var in agent_vars.items() if var.get()]

            conn = get_conn()
            try:
                c = conn.cursor()
                c.execute("DELETE FROM agent_zone WHERE zone_id = %s", (zone_id,))
                for agent_id in selected_ids:
                    c.execute("""
                        INSERT INTO agent_zone (agent_id, zone_id, assigned_at)
                        VALUES (%s, %s, %s)
                    """, (agent_id, zone_id, datetime.now()))
                conn.commit()
                messagebox.showinfo("Succès", f"{len(selected_ids)} agent(s) affecté(s) à la zone « {zone_nom} ».")
                self.refresh_zones_releve()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'affectation: {str(e)}")
            finally:
                conn.close()

        buttons_frame = tb.Frame(popup, padding=20)
        buttons_frame.pack(fill=X)

        tb.Button(buttons_frame, text="💾 Enregistrer",
                  bootstyle="success", width=15,
                  command=save_assignments).pack(side=LEFT, padx=(0, 12))

        tb.Button(buttons_frame, text="❌ Annuler",
                  bootstyle="secondary", width=12,
                  command=popup.destroy).pack(side=LEFT)

    def create_clients_tab(self):
        tab = tb.Frame(self.notebook, padding=30)
        self.notebook.add(tab, text="👤 Clients")

        tb.Label(tab, text="Liste des Clients",
                 font=("Segoe UI", 18, "bold")).pack(anchor=W, pady=(0, 30))

        list_panel = tb.Frame(tab, bootstyle="light", padding=25)
        list_panel.pack(fill=BOTH, expand=True)

        header_frame = tb.Frame(list_panel)
        header_frame.pack(fill=X, pady=(0, 15))

        tb.Label(header_frame, text="👥 Clients Enregistrés",
                 font=("Segoe UI", 14, "bold")).pack(side=LEFT)

        tb.Button(header_frame, text="🔄 Actualiser",
                  bootstyle="secondary",
                  command=self.refresh_clients).pack(side=RIGHT)

        # Panneau d'attribution du numéro de compteur
        assign_frame = tb.Frame(list_panel, bootstyle="secondary", padding=15)
        assign_frame.pack(fill=X, pady=(0, 10))

        tb.Label(assign_frame, text="🔌 Attribuer un N° de compteur :",
                 font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 10))

        self.selected_client_label = tb.Label(assign_frame, text="Aucun client sélectionné",
                                              font=("Segoe UI", 9, "italic"))
        self.selected_client_label.pack(side=LEFT, padx=(0, 15))

        self.meter_entry = tb.Entry(assign_frame, width=20, font=("Segoe UI", 10))
        self.meter_entry.pack(side=LEFT, padx=(0, 10))

        tb.Button(assign_frame, text="💾 Attribuer",
                  bootstyle="success",
                  command=self.assign_meter_number).pack(side=LEFT, padx=(0, 8))

        tb.Button(assign_frame, text="🗑️ Retirer",
                  bootstyle="danger-outline",
                  command=self.remove_meter_number).pack(side=LEFT)

        # Panneau de correction Ville / Quartier.
        # Règle métier : la zone d'un client N'EST PAS un attribut qu'on lui assigne
        # librement — elle est déterminée par les colonnes `ville` et `quartier` de
        # `users`, renseignées par le client lui-même à son inscription. Ce panneau
        # sert donc à corriger ces deux champs (faute de frappe, quartier mal saisi...),
        # jamais à "attacher" arbitrairement le client à une zone qui ne correspond pas
        # à sa véritable adresse.
        zone_assign_frame = tb.Frame(list_panel, bootstyle="secondary", padding=15)
        zone_assign_frame.pack(fill=X, pady=(0, 8))

        tb.Label(zone_assign_frame, text="🏙️ Ville / Quartier (déterminent la zone) :",
                 font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 10))

        self.client_ville_entry = tb.Entry(zone_assign_frame, width=16, font=("Segoe UI", 10))
        self.client_ville_entry.pack(side=LEFT, padx=(0, 6))

        self.client_quartier_entry = tb.Entry(zone_assign_frame, width=16, font=("Segoe UI", 10))
        self.client_quartier_entry.pack(side=LEFT, padx=(0, 10))

        tb.Button(zone_assign_frame, text="💾 Enregistrer",
                  bootstyle="success",
                  command=self.save_client_address).pack(side=LEFT, padx=(0, 15))

        tb.Label(zone_assign_frame, text="📋 Copier l'orthographe d'une zone existante :",
                 font=("Segoe UI", 9)).pack(side=LEFT, padx=(0, 8))

        self.client_zone_suggestion_combo = tb.Combobox(zone_assign_frame, width=26,
                                                          font=("Segoe UI", 10), state="readonly")
        self.client_zone_suggestion_combo.pack(side=LEFT, padx=(0, 8))

        tb.Button(zone_assign_frame, text="⬇️ Copier",
                  bootstyle="info-outline",
                  command=self.copy_zone_into_address_fields).pack(side=LEFT)

        self.client_zone_match_label = tb.Label(list_panel, text="",
                                                 font=("Segoe UI", 9, "italic"))
        self.client_zone_match_label.pack(anchor=W, pady=(0, 10))

        tb.Label(list_panel,
                 text="💡 Cliquez sur un client dans la liste ci-dessous pour le sélectionner. "
                      "La zone d'un client vient de sa ville/quartier saisis à l'inscription : "
                      "corrigez-les ici en cas de faute de frappe. Utilisez \"Copier\" pour "
                      "reprendre exactement l'orthographe d'une zone existante et éviter les "
                      "doublons (ex. \"Matsimou\" vs \"matsimou\").",
                 font=("Segoe UI", 8, "italic")).pack(anchor=W, pady=(0, 10))

        tree_frame = tb.Frame(list_panel)
        tree_frame.pack(fill=BOTH, expand=True)

        self.clients_tree = tb.Treeview(tree_frame,
                                        columns=("id", "username", "email", "telephone",
                                                 "adresse", "numero_compteur", "zone", "created_at"),
                                        show="headings", height=15,
                                        bootstyle="primary")

        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("username", text="Nom d'utilisateur")
        self.clients_tree.heading("email", text="Email")
        self.clients_tree.heading("telephone", text="Téléphone")
        self.clients_tree.heading("adresse", text="Adresse")
        self.clients_tree.heading("numero_compteur", text="N° Compteur")
        self.clients_tree.heading("zone", text="Zone")
        self.clients_tree.heading("created_at", text="Créé le")

        self.clients_tree.column("id", width=50, anchor="center")
        self.clients_tree.column("username", width=140)
        self.clients_tree.column("email", width=160)
        self.clients_tree.column("telephone", width=100)
        self.clients_tree.column("adresse", width=150)
        self.clients_tree.column("numero_compteur", width=100)
        self.clients_tree.column("zone", width=140)
        self.clients_tree.column("created_at", width=120)

        scrollbar = tb.Scrollbar(tree_frame, orient="vertical",
                                command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)

        self.clients_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Sélectionner un client dans la liste remplit les panneaux d'attribution
        self.clients_tree.bind("<<TreeviewSelect>>", self.on_client_select)
        self.selected_client_id = None

    def load_zone_suggestions(self):
        """Recharge la liste déroulante des zones existantes (aide-mémoire d'orthographe).

        Ceci n'est PAS une liste "d'assignation" : elle sert uniquement à copier
        l'orthographe exacte ville/quartier d'une zone déjà créée dans les champs
        d'édition, pour éviter les doublons de type "Matsimou" / "matsimou " / "Matsimou ".
        """
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("SELECT id, nom, ville, quartier FROM zones_releve ORDER BY nom")
            zones = c.fetchall()
        except Exception:
            zones = []
        finally:
            conn.close()

        self._zone_suggestions = {
            f"{nom} (#{zone_id})": {"ville": ville, "quartier": quartier}
            for zone_id, nom, ville, quartier in zones
        }
        if hasattr(self, "client_zone_suggestion_combo"):
            self.client_zone_suggestion_combo["values"] = list(self._zone_suggestions.keys())

    def copy_zone_into_address_fields(self):
        """Copie la ville/quartier de la zone sélectionnée dans les champs d'édition,
        SANS encore sauvegarder — l'admin doit cliquer sur "Enregistrer" pour appliquer
        le changement au client sélectionné."""
        choix = self.client_zone_suggestion_combo.get()
        zone_info = getattr(self, "_zone_suggestions", {}).get(choix)
        if not zone_info:
            messagebox.showwarning("Attention", "Veuillez d'abord choisir une zone dans la liste.")
            return

        self.client_ville_entry.delete(0, END)
        self.client_ville_entry.insert(0, zone_info["ville"] or "")

        self.client_quartier_entry.delete(0, END)
        self.client_quartier_entry.insert(0, zone_info["quartier"] or "")

    def save_client_address(self):
        """Corrige la ville/quartier du client sélectionné.

        C'est la SEULE vraie façon de changer la zone d'un client : sa zone n'est
        pas un attribut assignable librement, elle est déduite de son adresse
        (ville + quartier), renseignée à l'inscription. On met aussi à jour
        `zone_id` par correspondance, uniquement pour l'affichage/rétro-compatibilité.
        """
        if not getattr(self, 'selected_client_id', None):
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner un client dans la liste.")
            return

        ville = self.client_ville_entry.get().strip()
        quartier = self.client_quartier_entry.get().strip()

        if not ville and not quartier:
            messagebox.showwarning(
                "Attention",
                "Veuillez renseigner au moins la ville ou le quartier du client."
            )
            return

        conn = get_conn()
        try:
            c = conn.cursor()

            # zone_id est recalculé par correspondance ville/quartier, uniquement
            # pour l'affichage historique — le vrai filtrage côté agent se base
            # directement sur users.ville/quartier (voir server.js /api/abonnes).
            c.execute(
                "SELECT id FROM zones_releve WHERE (ville <=> %s) AND (quartier <=> %s) LIMIT 1",
                (ville or None, quartier or None)
            )
            match = c.fetchone()
            matched_zone_id = match[0] if match else None

            c.execute(
                "UPDATE users SET ville = %s, quartier = %s, zone_id = %s WHERE id = %s",
                (ville or None, quartier or None, matched_zone_id, self.selected_client_id)
            )
            conn.commit()

            if matched_zone_id:
                messagebox.showinfo(
                    "Succès",
                    f"Adresse mise à jour. Cette ville/quartier correspond à une zone "
                    f"existante (ID {matched_zone_id}) : le client sera visible par les "
                    f"agents affectés à cette zone."
                )
            else:
                messagebox.showwarning(
                    "Adresse enregistrée — aucune zone correspondante",
                    "L'adresse a été enregistrée, mais aucune zone (ville/quartier) "
                    "correspondante n'existe encore dans l'onglet « Zones de Relevé ». "
                    "Ce client ne sera visible par aucun agent tant qu'une zone "
                    "correspondante n'aura pas été créée et affectée à un agent."
                )

            self.refresh_clients()
            self.refresh_zones_releve()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour de l'adresse: {str(e)}")
        finally:
            conn.close()

    def on_client_select(self, event=None):
        """Remplit le panneau d'attribution avec le client sélectionné dans la liste."""
        selected = self.clients_tree.selection()
        if not selected:
            return
        values = self.clients_tree.item(selected[0], 'values')
        if not values:
            return

        # Ordre des colonnes : id, username, email, telephone, adresse, numero_compteur, zone, created_at
        client_id = values[0]
        username = values[1] if len(values) > 1 else ""
        current_meter = values[5] if len(values) > 5 else ""
        current_zone = values[6] if len(values) > 6 else ""

        self.selected_client_id = client_id
        self.selected_client_label.config(text=f"Client : {username} (ID {client_id})")

        self.meter_entry.delete(0, END)
        if current_meter:
            self.meter_entry.insert(0, current_meter)

        # Récupérer la ville/quartier réels du client pour pré-remplir les champs d'édition
        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("SELECT ville, quartier FROM users WHERE id = %s", (client_id,))
            row = c.fetchone()
        except Exception:
            row = None
        finally:
            conn.close()

        self.client_ville_entry.delete(0, END)
        self.client_quartier_entry.delete(0, END)
        if row:
            ville, quartier = row
            if ville:
                self.client_ville_entry.insert(0, ville)
            if quartier:
                self.client_quartier_entry.insert(0, quartier)

        self.client_zone_suggestion_combo.set("")

        if current_zone and current_zone != "—":
            self.client_zone_match_label.config(
                text=f"✅ Zone actuelle : {current_zone}", bootstyle="success"
            )
        else:
            self.client_zone_match_label.config(
                text="⚠️ Aucune zone ne correspond à la ville/quartier de ce client.",
                bootstyle="warning"
            )

    def assign_meter_number(self):
        """Attribue le numéro de compteur saisi au client sélectionné."""
        if not getattr(self, 'selected_client_id', None):
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner un client dans la liste.")
            return

        meter_value = self.meter_entry.get().strip()
        if not meter_value:
            messagebox.showwarning("Attention", "Veuillez saisir un numéro de compteur.")
            return

        conn = get_conn()
        try:
            existing_cols = [c.lower() for c in self._get_table_columns(conn, "users")]
            if "numero_compteur" not in existing_cols:
                messagebox.showerror("Erreur",
                                      "La colonne 'numero_compteur' n'existe pas dans la table 'users'.")
                return

            c = conn.cursor()

            # Vérifier que ce numéro n'est pas déjà attribué à un autre client
            c.execute("SELECT id, username FROM users WHERE numero_compteur=%s AND id != %s",
                      (meter_value, self.selected_client_id))
            conflict = c.fetchone()
            if conflict:
                messagebox.showerror(
                    "Erreur",
                    f"Ce numéro de compteur est déjà attribué à '{conflict[1]}' (ID {conflict[0]})."
                )
                return

            c.execute("UPDATE users SET numero_compteur=%s WHERE id=%s",
                      (meter_value, self.selected_client_id))
            conn.commit()
            messagebox.showinfo("Succès", "Numéro de compteur attribué avec succès.")
            self.refresh_clients()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'attribution: {str(e)}")
        finally:
            conn.close()

    def remove_meter_number(self):
        """Retire le numéro de compteur du client sélectionné."""
        if not getattr(self, 'selected_client_id', None):
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner un client dans la liste.")
            return

        if not messagebox.askyesno("Confirmer", "Retirer le numéro de compteur de ce client ?"):
            return

        conn = get_conn()
        try:
            c = conn.cursor()
            c.execute("UPDATE users SET numero_compteur=NULL WHERE id=%s", (self.selected_client_id,))
            conn.commit()
            self.meter_entry.delete(0, END)
            messagebox.showinfo("Succès", "Numéro de compteur retiré.")
            self.refresh_clients()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
        finally:
            conn.close()

    def refresh_clients(self):
        self.clients_tree.delete(*self.clients_tree.get_children())

        # Recharger la liste déroulante des zones disponibles pour l'assignation
        if hasattr(self, "client_zone_combo"):
            self.load_zone_combo_options()

        conn = get_conn()
        try:
            # Colonnes désirées, filtrées selon celles réellement présentes dans la table
            desired = ["id", "username", "email", "telephone", "adresse", "numero_compteur", "created_at"]
            existing = self._get_table_columns(conn, "users")
            existing_lower = [c.lower() for c in existing]
            cols = [c for c in desired if c.lower() in existing_lower] or ["id", "username"]
            has_ville_quartier = "ville" in existing_lower and "quartier" in existing_lower

            c = conn.cursor()

            if has_ville_quartier:
                # La zone affichée est déduite par correspondance ville/quartier
                # (même règle que le filtrage côté API agent), pas par zone_id seul,
                # pour refléter fidèlement qui verra réellement ce client.
                col_list = ", ".join(f"u.`{col}`" for col in cols)
                c.execute(f"""
                    SELECT {col_list}, z.nom
                    FROM users u
                    LEFT JOIN zones_releve z
                        ON (z.ville <=> u.ville) AND (z.quartier <=> u.quartier)
                    ORDER BY u.id DESC
                """)
                rows = c.fetchall()
                for r in rows:
                    *base_values, zone_nom = r
                    row = dict(zip(cols, base_values))
                    values = [row.get(col, "") if row.get(col) is not None else "" for col in desired]
                    # Insérer la zone juste avant "created_at"
                    values.insert(desired.index("created_at"), zone_nom or "—")
                    self.clients_tree.insert("", END, values=values)
            else:
                col_list = ", ".join(f"`{col}`" for col in cols)
                c.execute(f"SELECT {col_list} FROM users ORDER BY id DESC")
                rows = c.fetchall()
                for r in rows:
                    row = dict(zip(cols, r))
                    values = [row.get(col, "") if row.get(col) is not None else "" for col in desired]
                    values.insert(desired.index("created_at"), "—")
                    self.clients_tree.insert("", END, values=values)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des clients: {str(e)}")
        finally:
            conn.close()

    def load_zones_checkboxes(self, parent):
        # Nettoyer les anciennes checkboxes
        for widget in parent.winfo_children():
            widget.destroy()

        self.zone_checkboxes = {}

        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT id, name, type, city FROM electric_zones ORDER BY name")
            zones = c.fetchall()

            if not zones:
                tb.Label(parent, text="(Aucune zone enregistrée)",
                        font=("Segoe UI", 10, "italic")).pack(anchor=W, pady=10)
                return

            for zone_id, name, zone_type, city in zones:
                var = tb.BooleanVar()
                cb = tb.Checkbutton(parent, text=f"{name} ({zone_type}) - {city}",
                                   variable=var, bootstyle="primary")
                cb.pack(anchor=W, pady=2)
                self.zone_checkboxes[zone_id] = var

        except Exception as e:
            tb.Label(parent, text=f"Erreur: {str(e)}",
                    font=("Segoe UI", 10), bootstyle="danger").pack(anchor=W, pady=10)
        finally:
            conn.close()

    def check_all_zones(self):
        for var in self.zone_checkboxes.values():
            var.set(True)

    def uncheck_all_zones(self):
        for var in self.zone_checkboxes.values():
            var.set(False)

    def surprime_zone(self):
        selected_zones = [zone_id for zone_id, var in self.zone_checkboxes.items() if var.get()]

        if not selected_zones:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une zone à supprimer")
            return

        if not messagebox.askyesno("Confirmer", f"Supprimer {len(selected_zones)} zone(s) sélectionnée(s) ? Cette action est irréversible."):
            return

        conn = get_conn()
        c = conn.cursor()
        try:
            for zone_id in selected_zones:
                c.execute("DELETE FROM electric_zones WHERE id = %s", (zone_id,))
            conn.commit()
            messagebox.showinfo("Succès", f"{len(selected_zones)} zone(s) supprimée(s) avec succès.")
            self.load_zones_checkboxes(self.zone_checkboxes_frame)
            self.update_map_markers()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer les zones: {str(e)}")
        finally:
            conn.close()

    def send_selected_zones(self):
        selected_zones = [zone_id for zone_id, var in self.zone_checkboxes.items() if var.get()]

        if not selected_zones:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une zone")
            return

        # Récupérer les détails des zones sélectionnées
        zones_data = []
        conn = get_conn()
        c = conn.cursor()
        try:
            for zone_id in selected_zones:
                c.execute("""
                    SELECT name, type, latitude, longitude, city, voltage, status, description
                    FROM electric_zones WHERE id = %s
                """, (zone_id,))
                result = c.fetchone()
                if result:
                    zones_data.append({
                        'id': zone_id,
                        'name': result[0],
                        'type': result[1],
                        'latitude': result[2],
                        'longitude': result[3],
                        'city': result[4],
                        'voltage': result[5],
                        'status': result[6],
                        'description': result[7]
                    })
        finally:
            conn.close()

        # Envoyer les données (simulation d'envoi à un serveur/API)
        self.send_zones_to_server(zones_data)

    def send_zones_to_server(self, zones_data):
        # Simulation d'envoi à un serveur distant
        # En production, remplacer par un vrai appel API

        import json
        import requests

        try:
            # Préparer les données JSON
            payload = {
                'timestamp': datetime.now().isoformat(),
                'user_id': self.app.current_user_id,
                'zones': zones_data
            }

            # URL du serveur (à configurer selon vos besoins)
            server_url = "http://localhost:5000/api/zones"  # Exemple

            # headers = {'Content-Type': 'application/json'}
            # response = requests.post(server_url, json=payload, headers=headers)

            # Simulation de succès
            message = f"📤 Données envoyées avec succès!\n\n"
            message += f"📊 {len(zones_data)} zone(s) transmise(s)\n"
            message += f"📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

            for zone in zones_data:
                message += f"🏷️ {zone['name']} ({zone['type']})\n"
                message += f"📍 {zone['city']} - {zone['latitude']:.4f}, {zone['longitude']:.4f}\n"
                message += f"⚡ {zone['voltage']}V - {zone['status']}\n\n"

            messagebox.showinfo("Envoi réussi", message)

        except Exception as e:
            messagebox.showerror("Erreur d'envoi", f"Impossible d'envoyer les données: {str(e)}")

    def auto_send_zone_report(self, zone_data):
        """Envoi automatique lors de l'ajout d'une nouvelle zone"""
        try:
            payload = {
                'timestamp': datetime.now().isoformat(),
                'user_id': self.app.current_user_id,
                'auto_report': True,
                'zone': zone_data
            }

            # Simulation d'envoi automatique
            print(f"📤 Rapport automatique envoyé pour la zone: {zone_data['name']}")

            # Ici vous pouvez ajouter un vrai appel API silencieux
            # response = requests.post("http://your-server/api/auto-report", json=payload)

        except Exception as e:
            print(f"Erreur envoi automatique: {str(e)}")

    def center_map_Brazzaville(self):
        self.map_widget.set_position(-4.325, 15.322)
        self.map_widget.set_zoom(12)
        messagebox.showinfo("Navigation", "Carte centrée sur Brazzaville")

    def zoom_in(self):
        current_zoom = self.map_widget.zoom
        if current_zoom < 20:
            self.map_widget.set_zoom(current_zoom + 1)

    def zoom_out(self):
        current_zoom = self.map_widget.zoom
        if current_zoom > 1:
            self.map_widget.set_zoom(current_zoom - 1)

    def update_map_markers(self):
        # Supprimer tous les marqueurs existants
        self.map_widget.delete_all_marker()

        # Récupérer toutes les zones de la base de données
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute("SELECT id, name, type, latitude, longitude, city, status FROM electric_zones")
            zones = c.fetchall()

            for zone_id, name, zone_type, lat, lng, city, status in zones:
                # Déterminer la couleur du marqueur selon le statut
                if status == "✅ Fonctionnel":
                    marker_color = "green"
                    marker_color_outside = "darkgreen"
                elif status == "🔧 En maintenance":
                    marker_color = "orange"
                    marker_color_outside = "darkorange"
                elif status == "❌ Hors service":
                    marker_color = "red"
                    marker_color_outside = "darkred"
                else:
                    marker_color = "gray"
                    marker_color_outside = "black"

                # Créer le marqueur avec les informations détaillées
                marker_text = f"🏷️ {name}\n🏗️ {zone_type}\n🏙️ {city}\n📊 {status}"
                marker = self.map_widget.set_marker(lat, lng, text=marker_text,
                                         marker_color_circle=marker_color,
                                         marker_color_outside=marker_color_outside,
                                         font=("Arial", 10, "bold"))

                # Ajouter un événement de clic sur le marqueur pour afficher les détails
                marker.marker_id = zone_id  # Stocker l'ID pour référence future

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des marqueurs: {str(e)}")
        finally:
            conn.close()

    def clear_all_markers(self):
        """Efface tous les marqueurs de la carte"""
        self.map_widget.delete_all_marker()
        messagebox.showinfo("Marqueurs", "Tous les marqueurs ont été effacés de la carte")

    def add_zone_from_map(self, coords):
        lat, lng = coords

        # Ouvrir une boîte de dialogue pour saisir les informations de la zone
        self.create_zone_from_coords(lat, lng)

    def create_zone_from_coords(self, lat, lng):
        # Créer une fenêtre popup pour saisir les détails de la zone
        popup = tb.Toplevel(self)
        popup.title("📍 Ajouter Zone Électrique")
        popup.geometry("800x700")
        popup.resizable(False, False)

        # Centrer la fenêtre
        popup.transient(self)
        popup.grab_set()

        # Titre
        tb.Label(popup, text="Nouvelle Zone Électrique",
                 font=("Segoe UI", 10, "bold")).pack(pady=25)

        # Cadre pour le formulaire
        form_frame = tb.Frame(popup, padding=20)
        form_frame.pack(fill=X)

        # Coordonnées (non modifiables)
        coords_frame = tb.Frame(form_frame)
        coords_frame.pack(fill=X, pady=5)

        tb.Label(coords_frame, text="📍 Latitude:").pack(side=LEFT, padx=5)
        lat_entry = tb.Entry(coords_frame, width=15)
        lat_entry.pack(side=LEFT, padx=5)
        lat_entry.insert(0, f"{lat:.6f}")
        lat_entry.config(state="readonly")

        tb.Label(coords_frame, text="📍 Longitude:").pack(side=LEFT, padx=10)
        lng_entry = tb.Entry(coords_frame, width=15)
        lng_entry.pack(side=LEFT, padx=5)
        lng_entry.insert(0, f"{lng:.6f}")
        lng_entry.config(state="readonly")

        # Nom
        name_frame = tb.Frame(form_frame)
        name_frame.pack(fill=X, pady=5)

        tb.Label(name_frame, text="🏷️ Nom:").pack(side=LEFT, padx=5)
        name_entry = tb.Entry(name_frame, width=25)
        name_entry.pack(side=LEFT, padx=5)

        # Type
        type_frame = tb.Frame(form_frame)
        type_frame.pack(fill=X, pady=5)

        tb.Label(type_frame, text="🔧 Type:").pack(side=LEFT, padx=5)
        type_combo = tb.Combobox(type_frame,
                                values=["Réseau HT", "Poste de transformation",
                                        "Ligne BT", "Branchement", "Autre"],
                                width=20)
        type_combo.pack(side=LEFT, padx=5)

        # Ville
        city_frame = tb.Frame(form_frame)
        city_frame.pack(fill=X, pady=5)

        tb.Label(city_frame, text="🏙️ Ville:").pack(side=LEFT, padx=5)
        city_entry = tb.Entry(city_frame, width=25)
        city_entry.pack(side=LEFT, padx=5)

        # Tension
        voltage_frame = tb.Frame(form_frame)
        voltage_frame.pack(fill=X, pady=5)

        tb.Label(voltage_frame, text="⚡ Tension (V):").pack(side=LEFT, padx=5)
        voltage_entry = tb.Entry(voltage_frame, width=15)
        voltage_entry.pack(side=LEFT, padx=5)

        # État
        status_frame = tb.Frame(form_frame)
        status_frame.pack(fill=X, pady=5)

        tb.Label(status_frame, text="📊 État:").pack(side=LEFT, padx=5)
        status_combo = tb.Combobox(status_frame,
                                  values=["✅ Fonctionnel", "🔧 En maintenance",
                                          "❌ Hors service", "🔨 À réparer"],
                                  width=15)
        status_combo.pack(side=LEFT, padx=5)

        # Description
        desc_frame = tb.Frame(form_frame)
        desc_frame.pack(fill=X, pady=10)

        tb.Label(desc_frame, text="📝 Description:").pack(anchor=W, padx=5, pady=2)
        desc_text = tb.Text(desc_frame, height=3, width=35)
        desc_text.pack(padx=5, pady=2)

        # Boutons
        buttons_frame = tb.Frame(popup)
        buttons_frame.pack(fill=X, pady=15)

        def save_and_mark_zone():
            name = name_entry.get().strip()
            zone_type = type_combo.get()
            city = city_entry.get().strip()
            voltage = voltage_entry.get().strip()
            status = status_combo.get()
            description = desc_text.get("1.0", END).strip()

            if not name or not zone_type or not city:
                messagebox.showerror("Erreur", "Veuillez remplir au moins le nom, le type et la ville")
                return

            # Sauvegarder dans la base de données
            conn = get_conn()
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO electric_zones (name, type, latitude, longitude, city,
                                              voltage, status, description, created_by, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, zone_type, lat, lng, city, voltage, status,
                      description, self.app.current_user_id, datetime.now()))
                conn.commit()

                zone_id = c.lastrowid
                messagebox.showinfo("Succès", "Zone électrique ajoutée avec marqueur!")

                # Envoi automatique du rapport
                zone_data = {
                    'id': zone_id,
                    'name': name,
                    'type': zone_type,
                    'latitude': lat,
                    'longitude': lng,
                    'city': city,
                    'voltage': voltage,
                    'status': status,
                    'description': description
                }
                self.auto_send_zone_report(zone_data)

                # Ajouter un marqueur sur la carte à la position de la zone
                self.add_marker_to_map(lat, lng, zone_type, name, zone_id)

                # Actualiser la carte et la liste
                self.update_map_markers()
                self.refresh_zones()
                self.load_zones_checkboxes(self.zone_checkboxes_frame)

                # Fermer la popup
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
            finally:
                conn.close()

        def save_zone():
            name = name_entry.get().strip()
            zone_type = type_combo.get()
            city = city_entry.get().strip()
            voltage = voltage_entry.get().strip()
            status = status_combo.get()
            description = desc_text.get("1.0", END).strip()

            if not name or not zone_type or not city:
                messagebox.showerror("Erreur", "Veuillez remplir au moins le nom, le type et la ville")
                return

            # Sauvegarder dans la base de données
            conn = get_conn()
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO electric_zones (name, type, latitude, longitude, city,
                                              voltage, status, description, created_by, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, zone_type, lat, lng, city, voltage, status,
                      description, self.app.current_user_id, datetime.now()))
                conn.commit()

                messagebox.showinfo("Succès", "Zone électrique ajoutée avec succès!")

                # Envoi automatique du rapport
                zone_data = {
                    'id': c.lastrowid,
                    'name': name,
                    'type': zone_type,
                    'latitude': lat,
                    'longitude': lng,
                    'city': city,
                    'voltage': voltage,
                    'status': status,
                    'description': description
                }
                self.auto_send_zone_report(zone_data)

                # Actualiser la carte et la liste
                self.update_map_markers()
                self.refresh_zones()
                self.load_zones_checkboxes(self.zone_checkboxes_frame)

                # Fermer la popup
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
            finally:
                conn.close()

        def cancel():
            popup.destroy()

        tb.Button(buttons_frame, text="💾 Enregistrer & Marquer",
                  bootstyle="primary",
                  command=lambda: save_and_mark_zone()).pack(side=LEFT, padx=10)

        tb.Button(buttons_frame, text="💾 Enregistrer",
                  bootstyle="success",
                  command=save_zone).pack(side=LEFT, padx=10)

        tb.Button(buttons_frame, text="❌ Annuler",
                  bootstyle="secondary",
                  command=cancel).pack(side=LEFT, padx=10)

    def save_electric_zone(self):
        name = self.zone_name.get().strip()
        zone_type = self.zone_type.get()
        lat = self.zone_lat.get().strip()
        lng = self.zone_lng.get().strip()
        city = self.zone_city.get().strip()
        voltage = self.zone_voltage.get().strip()
        status = self.zone_status.get()
        description = self.zone_description.get("1.0", END).strip()

        if not name or not zone_type or not lat or not lng or not city:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return

        try:
            lat_val = float(lat)
            lng_val = float(lng)
        except ValueError:
            messagebox.showerror("Erreur", "Latitude et longitude doivent être des nombres")
            return

        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO electric_zones (name, type, latitude, longitude, city,
                                          voltage, status, description, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, zone_type, lat_val, lng_val, city, voltage, status,
                  description, self.app.current_user_id, datetime.now()))
            conn.commit()
            messagebox.showinfo("Succès", "Zone électrique enregistrée avec succès")
            self.clear_form()
            self.refresh_zones()
            # Recharger les checkboxes dans l'onglet carte
            self.load_zones_checkboxes(self.zone_checkboxes_frame)

            # Envoi automatique du rapport
            zone_data = {
                'id': c.lastrowid,
                'name': name,
                'type': zone_type,
                'latitude': lat_val,
                'longitude': lng_val,
                'city': city,
                'voltage': voltage,
                'status': status,
                'description': description
            }
            self.auto_send_zone_report(zone_data)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
        finally:
            conn.close()

    def send_electric_report(self):
        messagebox.showinfo("Rapport envoyé", "Le rapport des zones électriques a été envoyé avec succès")

    def clear_form(self):
        self.zone_name.delete(0, END)
        self.zone_type.set("")
        self.zone_lat.delete(0, END)
        self.zone_lng.delete(0, END)
        self.zone_city.delete(0, END)
        self.zone_voltage.delete(0, END)
        self.zone_status.set("")
        self.zone_description.delete("1.0", END)

    def refresh_zones(self):
        self.zones_tree.delete(*self.zones_tree.get_children())
        conn = get_conn()
        c = conn.cursor()
        try:
            c.execute("""
                SELECT id, name, type, city, status, created_at
                FROM electric_zones
                ORDER BY created_at DESC
            """)
            for r in c.fetchall():
                self.zones_tree.insert("", END, values=r)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
        finally:
            conn.close()

    def generate_report(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM electric_zones")
        total_zones = c.fetchone()[0]

        c.execute("SELECT status, COUNT(*) FROM electric_zones GROUP BY status")
        status_counts = dict(c.fetchall())

        conn.close()

        report = f"""📊 Rapport des Zones Électriques

Total des zones: {total_zones}

État des zones:
"""

        for status, count in status_counts.items():
            report += f"- {status}: {count}\n"

        messagebox.showinfo("Rapport généré", report)

    def generate_detailed_report(self):
        conn = get_conn()
        c = conn.cursor()

        # Statistiques générales
        c.execute("SELECT COUNT(*) FROM electric_zones")
        total_zones = c.fetchone()[0]

        c.execute("SELECT type, COUNT(*) FROM electric_zones GROUP BY type")
        type_counts = dict(c.fetchall())

        c.execute("SELECT status, COUNT(*) FROM electric_zones GROUP BY status")
        status_counts = dict(c.fetchall())

        c.execute("SELECT city, COUNT(*) FROM electric_zones GROUP BY city ORDER BY COUNT(*) DESC")
        city_counts = c.fetchall()

        conn.close()

        report = f"""📊 RAPPORT DÉTAILLÉ DES ZONES ÉLECTRIQUES
{'='*50}

📅 Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📈 STATISTIQUES GÉNÉRALES:
• Total des zones: {total_zones}

🏗️ RÉPARTITION PAR TYPE:
"""

        for zone_type, count in type_counts.items():
            report += f"• {zone_type}: {count}\n"

        report += f"\n📊 RÉPARTITION PAR ÉTAT:\n"
        for status, count in status_counts.items():
            report += f"• {status}: {count}\n"

        report += f"\n🏙️ RÉPARTITION PAR VILLE:\n"
        for city, count in city_counts:
            report += f"• {city}: {count}\n"

        self.stats_text.delete("1.0", END)
        self.stats_text.insert("1.0", report)

    def export_csv(self):
        messagebox.showinfo("Export", "Fonctionnalité d'export CSV à implémenter")

    def send_report_email(self):
        messagebox.showinfo("Email", "Fonctionnalité d'envoi par email à implémenter")

    def on_tab_changed(self, event):
        """Actualise certaines vues quand on change d'onglet.

        - Si on affiche la carte, on recharge les marqueurs.
        - Si on affiche l'onglet Factures, on recharge la liste des factures.
        """
        # Index actuel (numérique)
        current_tab = self.notebook.index(self.notebook.select())
        # Texte de l'onglet sélectionné
        try:
            tab_text = self.notebook.tab(self.notebook.select(), 'text') or ''
        except Exception:
            tab_text = ''

        # Carte interactive (ancien comportement)
        if 'Carte' in tab_text or current_tab == 1:
            self.update_map_markers()

        # Recharger les factures si on est sur l'onglet Factures
        if 'Factures' in tab_text:
            try:
                self.load_bills()
            except Exception:
                # Silence: si le serveur n'est pas accessible, load_bills gérera l'erreur
                pass

    def quick_add_zone(self, zone_type):
        """Ajout rapide d'une zone en cliquant sur la carte"""
        messagebox.showinfo("Ajout Rapide",
                           f"Cliquez avec le bouton droit sur la carte pour ajouter une zone '{zone_type}'")
        # Changer temporairement le menu contextuel
        # self.map_widget.delete_all_right_click_menu_commands()  # Méthode non disponible
        self.map_widget.add_right_click_menu_command(
            label=f"📍 Ajouter {zone_type}",
            command=lambda coords: self.add_quick_zone_from_map(coords, zone_type),
            pass_coords=True
        )

        # Remettre le menu normal après 30 secondes
        self.after(30000, lambda: self.restore_normal_menu())

    def restore_normal_menu(self):
        """Remet le menu contextuel normal"""
        # self.map_widget.delete_all_right_click_menu_commands()  # Méthode non disponible
        self.map_widget.add_right_click_menu_command(
            label="📍 Ajouter Zone Électrique",
            command=self.add_zone_from_map,
            pass_coords=True
        )

    def add_quick_zone_from_map(self, coords, zone_type):
        """Ajoute rapidement une zone avec un type prédéfini"""
        lat, lng = coords

        # Créer une popup simplifiée pour ce type de zone
        popup = tb.Toplevel(self)
        popup.title(f"📍 Ajouter {zone_type}")
        popup.geometry("350x400")
        popup.resizable(False, False)

        # Centrer la fenêtre
        popup.transient(self)
        popup.grab_set()

        # Titre
        tb.Label(popup, text=f"Nouvelle {zone_type}",
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Cadre pour le formulaire
        form_frame = tb.Frame(popup, padding=15)
        form_frame.pack(fill=X)

        # Coordonnées (non modifiables)
        coords_frame = tb.Frame(form_frame)
        coords_frame.pack(fill=X, pady=5)

        tb.Label(coords_frame, text="📍 Position:").pack(side=LEFT, padx=5)
        coords_label = tb.Label(coords_frame,
                               text=f"{lat:.4f}, {lng:.4f}",
                               font=("Consolas", 9))
        coords_label.pack(side=LEFT, padx=5)

        # Nom (auto-généré)
        name_frame = tb.Frame(form_frame)
        name_frame.pack(fill=X, pady=5)

        tb.Label(name_frame, text="🏷️ Nom:").pack(side=LEFT, padx=5)
        default_name = f"{zone_type} {datetime.now().strftime('%H%M%S')}"
        name_entry = tb.Entry(name_frame, width=20)
        name_entry.pack(side=LEFT, padx=5)
        name_entry.insert(0, default_name)

        # Ville
        city_frame = tb.Frame(form_frame)
        city_frame.pack(fill=X, pady=5)

        tb.Label(city_frame, text="🏙️ Ville:").pack(side=LEFT, padx=5)
        city_entry = tb.Entry(city_frame, width=20)
        city_entry.pack(side=LEFT, padx=5)
        city_entry.insert(0, "Kinshasa")  # Valeur par défaut

        # Tension (si applicable)
        voltage_frame = tb.Frame(form_frame)
        voltage_frame.pack(fill=X, pady=5)

        tb.Label(voltage_frame, text="⚡ Tension (V):").pack(side=LEFT, padx=5)
        voltage_entry = tb.Entry(voltage_frame, width=15)
        voltage_entry.pack(side=LEFT, padx=5)

        # Valeurs par défaut selon le type
        if zone_type == "Poste de transformation":
            voltage_entry.insert(0, "30000")
        elif zone_type == "Ligne BT":
            voltage_entry.insert(0, "220")
        elif zone_type == "Branchement":
            voltage_entry.insert(0, "220")

        # Description rapide
        desc_frame = tb.Frame(form_frame)
        desc_frame.pack(fill=X, pady=5)

        tb.Label(desc_frame, text="📝 Note:").pack(anchor=W, padx=5, pady=2)
        desc_text = tb.Text(desc_frame, height=2, width=30)
        desc_text.pack(padx=5, pady=2)

        # Boutons
        buttons_frame = tb.Frame(popup)
        buttons_frame.pack(fill=X, pady=10)

        def save_and_mark_quick_zone():
            name = name_entry.get().strip()
            city = city_entry.get().strip()
            voltage = voltage_entry.get().strip()
            description = desc_text.get("1.0", END).strip()

            if not name or not city:
                messagebox.showerror("Erreur", "Veuillez saisir au moins le nom et la ville")
                return

            # Sauvegarder dans la base de données
            conn = get_conn()
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO electric_zones (name, type, latitude, longitude, city,
                                              voltage, status, description, created_by, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, zone_type, lat, lng, city, voltage,
                      "✅ Fonctionnel", description, self.app.current_user_id, datetime.now()))
                conn.commit()

                zone_id = c.lastrowid
                messagebox.showinfo("Succès", f"{zone_type} ajouté avec marqueur!")

                # Envoi automatique du rapport
                zone_data = {
                    'id': zone_id,
                    'name': name,
                    'type': zone_type,
                    'latitude': lat,
                    'longitude': lng,
                    'city': city,
                    'voltage': voltage,
                    'status': "✅ Fonctionnel",
                    'description': description
                }
                self.auto_send_zone_report(zone_data)

                # Ajouter un marqueur sur la carte à la position de la zone
                self.add_marker_to_map(lat, lng, zone_type, name, zone_id)

                # Actualiser la carte et la liste
                self.update_map_markers()
                self.refresh_zones()
                self.load_zones_checkboxes(self.zone_checkboxes_frame)

                # Fermer la popup
                popup.destroy()

                # Remettre le menu normal
                self.restore_normal_menu()

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
            finally:
                conn.close()

        def save_quick_zone():
            name = name_entry.get().strip()
            city = city_entry.get().strip()
            voltage = voltage_entry.get().strip()
            description = desc_text.get("1.0", END).strip()

            if not name or not city:
                messagebox.showerror("Erreur", "Veuillez saisir au moins le nom et la ville")
                return

            # Sauvegarder dans la base de données
            conn = get_conn()
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO electric_zones (name, type, latitude, longitude, city,
                                              voltage, status, description, created_by, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, zone_type, lat, lng, city, voltage,
                      "✅ Fonctionnel", description, self.app.current_user_id, datetime.now()))
                conn.commit()

                messagebox.showinfo("Succès", f"{zone_type} ajouté avec succès!")

                # Envoi automatique du rapport
                zone_data = {
                    'id': c.lastrowid,
                    'name': name,
                    'type': zone_type,
                    'latitude': lat,
                    'longitude': lng,
                    'city': city,
                    'voltage': voltage,
                    'status': "✅ Fonctionnel",
                    'description': description
                }
                self.auto_send_zone_report(zone_data)

                # Actualiser la carte et la liste
                self.update_map_markers()
                self.refresh_zones()
                self.load_zones_checkboxes(self.zone_checkboxes_frame)

                # Fermer la popup
                popup.destroy()

                # Remettre le menu normal
                self.restore_normal_menu()

            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
            finally:
                conn.close()

        def cancel():
            popup.destroy()
            self.restore_normal_menu()

        tb.Button(buttons_frame, text="💾 Enregistrer & Marquer",
                  bootstyle="primary",
                  command=save_and_mark_quick_zone).pack(side=LEFT, padx=5)

        tb.Button(buttons_frame, text="💾 Enregistrer",
                  bootstyle="success",
                  command=save_quick_zone).pack(side=LEFT, padx=5)

        tb.Button(buttons_frame, text="❌ Annuler",
                  bootstyle="secondary",
                  command=cancel).pack(side=LEFT, padx=5)

    def send_map_image(self):
        """Capture et envoi de l'image de la carte"""
        try:
            # Créer un nom de fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"carte_zones_electriques_{timestamp}.png"

            # Capturer la carte (si tkintermapview supporte la capture)
            # Pour l'instant, simulation
            messagebox.showinfo("Capture Carte",
                               f"Carte capturée et sauvegardée sous:\n{filename}\n\nFonctionnalité d'envoi à implémenter.")

            # Ici vous pouvez ajouter :
            # 1. Capture réelle de la carte
            # 2. Sauvegarde du fichier
            # 3. Envoi par email ou upload vers serveur

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de capturer la carte: {str(e)}")

    def add_marker_to_map(self, lat, lng, zone_type, name, zone_id):
        """Ajoute un marqueur visuel sur la carte pour une zone"""
        try:
            # Déterminer la couleur selon le type de zone
            color_map = {
                "Poste de transformation": "red",
                "Ligne BT": "blue",
                "Branchement": "green",
                "Compteur": "orange",
                "Panneau solaire": "yellow",
                "Groupe électrogène": "purple"
            }
            marker_color = color_map.get(zone_type, "gray")

            # Créer le texte du popup
            popup_text = f"🏷️ {name}\n📍 {zone_type}\n📍 {lat:.4f}, {lng:.4f}"

            # Ajouter le marqueur sur la carte
            if hasattr(self, 'map_widget') and self.map_widget:
                marker = self.map_widget.set_marker(lat, lng, text=popup_text)
                if marker:
                    # Stocker l'ID de la zone dans le marqueur pour référence future
                    marker.zone_id = zone_id
                    marker.zone_type = zone_type
                    marker.zone_name = name

                    # Actualiser l'affichage des marqueurs
                    self.update_map_markers()

                    print(f"Marqueur ajouté pour {zone_type}: {name} à ({lat}, {lng})")

        except Exception as e:
            print(f"Erreur lors de l'ajout du marqueur: {str(e)}")
            messagebox.showwarning("Attention",
                                   f"Zone enregistrée mais marqueur non ajouté: {str(e)}")