from config import tk
from PIL import Image, ImageTk


def set_background(frame, image_path):
    image = Image.open(image_path).resize((1950, 1000), Image.LANCZOS)
    # attacher le PhotoImage au 'master' du widget pour éviter les problèmes
    # lorsque la racine Tkinter est détruite et que le PhotoImage est récupéré par le garbage collector
    photo = ImageTk.PhotoImage(image, master=frame)
    label = tk.Label(frame, image=photo)
    label.image = photo
    label.place(relwidth=1, relheight=1)