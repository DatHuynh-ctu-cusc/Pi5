import tkinter as tk

class SettingsTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        tk.Label(self, text="Cài đặt hệ thống", font=("Arial", 16), bg="white").pack(pady=50)
        # Thêm các cài đặt (option, cấu hình v.v.) nếu cần
