import tkinter as tk
from PIL import Image, ImageTk

class HomeTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        tk.Label(self, text="ĐỒ ÁN TỐT NGHIỆP",
                 font=("Arial", 24, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
        tk.Label(self, text="HỆ THỐNG XE TỰ HÀNH TRÁNH VẬT CẢN DÙNG LIDAR",
                 font=("Arial", 14, "bold"), bg="white", fg="#34495e").pack(pady=(10, 2))
        try:
            img = Image.open("bach_khoa.jpg")
            img = img.resize((600, 300), Image.Resampling.LANCZOS)
            self.home_image = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.home_image, bg="white").pack(pady=10)
        except Exception as e:
            tk.Label(self, text=f"Lỗi ảnh: {e}", fg="red", bg="white").pack()

        bottom_frame = tk.Frame(self, bg="white")
        bottom_frame.pack(fill="x", padx=30, pady=(30, 10))

        gvhd_frame = tk.Frame(bottom_frame, bg="white")
        gvhd_frame.pack(side="left", anchor="nw", padx=(0, 30))
        tk.Label(gvhd_frame, text="GVHD:", font=("Arial", 11, "bold"), bg="white", anchor="w", fg="gray30").pack(anchor="w")
        tk.Label(gvhd_frame, text="Trương Phong Tuyên", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")

        student_frame = tk.Frame(bottom_frame, bg="white")
        student_frame.pack(side="right", anchor="ne", padx=(30, 0))
        sv1_frame = tk.Frame(student_frame, bg="white")
        sv1_frame.pack(anchor="w", pady=(0, 10))
        tk.Label(sv1_frame, text="Sinh viên 1: Huỳnh Tuấn Đạt", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")
        tk.Label(sv1_frame, text="MSSV: B2016890", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")
        tk.Label(sv1_frame, text="Lớp: Kỹ Thuật Máy Tính – K46", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")

        sv2_frame = tk.Frame(student_frame, bg="white")
        sv2_frame.pack(anchor="w")
        tk.Label(sv2_frame, text="Sinh viên 2: Nguyễn Phước Hoày", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")
        tk.Label(sv2_frame, text="MSSV: B2007073", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")
        tk.Label(sv2_frame, text="Lớp: Kỹ Thuật Máy Tính – K46", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")
