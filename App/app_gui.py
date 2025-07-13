# App/app_gui.py
import tkinter as tk
from PIL import Image, ImageTk
from App.home_tab import show_home
from App.map_tab import show_map
from App.scan_tab import show_scan_map
from App.data_tab import show_data
from App.folder_tab import show_folder
from App.robot_tab import show_robot
from App.settings_tab import show_settings

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Robot")
        self.root.geometry("900x600")

        self.sidebar = tk.Frame(root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="📋 MENU", bg="#2c3e50", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=20)

        self.buttons = []
        self.active_button = None
        self.send_text = None
        self.recv_text = None

        self.add_sidebar_button("🏠 Trang chu", lambda: show_home(self))
        self.add_sidebar_button("\U0001F6F9 Ban do", lambda: show_map(self))
        self.add_sidebar_button("\U0001F4F6 Quet ban do", lambda: show_scan_map(self))
        self.add_sidebar_button("\U0001F4BE Du lieu", lambda: show_data(self))
        self.add_sidebar_button("\U0001F4C1 Thu muc", lambda: show_folder(self))
        self.add_sidebar_button("\U0001F916 Robot", lambda: show_robot(self))
        self.add_sidebar_button("⚙️ Cai dat", lambda: show_settings(self))

        self.main_content = tk.Frame(root, bg="white")
        self.main_content.pack(side="left", fill="both", expand=True)

        show_home(self)

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def add_sidebar_button(self, text, command):
        btn = tk.Label(self.sidebar, text=text, bg="#34495e", fg="white",
                       font=("Arial", 12), padx=10, pady=8, cursor="hand2")
        btn.pack(fill="x", padx=15, pady=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1abc9c"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#34495e"))
        btn.bind("<Button-1>", lambda e: command())
        self.buttons.append(btn)
