# app/settings_view.py

import tkinter as tk

def show_settings(app):
    app.clear_main_content()
    tk.Label(app.main_content, text="CÀI ĐẶT HỆ THỐNG", font=("Arial", 18, "bold"),
             bg="white", fg="#2c3e50").pack(pady=30)
    # Có thể bổ sung thêm widget cấu hình, nút reset, chọn theme, ...
