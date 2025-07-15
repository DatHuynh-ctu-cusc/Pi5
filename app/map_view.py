# app/map_view.py
import tkinter as tk
from lidar_map_drawer import draw_lidar_on_canvas, draw_zoomed_lidar_map

def show_map(app):
    app.clear_main_content()
    tk.Label(app.main_content, text="BẢN ĐỒ HOẠT ĐỘNG CỦA ROBOT",
             font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
    app.main_map = tk.Canvas(app.main_content, width=680, height=300, bg="#ecf0f1", highlightbackground="#bdc3c7")
    app.main_map.pack(pady=5)
    bottom_frame = tk.Frame(app.main_content, bg="white")
    bottom_frame.pack(fill="x", padx=10, pady=10)
    app.sub_map = tk.Canvas(bottom_frame, width=300, height=200, bg="#dfe6e9", highlightbackground="#bdc3c7")
    app.sub_map.pack(side="left", padx=5)
    control_frame = tk.Frame(bottom_frame, bg="white")
    control_frame.pack(side="left", fill="both", expand=True, padx=10)
    tk.Button(control_frame, text="🗂 Chọn bản đồ", font=("Arial", 11), width=20, command=lambda: select_map(app)).pack(pady=4)
    tk.Button(control_frame, text="🗑 Xoá bản đồ", font=("Arial", 11), width=20, command=lambda: clear_map(app)).pack(pady=4)
    tk.Button(control_frame, text="✏️ Vẽ đường đi", font=("Arial", 11), width=20, command=lambda: draw_path(app)).pack(pady=4)
    tk.Button(control_frame, text="❌ Xoá đường đi", font=("Arial", 11), width=20, command=lambda: clear_path(app)).pack(pady=4)
    app.robot_status_label = tk.Label(control_frame, text="Trạng thái: Di chuyển", font=("Arial", 11, "bold"),
                                      bg="green", fg="white", width=20)
    app.robot_status_label.pack(pady=10)

def select_map(app):
    from tkinter import filedialog
    from PIL import Image, ImageTk
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        try:
            image = Image.open(file_path)
            image = image.resize((680, 300), Image.Resampling.LANCZOS)
            app.map_image = ImageTk.PhotoImage(image)
            app.main_map.create_image(0, 0, anchor="nw", image=app.map_image)
            print(f"🖼 Đã chọn bản đồ: {file_path}")
        except Exception as e:
            print("❌ Lỗi khi mở bản đồ:", e)

def clear_map(app):
    print("🗑 Đã xoá bản đồ!")

def draw_path(app):
    print("✏️ Vẽ đường đi")

def clear_path(app):
    print("❌ Đã xoá đường đi")
