# app/sidebar.py

import tkinter as tk

class Sidebar:
    def __init__(self, root, main_app):
        self.main_app = main_app
        self.frame = tk.Frame(root, bg="#2c3e50", width=200)
        self.frame.pack(side="left", fill="y")
        self.frame.pack_propagate(False)

        # Tiêu đề sidebar
        tk.Label(self.frame, text="📋 MENU", bg="#2c3e50", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=20)

        # Các nút chuyển tab
        self.buttons = []
        self.add_sidebar_button("🏠 Trang chủ", self.main_app.show_home)
        self.add_sidebar_button("🗺️ Bản đồ", self.main_app.show_map)
        self.add_sidebar_button("📶 Quét bản đồ", self.main_app.show_scan_map)
        self.add_sidebar_button("💾 Dữ liệu", self.main_app.show_data)
        self.add_sidebar_button("📁 Thư mục", self.main_app.show_folder)
        self.add_sidebar_button("🤖 Robot", self.main_app.show_robot)
        self.add_sidebar_button("🛠️ Cài đặt", self.main_app.show_settings)

    def add_sidebar_button(self, text, command):
        btn = tk.Label(self.frame, text=text, bg="#34495e", fg="white",
                       font=("Arial", 12), padx=10, pady=8, cursor="hand2")
        btn.pack(fill="x", padx=15, pady=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1abc9c"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#34495e"))
        btn.bind("<Button-1>", lambda e: command())
        self.buttons.append(btn)
