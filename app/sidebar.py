# app/sidebar.py
import tkinter as tk

def setup_sidebar(app):
    def add_btn(text, cmd):
        btn = tk.Label(app.sidebar, text=text, bg="#34495e", fg="white",
                       font=("Arial", 12), padx=10, pady=8, cursor="hand2")
        btn.pack(fill="x", padx=15, pady=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1abc9c"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#34495e"))
        btn.bind("<Button-1>", lambda e: cmd())
        app.buttons.append(btn)
    app.buttons = []
    add_btn("🏠 Trang chu", app.show_home)
    add_btn("🗺️ Ban do", app.show_map)
    add_btn("📶 Quet ban do", app.show_scan_map)
    add_btn("💾 Du lieu", app.show_data)
    add_btn("📁 Thu muc", app.show_folder)
    add_btn("🤖 Robot", app.show_robot)
    add_btn("🛠️ Cai dat", app.show_settings)
