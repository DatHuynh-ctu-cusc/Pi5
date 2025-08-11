import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import json, math

from encoder_handler import set_offset, get_robot_pose
from lidar_receiver import register_lidar_callback
from lidar_map_drawer import world_to_pixel, MAP_SCALE, MAP_SIZE_PIXELS

class MapTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        self.app = app
        self.last_lidar_scan = None
        self.ogm_set = set()
        self.map_image_pil = None
        self.map_canvas_image = None
        self.robot_pose = None
        self.path_points = []
        self.drawing_path_mode = False

        tk.Label(self, text="CHẾ ĐỘ HIỂN THỬa BẢN ĐỒ", font=("Arial", 20, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=10)

        self.main_map = tk.Canvas(self, width=700, height=400,
                                  bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.main_map.pack(pady=5)
        self.main_map.bind("<Button-1>", self.on_canvas_click)

        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(fill="x", pady=10)

        tk.Button(button_frame, text="📂 Chọn bản đồ",
                  font=("Arial", 11), command=self.select_map).pack(side="left", padx=5)
        tk.Button(button_frame, text="🧹 Xóa bản đồ",
                  font=("Arial", 11), command=self.clear_map).pack(side="left", padx=5)
        tk.Button(button_frame, text="📍 Định vị robot",
                  font=("Arial", 11), command=self.locate_robot).pack(side="left", padx=5)
        tk.Button(button_frame, text="✏️ Vẽ đường đi",
                  font=("Arial", 11), command=self.toggle_draw_path_mode).pack(side="left", padx=5)
        tk.Button(button_frame, text="❌ Xóa đường đi",
                  font=("Arial", 11), command=self.clear_path).pack(side="left", padx=5)
        tk.Button(button_frame, text="📤 Gửi đường đi",
                  font=("Arial", 11), command=self.send_path_to_pi4).pack(side="left", padx=5)

        register_lidar_callback(self.on_lidar_data)
        self.update_robot_position_loop()

    def on_lidar_data(self, data):
        self.last_lidar_scan = data

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
        self.robot_pose = None
        self.path_points.clear()
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

            def compute_score(scan_pts, ogm, tx, ty, theta):
                cos_t, sin_t = math.cos(theta), math.sin(theta)
                score = 0
                for x, y in scan_pts:
                    x_map = x * cos_t - y * sin_t + tx
                    y_map = x * sin_t + y * cos_t + ty
                    px = int(x_map * MAP_SCALE + MAP_SIZE_PIXELS // 2)
                    py = int(MAP_SIZE_PIXELS // 2 - y_map * MAP_SCALE)
                    if (px, py) in ogm:
                        score += 1
                return score

            scan_points = scan_to_points(self.last_lidar_scan)
            _, _, lidar_heading, *_ = get_robot_pose()

            best_pose = None
            best_score = -1
            step = 0.1
            search_range = 10

            for dx in range(-search_range, search_range + 1):
                tx = dx * step
                for dy in range(-search_range, search_range + 1):
                    ty = dy * step
                    theta = lidar_heading
                    score = compute_score(scan_points, self.ogm_set, tx, ty, theta)
                    if score > best_score:
                        best_score = score
                        best_pose = (tx, ty, theta)

            if best_pose:
                set_offset(*best_pose)
                print(f"📍 Định vị: x={best_pose[0]:.2f}, y={best_pose[1]:.2f}, θ={math.degrees(best_pose[2]):.1f}°")
            else:
                print("❌ Không tìm được vị trí phù hợp.")

    def update_robot_position_loop(self):
        if self.robot_pose is not None:
            self.robot_pose = get_robot_pose()
            self.draw_robot_and_path()
        self.after(200, self.update_robot_position_loop)  # gọi lại mỗi 200ms

    def draw_robot_and_path(self):
        if not self.map_image_pil:
            return
        img = self.map_image_pil.copy()
        draw = ImageDraw.Draw(img)

        x, y, theta, *_ = get_robot_pose()
        px, py = world_to_pixel(x, y)
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill="red")
        arrow_len = 20
        arrow_x = px + arrow_len * math.cos(theta)
        arrow_y = py - arrow_len * math.sin(theta)
        draw.line((px, py, arrow_x, arrow_y), fill="green", width=2)

        path = [(x, y)] + self.path_points
        for i in range(len(path) - 1):
            p1 = world_to_pixel(*path[i])
            p2 = world_to_pixel(*path[i + 1])
            draw.line((*p1, *p2), fill="blue", width=2)
            draw.ellipse((p2[0] - 3, p2[1] - 3, p2[0] + 3, p2[1] + 3), fill="blue")

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

    def update_robot_position_loop(self):
        if self.map_image_pil:
            self.draw_robot_and_path()
        self.after(200, self.update_robot_position_loop)

    def toggle_draw_path_mode(self):
        self.drawing_path_mode = not self.drawing_path_mode
        status = "Bật" if self.drawing_path_mode else "Tắt"
        print(f"✏️ Chế độ vẽ đường đi: {status}")

    def on_canvas_click(self, event):
        if not self.drawing_path_mode or not self.map_image_pil:
            return
        w, h = self.main_map.winfo_width(), self.main_map.winfo_height()
        img_x = int(event.x * MAP_SIZE_PIXELS / w)
        img_y = int(event.y * MAP_SIZE_PIXELS / h)
        x_m = (img_x - MAP_SIZE_PIXELS // 2) / MAP_SCALE
        y_m = (MAP_SIZE_PIXELS // 2 - img_y) / MAP_SCALE
        self.path_points.append((x_m, y_m))
        print(f"➕ Thêm điểm đích: ({x_m:.2f}, {y_m:.2f})")

    def clear_path(self):
        self.path_points.clear()
        print("🧹 Đã xóa đường đi.")

    def send_path_to_pi4(self):
        if not self.app.bt_client or not self.path_points:
            print("⚠️ Chưa có kết nối Bluetooth hoặc chưa vẽ đường đi.")
            return

        x, y, theta, *_ = get_robot_pose()
        commands = []

        for (tx, ty) in self.path_points:
            dx = tx - x
            dy = ty - y
            distance = math.hypot(dx, dy)
            angle_target = math.atan2(dy, dx)
            angle_diff = (angle_target - theta + math.pi) % (2 * math.pi) - math.pi
            deg = round(math.degrees(angle_diff), 1)

            if abs(deg) > 5:
                direction = "left" if deg > 0 else "right"
                commands.append(f"{direction} {abs(deg):.1f}")
                theta += math.radians(deg)

            if distance > 0.05:
                commands.append(f"forward {distance:.2f}")
                x, y = tx, ty

        if commands:
            script = "\n".join(commands) + "\n"
            print("📤 Lệnh gửi tới Pi4:\n" + script)
            self.app.bt_client.send(script)
        else:
            print("⚠️ Không có lệnh hợp lệ để gửi.")
