import tkinter as tk
import threading
import numpy as np
from PIL import Image, ImageTk
import os
import time
from tkinter import filedialog

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Robot")
        self.root.geometry("1100x700")

        self.running = threading.Event()
        self.running.set()

        self.sidebar = tk.Frame(root, width=250, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.buttons = []
        self.active_button = None

        tk.Label(self.sidebar, text="\U0001F4CB MENU", bg="#2c3e50", fg="white", font=("Arial", 14, "bold")).pack(pady=20)
        self.add_sidebar_button("\U0001F3E1 Trang chu", self.show_home)
        self.add_sidebar_button("\U0001F6F9 Ban do", self.show_map)
        self.add_sidebar_button("\U0001F4F6 Quet ban do", self.show_scan_map)
        self.add_sidebar_button("\U0001F4BE Du lieu", self.show_data)
        self.add_sidebar_button("\U0001F4C2 Thu muc", self.show_folder)
        self.add_sidebar_button("\U0001F916 Robot", self.show_robot)
        self.add_sidebar_button("\U0001F6E0 Cai dat", self.show_settings)

        self.content = tk.Frame(root, bg="white")
        self.content.pack(side="right", expand=True, fill="both")

        self.encoder_labels = {}
        self.main_map_canvas = None
        self.zoom_map_canvas = None
        self.path_label = None
        self.send_text = None
        self.recv_text = None

        self.map_size = 10.0
        self.resolution = 0.1
        self.cells = int(self.map_size / self.resolution)
        self.ogm_map = np.ones((self.cells, self.cells), dtype=np.uint8) * 255
        self.ogm_map_scan = np.zeros((self.cells, self.cells), dtype=np.uint8)
        self.robot_pose = (5.0, 5.0, 0.0)

        self.scan_map_canvas = tk.Canvas(self.content, bg="white")
        self.scan_map_canvas.pack_forget()

        self.loaded_map_image = None
        os.makedirs("/home/dat/LuanVan/maps", exist_ok=True)

        self.show_home()

    def add_sidebar_button(self, text, command):
        btn = tk.Button(self.sidebar, text=text, bg="#34495e", fg="white", font=("Arial", 12, "bold"), relief="flat", command=command)
        btn.pack(fill="x", pady=5, padx=10)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1abc9c"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#34495e"))
        self.buttons.append(btn)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.pack_forget()

    def show_home(self):
        self.clear_content()
        tk.Label(self.content, text="\U0001F3E1 TRANG CHỦ", font=("Arial", 20), bg="white").pack(pady=50)

    def update_lidar_map(self, lidar_data):
        try:
            if not self.scan_map_canvas or not self.scan_map_canvas.winfo_exists():
                return

            angle = lidar_data.get("angle_min", 0)
            increment = lidar_data.get("angle_increment", 0.01)
            ranges = lidar_data.get("ranges", [])
            cx, cy = 50, 50
            max_range = 6.0

            for r in ranges:
                if 0.05 < r < max_range:
                    x = r * np.cos(angle)
                    y = r * np.sin(angle)
                    gx = int(cx + x / self.resolution)
                    gy = int(cy + y / self.resolution)
                    if 0 <= gx < 100 and 0 <= gy < 100:
                        self.ogm_map_scan[gy][gx] = 2
                    angle += increment

            img = Image.fromarray((self.ogm_map_scan * 127).astype(np.uint8), mode="L")
            img = img.resize((self.scan_map_canvas.winfo_width(), self.scan_map_canvas.winfo_height()))
            tk_img = ImageTk.PhotoImage(img)
            self.scan_map_canvas.create_image(0, 0, anchor="nw", image=tk_img)
            self.scan_map_canvas.image = tk_img

        except Exception as e:
            print("[App] ⚠️ Lỗi khi cập nhật LiDAR map:", e)


    def show_map(self):
        self.clear_content()

        self.main_map_canvas = tk.Canvas(self.content, bg="white")
        self.main_map_canvas.pack(side="top", expand=True, fill="both")

        bottom_frame = tk.Frame(self.content, bg="white")
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.zoom_map_canvas = tk.Canvas(bottom_frame, width=200, height=200, bg="lightgray")
        self.zoom_map_canvas.pack(side="left", padx=10)

        button_frame = tk.Frame(bottom_frame, bg="white")
        button_frame.pack(side="left", padx=20)

        select_btn = tk.Button(button_frame, text="\U0001F4C2 Chọn bản đồ", font=("Arial", 11), command=self.select_map_file)
        select_btn.pack(pady=5, fill="x")

        draw_btn = tk.Button(button_frame, text="✏️ Vẽ đường đi", font=("Arial", 11), command=self.enable_draw_path)
        draw_btn.pack(pady=5, fill="x")

        clear_path_btn = tk.Button(button_frame, text="❌ Xóa đường đi", font=("Arial", 11), command=self.clear_drawn_path)
        clear_path_btn.pack(pady=5, fill="x")

        clear_map_btn = tk.Button(button_frame, text="\U0001F5D1 Xóa bản đồ", font=("Arial", 11), command=self.clear_main_map)
        clear_map_btn.pack(pady=5, fill="x")

    def show_scan_map(self):
        self.clear_content()
        self.scan_map_canvas.pack(expand=True, fill="both")

        btn_frame = tk.Frame(self.content, bg="white")
        btn_frame.pack(fill="x", pady=10)

        save_btn = tk.Button(btn_frame, text="\U0001F4BE Lưu bản đồ", font=("Arial", 11), command=self.save_scan_map)
        save_btn.pack(side="left", padx=10)

        clear_btn = tk.Button(btn_frame, text="\U0001F504 Làm mới", font=("Arial", 11), command=self.clear_scan_map)
        clear_btn.pack(side="left", padx=10)

    def show_data(self):
        self.clear_content()
        title = tk.Label(self.content, text="\U0001F4BE DỮ LIỆU", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50")
        title.pack(pady=10)

        container = tk.Frame(self.content, bg="white")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        send_frame = tk.LabelFrame(container, text="\U0001F4E4 DỮ LIỆU GỬI", font=("Arial", 12, "bold"), bg="white", fg="#34495e", padx=10, pady=5)
        send_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.send_text = tk.Text(send_frame, height=25, bg="#ecf0f1", font=("Courier", 10))
        self.send_text.pack(fill="both", expand=True)

        recv_frame = tk.LabelFrame(container, text="\U0001F4E5 DỮ LIỆU NHẬN", font=("Arial", 12, "bold"), bg="white", fg="#34495e", padx=10, pady=5)
        recv_frame.pack(side="right", fill="both", expand=True, padx=10)

        self.recv_text = tk.Text(recv_frame, height=25, bg="#ecf0f1", font=("Courier", 10))
        self.recv_text.pack(fill="both", expand=True)

    def show_folder(self):
        self.clear_content()
        tk.Label(self.content, text="\U0001F4C2 THƯ MỤC", font=("Arial", 20), bg="white").pack(pady=50)

    def show_robot(self):
        self.clear_content()
        tk.Label(self.content, text="\U0001F916 ROBOT", font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        canvas = tk.Canvas(self.content, width=400, height=400, bg="white", highlightthickness=0)
        canvas.pack()

        canvas.create_rectangle(100, 100, 300, 300, fill="#ecf0f1", outline="black", width=2)
        positions = {
            "E1": (90, 90, "Trái Trước"),
            "E2": (90, 310, "Trái Sau"),
            "E3": (310, 90, "Phải Trước"),
            "E4": (310, 310, "Phải Sau")
        }
        self.encoder_labels.clear()
        for key, (x, y, label) in positions.items():
            canvas.create_oval(x-10, y-10, x+10, y+10, fill="black")
            canvas.create_text(x, y-15, text=label, font=("Arial", 9, "bold"))
            lbl = tk.Label(self.content, text=f"{key}: 0", bg="white", font=("Arial", 10))
            lbl.pack()
            self.encoder_labels[key] = lbl

        self.update_robot_ui()

    def show_settings(self):
        self.clear_content()
        tk.Label(self.content, text="\U0001F6E0 CÀI ĐẶT", font=("Arial", 20), bg="white").pack(pady=50)

    def select_map_file(self):
        path = filedialog.askopenfilename(initialdir="/home/dat/LuanVan/maps", filetypes=[("PNG Files", "*.png")])
        if path:
            try:
                img = Image.open(path).convert("L")
                img = img.resize((self.ogm_map.shape[1], self.ogm_map.shape[0]))
                self.ogm_map = np.array(img)
                self.main_map_canvas.delete("all")
                self.draw_main_map()
                print("[App] ✅ Đã tải bản đồ:", path)
            except Exception as e:
                print("[App] ❌ Lỗi khi tải bản đồ:", e)

    def enable_draw_path(self):
        self.main_map_canvas.bind("<Button-1>", self.draw_path_point)
        print("[App] ✏️ Chế độ vẽ đường đi được kích hoạt")

    def draw_path_point(self, event):
        x, y = event.x, event.y
        self.main_map_canvas.create_oval(x-3, y-3, x+3, y+3, fill="red")

    def clear_drawn_path(self):
        self.main_map_canvas.delete("all")
        self.draw_main_map()
        print("[App] ❌ Đã xoá đường đi")

    def clear_main_map(self):
        self.ogm_map.fill(255)
        self.main_map_canvas.delete("all")
        print("[App] 🗑️ Đã xoá bản đồ chính")

    def draw_main_map(self):
        img = Image.fromarray((self.ogm_map * 1).astype(np.uint8), mode="L")
        img = img.resize((self.main_map_canvas.winfo_width(), self.main_map_canvas.winfo_height()))
        tk_img = ImageTk.PhotoImage(img)
        self.main_map_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        self.main_map_canvas.image = tk_img

    def clear_scan_map(self):
        self.ogm_map_scan.fill(0)
        self.scan_map_canvas.delete("all")
        print("[App] 🔄 Đã làm mới bản đồ quét")

    def save_scan_map(self):
        try:
            img = Image.fromarray((self.ogm_map_scan * 127).astype(np.uint8), mode="L")
            path = f"/home/dat/LuanVan/maps/map_{time.strftime('%Y%m%d_%H%M%S')}.png"
            img.save(path)
            print("[App] ✅ Đã lưu bản đồ quét tại:", path)
        except Exception as e:
            print("[App] ❌ Không thể lưu bản đồ quét:", e)

    def update_robot_ui(self):
        encoder_data = getattr(self, "encoder_data", {"E1": 0, "E2": 0, "E3": 0, "E4": 0})
        for key, lbl in self.encoder_labels.items():
            value = encoder_data.get(key, 0)
            lbl.config(text=f"{key}: {value}")
