import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import json, math
import numpy as np

from encoder_handler import set_offset
from lidar_receiver import register_lidar_callback
from lidar_map_drawer import world_to_pixel, MAP_SCALE, MAP_SIZE_PIXELS  # ✅ dùng lại tiện ích

class MapTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        self.app = app
        self.last_lidar_scan = None
        self.ogm_set = set()
        self.map_image_pil = None
        self.map_canvas_image = None

        tk.Label(self, text="CHẾ ĐỘ HIỂN THỊ BẢN ĐỒ", font=("Arial", 20, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=10)

        self.main_map = tk.Canvas(self, width=700, height=400,
                                  bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.main_map.pack(pady=5)

        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(fill="x", pady=10)

        tk.Button(button_frame, text="📂 Chọn bản đồ",
                  font=("Arial", 11), command=self.select_map).pack(side="left", padx=10)
        tk.Button(button_frame, text="🧹 Xóa bản đồ",
                  font=("Arial", 11), command=self.clear_map).pack(side="left", padx=10)
        tk.Button(button_frame, text="📍 Định vị robot",
                  font=("Arial", 11), command=self.locate_robot).pack(side="left", padx=10)

        register_lidar_callback(self.on_lidar_data)

    def select_map(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Map", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            if "occupied_points" not in data:
                print("⚠️ File JSON không chứa bản đồ OGM!")
                return

            self.ogm_set = set(tuple(p) for p in data["occupied_points"])

            self.map_image_pil = Image.new("RGB", (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), "white")
            draw = ImageDraw.Draw(self.map_image_pil)
            for px, py in self.ogm_set:
                if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                    draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="black")

            self.render_map()
            print("✅ Đã hiển thị bản đồ JSON.")

            if self.last_lidar_scan:
                self.locate_robot()

        except Exception as e:
            print(f"❌ Lỗi khi đọc file JSON: {e}")

    def render_map(self):
        if not self.map_image_pil:
            return
        w, h = self.main_map.winfo_width(), self.main_map.winfo_height()
        if w < 10 or h < 10:
            return
        img = self.map_image_pil.resize((w, h))
        tk_img = ImageTk.PhotoImage(img)
        if self.map_canvas_image:
            self.main_map.itemconfig(self.map_canvas_image, image=tk_img)
        else:
            self.map_canvas_image = self.main_map.create_image(0, 0, anchor="nw", image=tk_img)
        self.main_map.image = tk_img

    def clear_map(self):
        self.main_map.delete("all")
        self.map_image_pil = None
        self.map_canvas_image = None
        self.ogm_set.clear()
        print("🧹 Đã xóa bản đồ.")

    def locate_robot(self):
        if not self.last_lidar_scan or not self.ogm_set or not self.map_image_pil:
            print("⚠️ Cần bản đồ JSON và dữ liệu LiDAR để định vị.")
            return

        def scan_to_points(scan):
            angle = scan["angle_min"]
            angle_inc = scan["angle_increment"]
            points = []
            for r in scan["ranges"]:
                if 0.1 < r < 6.0:
                    x = r * math.cos(angle)
                    y = r * math.sin(angle)
                    points.append((x, y))
                angle += angle_inc
            return points

        def compute_matching_score(scan_points, ogm_set, tx, ty, theta):
            score = 0
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            for x, y in scan_points:
                x_map = x * cos_t - y * sin_t + tx
                y_map = x * sin_t + y * cos_t + ty
                px = int(x_map * MAP_SCALE + MAP_SIZE_PIXELS // 2)
                py = int(MAP_SIZE_PIXELS // 2 - y_map * MAP_SCALE)
                if (px, py) in ogm_set:
                    score += 1
            return score

        scan_pts = scan_to_points(self.last_lidar_scan)
        best_score = -1
        best_pose = None

        step = 0.1  # bước 10 cm
        angle_step = math.radians(5)  # bước 5 độ
        search_range = 10  # ±10 * 0.1 = ±1m

        for dx in range(-search_range, search_range + 1):
            for dy in range(-search_range, search_range + 1):
                tx = dx * step
                ty = dy * step
                for dtheta in range(-18, 19):  # từ -90 đến +90 độ
                    theta = dtheta * angle_step
                    score = compute_matching_score(scan_pts, self.ogm_set, tx, ty, theta)
                    if score > best_score:
                        best_score = score
                        best_pose = (tx, ty, theta)

        if best_pose:
            set_offset(*best_pose)
            print(f"📍 Định vị: x={best_pose[0]:.2f} m, y={best_pose[1]:.2f} m, θ={math.degrees(best_pose[2]):.1f}°")
            self.draw_robot(*best_pose)
        else:
            print("❌ Không tìm được vị trí phù hợp.")


    def draw_robot(self, x, y, theta):
        if not self.map_image_pil:
            return
        img = self.map_image_pil.copy()
        draw = ImageDraw.Draw(img)
        px, py = world_to_pixel(x, y)
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill="red")
        arrow_len = 20
        arrow_x = px + arrow_len * math.cos(theta)
        arrow_y = py - arrow_len * math.sin(theta)
        draw.line((px, py, arrow_x, arrow_y), fill="green", width=2)

        w, h = self.main_map.winfo_width(), self.main_map.winfo_height()
        if w < 10 or h < 10:
            return
        resized = img.resize((w, h))
        tk_img = ImageTk.PhotoImage(resized)
        if self.map_canvas_image:
            self.main_map.itemconfig(self.map_canvas_image, image=tk_img)
        else:
            self.map_canvas_image = self.main_map.create_image(0, 0, anchor="nw", image=tk_img)
        self.main_map.image = tk_img

    def on_lidar_data(self, data):
        self.last_lidar_scan = data
