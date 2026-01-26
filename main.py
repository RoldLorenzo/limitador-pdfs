from tkinterdnd2 import TkinterDnD
import customtkinter as ctk
from ui import App

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    root = TkinterDnD.Tk()
    root.configure(bg="#2b2b2b")

    app = App(root)
    root.mainloop()
