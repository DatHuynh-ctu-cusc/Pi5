# app.py
import tkinter as tk
import threading
import numpy as np
from encoder_handler import positions, get_robot_pose
from lidar_map_drawer import update_ogm_map, draw_ogm_on_canvas, draw_zoomed_lidar_map
from PIL import Image, ImageTk
import time
import math


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
        self.scan_canvas = None
        self.path_label = None
        self.send_text = None
        self.recv_text = None

        self.map_size = 10.0
        self.resolution = 0.1
        self.cells = int(self.map_size / self.resolution)
        self.ogm_map = np.ones((self.cells, self.cells), dtype=np.uint8) * 255
        self.ogm_map_scan = np.zeros((self.cells, self.cells), dtype=np.uint8)  # 0: unknown, 1: free, 2: occupied
        self.robot_pose = (5.0, 5.0, 0.0)

        self.show_home()

    def add_sidebar_button(self, label, command):
        btn = tk.Button(self.sidebar, text=label, bg="#34495e", fg="white", font=("Arial", 12), height=2, anchor="w", padx=20, relief="flat")
        btn.pack(fill="x", pady=2)
        btn.config(command=lambda b=btn, c=command: self.on_sidebar_click(b, c))
        self.buttons.append(btn)

    def on_sidebar_click(self, button, command):
        if self.active_button:
            self.active_button.config(bg="#34495e")
        button.config(bg="#1abc9c")
        self.active_button = button
        command()

    def show_home(self):
        self.update_content("\U0001F3E1 Đây là Trang chủ")

    def show_map(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        map_frame = tk.Frame(self.content, bg="white")
        map_frame.pack(fill="both", expand=True)
        map_frame.grid_rowconfigure(0, weight=3)
        map_frame.grid_rowconfigure(1, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)
        map_frame.grid_columnconfigure(1, weight=1)

        self.main_map_canvas = tk.Canvas(map_frame, bg="white")
        self.main_map_canvas.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.zoom_map_canvas = tk.Canvas(map_frame, bg="white", width=200, height=200)
        self.zoom_map_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        btn_frame = tk.Frame(map_frame, bg="white")
        btn_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.save_btn = tk.Button(btn_frame, text="Lưu bản đồ", width=15)
        self.save_btn.pack(pady=5)

        self.clear_btn = tk.Button(btn_frame, text="Xóa bản đồ", width=15)
        self.clear_btn.pack(pady=5)

        self.path_btn = tk.Button(btn_frame, text="Vẽ đường đi", width=15)
        self.path_btn.pack(pady=5)

        self.path_label = tk.Label(btn_frame, text="Số đường đi: 0", bg="white", font=("Arial", 11))
        self.path_label.pack(pady=10)

    def show_scan_map(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.content, bg="white")
        frame.pack(fill="both", expand=True)

        self.scan_canvas = tk.Canvas(frame, bg="white")
        self.scan_canvas.pack(expand=True, fill="both")

    def show_data(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        title = tk.Label(self.content, text="\U0001F4BE Dữ LIỆU ROBOT", font=("Arial", 20), bg="white")
        title.pack(pady=10)

        send_label = tk.Label(self.content, text="Dữ LIỆU Gửi (Encoder + Limit):", bg="white", font=("Arial", 12, "bold"))
        send_label.pack(pady=(10, 0))
        self.send_text = tk.Text(self.content, height=10, bg="#ecf0f1")
        self.send_text.pack(fill="x", padx=20)

        recv_label = tk.Label(self.content, text="Dữ LIỆU NHẬN (LiDAR từ Pi4):", bg="white", font=("Arial", 12, "bold"))
        recv_label.pack(pady=(20, 0))
        self.recv_text = tk.Text(self.content, height=10, bg="#ecf0f1")
        self.recv_text.pack(fill="x", padx=20)

    def show_folder(self):
        self.update_content("\U0001F4C2 Thư mục lưu file")

    def show_robot(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.canvas = tk.Canvas(self.content, bg="white")
        self.canvas.pack(expand=True, fill="both")
        self.encoder_labels = {}
        self.canvas.bind("<Configure>", self.draw_robot_centered)

    def show_settings(self):
        self.update_content("\U0001F6E0 Cài đặt hệ thống")

    def update_content(self, text):
        for widget in self.content.winfo_children():
            widget.destroy()
        tk.Label(self.content, text=text, font=("Arial", 20), bg="white").pack(expand=True)

    def draw_robot_centered(self, event):
        self.canvas.delete("all")
        for lbl in self.encoder_labels.values():
            lbl.destroy()
        self.encoder_labels.clear()
        width, height = event.width, event.height
        car_w, car_h = 200, 300
        x0 = (width - car_w) // 2
        y0 = (height - car_h) // 2
        x1 = x0 + car_w
        y1 = y0 + car_h
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="#bdc3c7", outline="black", width=2)
        wheel_pos = {
            "E1": (x0 - 45, y0 + 10),
            "E2": (x0 - 45, y1 - 40),
            "E3": (x1 + 5, y0 + 10),
            "E4": (x1 + 5, y1 - 40),
        }
        for name, (x, y) in wheel_pos.items():
            self.canvas.create_rectangle(x, y, x + 40, y + 30, fill="#2c3e50")
            self.canvas.create_text(x + 20, y - 10, text=name, font=("Arial", 9))
            lbl = tk.Label(self.canvas, text=f"Encoder: {positions[name]}", bg="white", font=("Arial", 9))
            lbl.place(x=x - 5, y=y + 35)
            self.encoder_labels[name] = lbl

    def update_lidar_map(self, data):
        try:
            self.robot_pose = get_robot_pose()[:3]
            x_cell = int(self.robot_pose[0] / self.resolution)
            y_cell = int(self.robot_pose[1] / self.resolution)
            self.robot_pos_xy = [x_cell, y_cell]

            if hasattr(self, 'main_map_canvas') and self.main_map_canvas and self.main_map_canvas.winfo_exists():
                draw_ogm_on_canvas(self.main_map_canvas, self.ogm_map, self.robot_pose)

            if hasattr(self, 'zoom_map_canvas') and self.zoom_map_canvas and self.zoom_map_canvas.winfo_exists():
                draw_zoomed_lidar_map(self.zoom_map_canvas, data)

            if hasattr(self, 'scan_canvas') and self.scan_canvas and self.scan_canvas.winfo_exists():
                angle = data.get("angle_min", 0)
                inc = data.get("angle_increment", 0.01)
                for r in data.get("ranges", []):
                    if 0.05 < r < 6.0:
                        x = self.robot_pose[0] + r * math.cos(angle)
                        y = self.robot_pose[1] + r * math.sin(angle)
                        gx = int(x / self.resolution)
                        gy = int(y / self.resolution)
                        if 0 <= gx < self.cells and 0 <= gy < self.cells:
                            self.ogm_map_scan[gy, gx] = 2
                        steps = int(r / self.resolution)
                        for s in range(steps):
                            fx = self.robot_pose[0] + s * self.resolution * math.cos(angle)
                            fy = self.robot_pose[1] + s * self.resolution * math.sin(angle)
                            fx_cell = int(fx / self.resolution)
                            fy_cell = int(fy / self.resolution)
                            if 0 <= fx_cell < self.cells and 0 <= fy_cell < self.cells:
                                if self.ogm_map_scan[fy_cell, fx_cell] == 0:
                                    self.ogm_map_scan[fy_cell, fx_cell] = 1
                    angle += inc
                draw_ogm_scan_canvas(self.scan_canvas, self.ogm_map_scan, self.robot_pose)

        except Exception as e:
            print("[App] ⚠️ Lỗi khi cập nhật LiDAR map:", e)

    def draw_path(self):
        print("[App] 🚗 Đã bấm nút vẽ đường đi")
        if self.path_label:
            current = int(self.path_label.cget("text").split(":")[-1].strip())
            self.path_label.config(text=f"Số thứ tự: {current + 1}")


def draw_ogm_scan_canvas(canvas, ogm_map, robot_pose):
    if not canvas or not canvas.winfo_exists():
        return

    width = canvas.winfo_width()
    height = canvas.winfo_height()
    map_size_px = min(width, height)

    ogm_res = ogm_map.shape[0]
    scale = map_size_px // ogm_res
    img_size = ogm_res * scale

    img = Image.new("RGB", (img_size, img_size), "gray")  # gray = unknown
    pixels = img.load()

    for y in range(ogm_res):
        for x in range(ogm_res):
            value = ogm_map[y, x]
            if value == 1:
                pixels[x * scale, y * scale] = (255, 255, 255)  # free: white
            elif value == 2:
                pixels[x * scale, y * scale] = (0, 0, 0)        # occupied: black

    # Tô pixel theo tỷ lệ
    for y in range(ogm_res):
        for x in range(ogm_res):
            color = pixels[x * scale, y * scale]
            for dy in range(scale):
                for dx in range(scale):
                    if (x * scale + dx) < img_size and (y * scale + dy) < img_size:
                        pixels[x * scale + dx, y * scale + dy] = color

    # Vẽ robot
    rx, ry, theta = robot_pose
    center_cell = ogm_res // 2
    rx_cell = center_cell + int(rx / 0.1)
    ry_cell = center_cell - int(ry / 0.1)

    rx_px = rx_cell * scale
    ry_px = ry_cell * scale

    if 0 <= rx_px < img_size and 0 <= ry_px < img_size:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if 0 <= rx_px+dx < img_size and 0 <= ry_px+dy < img_size:
                    pixels[rx_px+dx, ry_px+dy] = (255, 0, 0)  # red dot
        dx = int(10 * math.cos(theta))
        dy = int(10 * math.sin(theta))
        if 0 <= rx_px+dx < img_size and 0 <= ry_px+dy < img_size:
            for i in range(3):
                if 0 <= rx_px+dx+i < img_size and 0 <= ry_px+dy+i < img_size:
                    pixels[rx_px+dx+i, ry_px+dy+i] = (0, 0, 255)  # blue arrow

        # Hiển thị ảnh
    canvas.update_idletasks()
    width = canvas.winfo_width()
    height = canvas.winfo_height()    
    img = img.resize((width, height), Image.NEAREST)
    tk_img = ImageTk.PhotoImage(img)
    canvas.image = tk_img  # giữ tham chiếu tránh bị xoá
    canvas.delete("all")

    # Tính tọa độ để vẽ ở giữa canvas
    img_width = tk_img.width()
    img_height = tk_img.height()
    x = (width - img_width) // 2
    y = (height - img_height) // 2

    canvas.create_image(x, y, anchor="nw", image=tk_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
