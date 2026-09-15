from config import tb, BOTH
from sidebar import Sidebar
from login import LoginFrame
from register import RegisterFrame
from dashboard_frame import DashboardFrame
from map_frame import MapFrame
from database import init_db
from map_server_pkg import start_map_server


start_map_server

class App(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("E²C congo - Application Technique et Électrique")
        self.geometry("1200x700")

        self.current_user = None
        self.current_user_id = None
        self.sidebar = None

        self.container = tb.Frame(self)
        self.container.pack(fill=BOTH, expand=True)

        self.frames = {}
        for F, name in [
            (LoginFrame, "Login"),
            
            (DashboardFrame, "Dashboard"),
            (MapFrame, "Map")
        ]:
            frame = F(self.container, self)
            self.frames[name] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("Login")

    def show_frame(self, name):
        if name in ("Dashboard", "Map") and not self.sidebar:
            self.sidebar = Sidebar(self, self)

        self.frames[name].tkraise()

        if name == "Dashboard":
            self.frames[name].refresh()
        if name == "Map":
            self.frames[name].load_points()

    def show_admin_view(self):
        """Basculer vers la vue admin dans le dashboard"""
        if "Dashboard" in self.frames:
            self.frames["Dashboard"].show_view("admin")

    def logout(self):
        self.current_user = None
        self.current_user_id = None
        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None
        self.show_frame("Login")


# ---------------- RUN ----------------


if __name__ == "__main__":
    init_db()
    start_map_server()
    app = App()
    app.mainloop()
    

