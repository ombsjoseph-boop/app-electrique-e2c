from config import tb, LEFT, Y, X


class Sidebar(tb.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bootstyle="dark", width=280)
        self.app = app
        self.pack(side=LEFT, fill=Y)
        self.pack_propagate(False)


    

    