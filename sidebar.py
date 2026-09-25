from config import tb, LEFT, Y, X, messagebox
import sys


class Sidebar(tb.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bootstyle="dark", width=280)
        self.app = app
        self.pack_propagate(False)
        # Pas de self.pack(...) ici : c'est App (dans show_frame) qui
        # empile la sidebar avec before=self.container, pour qu'elle
        # obtienne réellement de l'espace à gauche.

        # --- En-tête ---
        header = tb.Frame(self, bootstyle="dark", padding=20)
        header.pack(fill=X)

        tb.Label(header, text="⚡ E²C Admin",
                 font=("Segoe UI", 16, "bold"),
                 bootstyle="inverse-dark").pack(anchor=LEFT)

        # --- Navigation ---
        nav_frame = tb.Frame(self, bootstyle="dark", padding=(15, 20))
        nav_frame.pack(fill=X)

        tb.Button(nav_frame, text="🏠 Tableau de bord", bootstyle="dark-outline",
                   width=24,
                   command=lambda: self.app.show_frame("Dashboard")).pack(fill=X, pady=4)

        tb.Button(nav_frame, text="🗺️ Carte", bootstyle="dark-outline",
                   width=24,
                   command=lambda: self.app.show_frame("Map")).pack(fill=X, pady=4)

        tb.Label(nav_frame, text="Onglets du dashboard :",
                 font=("Segoe UI", 8, "italic"),
                 bootstyle="inverse-dark").pack(anchor=LEFT, pady=(15, 5))

        dashboard_tabs = [
            ("📍 Zones", 0),
            ("🗺️ Carte interactive", 1),
            ("📊 Rapports", 2),
            ("🧑‍🔧 Agents", 3),
            ("🗺️ Zones de Relevé", 4),
            ("👤 Clients", 5),
        ]
        for label, tab_index in dashboard_tabs:
            tb.Button(nav_frame, text=label, bootstyle="secondary-link",
                       command=lambda i=tab_index: self.go_to_dashboard_tab(i)
                       ).pack(fill=X, pady=1)

        # --- Bas de la sidebar : déconnexion / quitter ---
        footer = tb.Frame(self, bootstyle="dark", padding=15)
        footer.pack(side="bottom", fill=X)

        tb.Button(footer, text="🚪 Se déconnecter", bootstyle="warning",
                   width=24,
                   command=self.logout).pack(fill=X, pady=(0, 8))

        tb.Button(footer, text="⛔ Quitter", bootstyle="danger",
                   width=24,
                   command=self.quit_app).pack(fill=X)

    def go_to_dashboard_tab(self, index):
        """Affiche le Dashboard puis sélectionne l'onglet demandé."""
        self.app.show_frame("Dashboard")
        dashboard = self.app.frames.get("Dashboard")
        if dashboard and hasattr(dashboard, "notebook"):
            dashboard.notebook.select(index)

    def logout(self):
        """Déconnecte l'admin et revient à l'écran de connexion (App.logout())."""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.app.logout()

    def quit_app(self):
        """Ferme complètement l'application."""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.app.destroy()
            sys.exit(0)