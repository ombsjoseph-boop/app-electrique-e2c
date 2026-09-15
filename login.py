import threading

from config import tb, CENTER, messagebox
from ui_utils import set_background
from database import get_conn


# Largeur commune à tous les champs et au bouton, pour un alignement propre
FIELD_WIDTH = 24
LABEL_WIDTH = 15


class LoginFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        set_background(self, "assets/bg.jpg")

        # ---------- Carte centrale ----------
        card = tb.Frame(self, bootstyle="light", padding=0)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Bande d'accent en haut de la carte
        accent = tb.Frame(card, bootstyle="success", height=6)
        accent.pack(fill="x", side="top")

        inner = tb.Frame(card, bootstyle="light", padding=(45, 35, 45, 35))
        inner.pack(fill="both", expand=True)

        # ---------- En-tête ----------
        tb.Label(
            inner,
            text="🔐",
            font=("Segoe UI", 32),
            bootstyle="success",
        ).pack(pady=(0, 5))

        tb.Label(
            inner,
            text="Connexion Admin Technique",
            font=("Segoe UI", 19, "bold"),
        ).pack()

        tb.Label(
            inner,
            text="Réservé aux administrateurs techniques",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).pack(pady=(2, 25))

        # ---------- Champ utilisateur (label + entrée côte à côte) ----------
        user_row = tb.Frame(inner)
        user_row.pack(fill="x", pady=(0, 10))

        tb.Label(
            user_row, text="Nom d'utilisateur",
            font=("Segoe UI", 10, "bold"),
            width=LABEL_WIDTH, anchor="w",
        ).pack(side="left")

        self.user = tb.Entry(user_row, width=FIELD_WIDTH, font=("Segoe UI", 11))
        self.user.pack(side="left", fill="x", expand=True, ipady=6)
        self.user.focus_set()

        # ---------- Champ mot de passe (label + entrée + bouton, côte à côte) ----------
        pwd_row = tb.Frame(inner)
        pwd_row.pack(fill="x", pady=(0, 6))

        tb.Label(
            pwd_row, text="Mot de passe",
            font=("Segoe UI", 10, "bold"),
            width=LABEL_WIDTH, anchor="w",
        ).pack(side="left")

        self.pwd = tb.Entry(pwd_row, width=FIELD_WIDTH, show="•", font=("Segoe UI", 11))
        self.pwd.pack(side="left", fill="x", expand=True, ipady=6)

        self.show_pwd = tb.Button(
            pwd_row, text="👁", bootstyle="link-secondary", width=3,
            command=self.toggle_password,
        )
        self.show_pwd.pack(side="left", padx=(6, 0))

        # ---------- Message d'erreur inline ----------
        self.error_label = tb.Label(
            inner, text="", font=("Segoe UI", 9),
            bootstyle="danger", wraplength=300, justify="left",
        )
        self.error_label.pack(anchor="w", pady=(2, 10))

        # Efface l'erreur dès que l'utilisateur corrige sa saisie
        self.user.bind("<KeyRelease>", lambda e: self.clear_error())
        self.pwd.bind("<KeyRelease>", lambda e: self.clear_error())

        # Entrée = connexion (depuis les deux champs)
        self.user.bind("<Return>", lambda e: self.login())
        self.pwd.bind("<Return>", lambda e: self.login())

        # ---------- Bouton de connexion ----------
        self.login_btn = tb.Button(
            inner, text="Se connecter",
            bootstyle="success",
            width=FIELD_WIDTH + LABEL_WIDTH,
            command=self.login,
        )
        self.login_btn.pack(pady=(6, 4), ipady=4)

        self.status_label = tb.Label(
            inner, text="", font=("Segoe UI", 9, "italic"),
            bootstyle="secondary",
        )
        self.status_label.pack(pady=(2, 0))

        """tb.Button(inner, text="Créer un compte",
                  bootstyle="secondary",
                  command=lambda: app.show_frame("Register")).pack()"""

    # ------------------------------------------------------------------
    # UX helpers
    # ------------------------------------------------------------------
    def toggle_password(self):
        if self.pwd.cget("show") == "•":
            self.pwd.config(show="")
            self.show_pwd.config(text="🙈")
        else:
            self.pwd.config(show="•")
            self.show_pwd.config(text="👁")

    def clear_error(self):
        if self.error_label.cget("text"):
            self.error_label.config(text="")

    def show_error(self, message):
        self.error_label.config(text=message)

    def set_loading(self, loading: bool):
        if loading:
            self.login_btn.config(state="disabled", text="Connexion en cours...")
            self.status_label.config(text="Vérification des identifiants...")
        else:
            self.login_btn.config(state="normal", text="Se connecter")
            self.status_label.config(text="")

    # ------------------------------------------------------------------
    # Logique de connexion
    # ------------------------------------------------------------------
    def login(self):
        username = self.user.get().strip()
        password = self.pwd.get()

        # Validation avant tout appel réseau/DB
        if not username or not password:
            self.show_error("Veuillez renseigner le nom d'utilisateur et le mot de passe.")
            return

        self.clear_error()
        self.set_loading(True)

        # Requête DB dans un thread pour ne pas geler l'interface
        threading.Thread(target=self._authenticate, args=(username, password), daemon=True).start()

    def _authenticate(self, username, password):
        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "SELECT id FROM admin WHERE nom=%s AND password=%s",
                (username, password),
            )
            row = c.fetchone()
            conn.close()
        except Exception as exc:
            self.after(0, self._on_login_error, f"Connexion à la base de données impossible : {exc}")
            return

        if row:
            self.after(0, self._on_login_success, username, row[0])
        else:
            self.after(0, self._on_login_error, "Identifiants incorrects.")

    def _on_login_success(self, username, user_id):
        self.set_loading(False)
        self.app.current_user = username
        self.app.current_user_id = user_id
        self.app.show_frame("Dashboard")

    def _on_login_error(self, message):
        self.set_loading(False)
        self.show_error(message)
        self.pwd.delete(0, "end")
        self.pwd.focus_set()