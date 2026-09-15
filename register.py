from config import tb, CENTER, messagebox, mysql
from ui_utils import set_background
from database import get_conn, notify_dashboard


class RegisterFrame(tb.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        set_background(self, "assets/bg.jpg")

        card = tb.Frame(self, bootstyle="light", padding=40)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)

        tb.Label(card, text="📝 Inscription",
                 font=("Segoe UI", 20, "bold")).pack(pady=10)

        self.user = tb.Entry(card, width=30)
        self.user.pack(pady=8)

        self.pwd = tb.Entry(card, width=30, show="*")
        self.pwd.pack(pady=8)

        

    def register(self):
        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "INSERT INTO users(username,password) VALUES (%s,%s)",
                (self.user.get(), self.pwd.get())
            )
            conn.commit()
            conn.close()
            notify_dashboard()
            messagebox.showinfo("Succès", "Compte créé")
            self.app.show_frame("Login")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erreur", "Utilisateur déjà existant")