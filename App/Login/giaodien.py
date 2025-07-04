import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from App.Login.chucnang import kiem_tra_dang_nhap
import os

def hien_thi_login(window, on_success_callback):
    current_dir = os.path.dirname(__file__)
    logo_path = os.path.join(current_dir, "assets", "logo.png")

    try:
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((150, 150))
        logo = ImageTk.PhotoImage(logo_img)
        label_logo = tk.Label(window, image=logo)
        label_logo.image = logo
        label_logo.pack(pady=10)
    except Exception as e:
        print(f"[LỖI] Không thể tải logo: {e}")

    tk.Label(window, text="Tên đăng nhập").pack(pady=5)
    entry_user = tk.Entry(window)
    entry_user.pack()

    tk.Label(window, text="Mật khẩu").pack(pady=5)
    entry_pass = tk.Entry(window, show="*")
    entry_pass.pack()

    def dang_nhap():
        user = entry_user.get()
        passwd = entry_pass.get()
        if kiem_tra_dang_nhap(user, passwd):
            messagebox.showinfo("Thông báo", "Đăng nhập thành công!")
            on_success_callback(user)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu")

    tk.Button(window, text="Đăng nhập", command=dang_nhap).pack(pady=15)
    entry_user.focus()
