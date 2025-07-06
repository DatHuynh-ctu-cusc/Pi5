# app.py
import os
import tkinter as tk 
import threading
import numpy as np
from encoder_handler import positions, get_robot_pose
from lidar_map_drawer import update_ogm_map, draw_ogm_on_canvas, draw_zoomed_lidar_map
from PIL import Image, ImageTk
import time
import math
from tkinter import filedialog
from PIL import Image, ImageTk



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
        os.makedirs("/home/dat/LuanVan/maps", exist_ok=True)
        self.loaded_map_image = None  # ảnh bản đồ đã chọn


    def save_scan_map(self):
        try:
            img_size = self.ogm_map_scan.shape[0]
            img = Image.new("RGB", (img_size, img_size), "gray")
            pixels = img.load()
            for y in range(img_size):
                for x in range(img_size):
                    v = self.ogm_map_scan[y, x]
                    if v == 1:
                        pixels[x, y] = (255, 255, 255)
                    elif v == 2:
                        pixels[x, y] = (0, 0, 0)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = f"/home/dat/LuanVan/maps/map_{timestamp}.png"
            img.save(path)
            print(f"[App] ✅ Đã lưu bản đồ quét tại: {path}")
            self.update_folder_tab()  # Cập nhật lại danh sách
        except Exception as e:
            print("[App] ❌ Lỗi khi lưu bản đồ quét:", e)


    def clear_scan_map(self):
            self.ogm_map_scan.fill(0)
            if self.scan_canvas and self.scan_canvas.winfo_exists():
                draw_ogm_scan_canvas(self.scan_canvas, self.ogm_map_scan, self.robot_pose)
            print("[App] 🔄 Đã làm mới bản đồ quét")

    def update_folder_tab(self):
        if not hasattr(self, 'folder_frame') or not self.folder_frame:
            return

        for widget in self.folder_frame.winfo_children():
            widget.destroy()

        try:
            files = sorted(
                [f for f in os.listdir("/home/dat/LuanVan/maps") if f.endswith(".png")],
                reverse=True
            )
            if not files:
                tk.Label(self.folder_frame, text="❌ Chưa có bản đồ nào", bg="white", font=("Arial", 12)).pack()
                return

            for fname in files:
                path = os.path.join("/home/dat/LuanVan/maps", fname)
                frame = tk.Frame(self.folder_frame, bg="white", padx=5, pady=5)
                frame.pack(anchor="w", fill="x")

                img = Image.open(path).resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(frame, image=img_tk)
                lbl_img.image = img_tk
                lbl_img.pack(side="left")

                lbl_name = tk.Label(frame, text=fname, bg="white", font=("Arial", 11))
                lbl_name.pack(side="left", padx=10)
        except Exception as e:
            print("[App] ❌ Lỗi khi cập nhật thư mục bản đồ:", e)



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

        self.choose_map_btn = tk.Button(btn_frame, text="Chọn bản đồ", width=15, command=self.choose_map_file)
        self.choose_map_btn.pack(pady=5)


        if self.loaded_map_image:
            try:
                img = self.loaded_map_image.resize((self.main_map_canvas.winfo_width(), self.main_map_canvas.winfo_height()), Image.NEAREST)
                tk_img = ImageTk.PhotoImage(img)
                self.main_map_canvas.image = tk_img
                self.main_map_canvas.create_image(0, 0, anchor="nw", image=tk_img)
            except Exception as e:
                print("[App] ❌ Không thể hiển thị bản đồ đã chọn:", e)

    def choose_map_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file bản đồ",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                from PIL import Image
                self.loaded_map_image = Image.open(file_path)
                self.show_map()  # cập nhật lại canvas hiển thị
                print(f"[App] ✅ Đã chọn bản đồ: {file_path}")
            except Exception as e:
                print(f"[App] ❌ Không thể mở bản đồ: {e}")


    def show_scan_map(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.content, bg="white")
        frame.pack(fill="both", expand=True)

        # === Canvas bản đồ quét ===
        self.scan_canvas = tk.Canvas(frame, bg="white")
        self.scan_canvas.pack(expand=True, fill="both")

        # === Nút chức năng ===
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(fill="x", pady=10)

        save_btn = tk.Button(btn_frame, text="💾 Lưu bản đồ", font=("Arial", 11), command=self.save_scan_map)
        save_btn.pack(side="left", padx=10)

        clear_btn = tk.Button(btn_frame, text="🔄 Làm mới", font=("Arial", 11), command=self.clear_scan_map)
        clear_btn.pack(side="left", padx=10)


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
        for widget in self.content.winfo_children():
            widget.destroy()

        title = tk.Label(self.content, text="\U0001F4C2 BẢN ĐỒ ĐÃ LƯU", font=("Arial", 20), bg="white")
        title.pack(pady=10)

        load_btn = tk.Button(self.content, text="🗂 Chọn bản đồ từ thư mục", command=self.load_map_from_file)
        load_btn.pack(pady=10)

        self.map_preview_canvas = tk.Canvas(self.content, bg="white", width=400, height=400)
        self.map_preview_canvas.pack(pady=10)

    def load_map_from_file(self):
        file_path = filedialog.askopenfilename(
            initialdir="/home/dat/LuanVan/maps",
            title="Chọn bản đồ",
            filetypes=[("PNG files", "*.png")]
        )
        if file_path:
            try:
                img = Image.open(file_path)
                self.loaded_map_image = img  # Lưu lại ảnh để dùng lại
                img_resized = img.resize((400, 400), Image.NEAREST)
                tk_img = ImageTk.PhotoImage(img_resized)
                self.map_preview_canvas.image = tk_img
                self.map_preview_canvas.delete("all")
                self.map_preview_canvas.create_image(0, 0, anchor="nw", image=tk_img)
                print(f"[App] ✅ Đã chọn bản đồ: {file_path}")
            except Exception as e:
                print("[App] ❌ Lỗi khi tải ảnh bản đồ:", e)

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
