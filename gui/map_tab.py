import json
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from encoder_handler import get_robot_pose
from lidar_map_drawer import draw_lidar_on_canvas, reset_lidar_map, global_map_image, global_draw, drawn_points
from lidar_map_drawer import world_to_pixel, MAP_SIZE_PIXELS, MAP_SCALE
from PIL import ImageTk, Image

class MapTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        self.app = app
        self.ogm_set = set()
        self.path_lines = []
        self.robot_goal = None
        self.robot_start = None
        self.last_lidar_scan = None

        tk.Label(self, text="BẢN ĐỒ HOẠT ĐỘNG CỦA ROBOT",
                 font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # Main map canvas
        self.main_map = tk.Canvas(self, width=680, height=300, bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.main_map.pack(pady=5)

        # Bottom: sub-map + control frame
        bottom_frame = tk.Frame(self, bg="white")
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.sub_map = tk.Canvas(bottom_frame, width=300, height=200, bg="#dfe6e9", highlightbackground="#bdc3c7")
        self.sub_map.pack(side="left", padx=5)

        control_frame = tk.Frame(bottom_frame, bg="white")
        control_frame.pack(side="left", fill="both", expand=True, padx=10)

        tk.Button(control_frame, text="🗂 Chọn bản đồ", font=("Arial", 11), width=20, command=self.select_map).pack(pady=4)
        tk.Button(control_frame, text="🗑 Xoá bản đồ", font=("Arial", 11), width=20, command=self.clear_map).pack(pady=4)
        tk.Button(control_frame, text="✏️ Vẽ đường đi", font=("Arial", 11), width=20, command=self.draw_path).pack(pady=4)
        tk.Button(control_frame, text="❌ Xoá đường đi", font=("Arial", 11), width=20, command=self.clear_path).pack(pady=4)
        tk.Button(control_frame, text="📍 Định vị robot", font=("Arial", 11), width=20, command=self.locate_robot).pack(pady=4)

        self.robot_status_label = tk.Label(control_frame, text="Trạng thái: Di chuyển", font=("Arial", 11, "bold"),
                                           bg="green", fg="white", width=20)
        self.robot_status_label.pack(pady=10)
        self.lidar_status_label = tk.Label(
            control_frame,
            text="Chưa có dữ liệu LiDAR",
            font=("Arial", 11, "bold"),
            bg="gray", fg="white", width=20
        )
        self.lidar_status_label.pack(pady=4)  

    def on_lidar_data(self, lidar_data):
        # Lưu lại LiDAR mới nhất
        print("[MAPTAB] Đã nhận được LiDAR scan mới!")
        self.last_lidar_scan = lidar_data

    def select_map(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Map or Scan", "*.json")]
        )
        if not file_path:
            return

        canvas = getattr(self, "main_map", None)
        if canvas:
            canvas.delete("all")
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            if "occupied_points" not in data:
                print("⚠️ File JSON không chứa bản đồ OGM!")
                return

            reset_lidar_map(canvas)
            drawn_points.clear()
            ogm_set = set(tuple(p) for p in data["occupied_points"])
            for px, py in ogm_set:
                if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                    global_draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="black")
                    drawn_points.add((px, py))
            print("✅ Đã hiển thị bản đồ OGM.")

            self.ogm_set = ogm_set

            scan = getattr(self, "last_lidar_scan", None)
            print("DEBUG | LiDAR scan nhận được:", scan)
            if scan and isinstance(scan, dict) and "ranges" in scan:
                self.locate_robot()  # Tự động định vị robot nếu có scan
            else:
                print("⚠️ Chưa có vòng quét LiDAR để định vị robot!")
                print("⚠️ Gợi ý: Chạy robot Pi4, đợi nhận dữ liệu LiDAR, rồi bấm lại 'Chọn bản đồ'.")

            img_resized = global_map_image.resize((canvas.winfo_width(), canvas.winfo_height()))
            tk_img = ImageTk.PhotoImage(img_resized)
            canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img
            self.lidar_image = global_map_image.copy()

        except Exception as e:
            print(f"❌ Lỗi khi đọc hoặc xử lý JSON: {e}")

    def clear_map(self):
        print("🗑 Đã xoá bản đồ chính!")
        if hasattr(self, "main_map"):
            self.main_map.delete("all")
        self.map_image = None
        self.lidar_image = None
        self.last_lidar_data = None
        reset_lidar_map(self.main_map)
        messagebox.showinfo("Xoá bản đồ", "Bản đồ chính đã được xoá khỏi giao diện.")

    def draw_path(self):

        canvas = self.main_map
        if not canvas or not hasattr(self, "ogm_set"):
            print("⚠️ Chưa có bản đồ OGM để vẽ đường.")
            return

        if hasattr(self, "path_items"):
            for item in self.path_items:
                canvas.delete(item)
        self.path_items = []

        try:
            x, y, theta = get_robot_pose()[:3]
        except Exception as e:
            print("❌ Không thể lấy vị trí robot từ encoder:", e)
            return

        px, py = world_to_pixel(x, y)
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        cx = px * canvas_w / MAP_SIZE_PIXELS
        cy = py * canvas_h / MAP_SIZE_PIXELS

        r = 4
        dot = canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="red", outline="")
        self.path_items = [dot]
        self._last_path_xy = (cx, cy)

        print(f"🚩 Vị trí robot bắt đầu: ({x:.2f}, {y:.2f}) → canvas ({cx:.1f}, {cy:.1f})")
        print("✏️ Click từng điểm trên bản đồ để nối đường đi...")

        def on_canvas_click(event):
            x1, y1 = self._last_path_xy
            x2, y2 = event.x, event.y

            line = canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
            dot = canvas.create_oval(x2 - 3, y2 - 3, x2 + 3, y2 + 3, fill="green", outline="")
            self.path_items += [line, dot]
            self._last_path_xy = (x2, y2)
            print(f"➕ Đã thêm điểm ({x2}, {y2}) trên canvas")

        canvas.bind("<Button-1>", on_canvas_click)

    def clear_path(self):
        if not hasattr(self, "main_map"):
            print("⚠️ Không tìm thấy canvas để xoá đường đi.")
            return
        for line in getattr(self, "path_lines", []):
            self.main_map.delete(line)
        self.path_lines = []

        if hasattr(self, "goal_dot"):
            self.main_map.delete(self.goal_dot)
            del self.goal_dot
        self.robot_start = None
        self.robot_goal = None
        print("🧹 Đã xoá đường đi.")

    def locate_robot(self):
        if not hasattr(self, "ogm_set") or not self.ogm_set:
            print("⚠️ Chưa có bản đồ OGM để định vị!")
            return
        scan = getattr(self, "last_lidar_scan", None)
        if not scan or "ranges" not in scan:
            print("⚠️ Chưa có dữ liệu LiDAR scan!")
            if hasattr(self, "lidar_status_label"):
                self.lidar_status_label.config(text="Chưa có dữ liệu LiDAR", bg="red")
            return

        def frange(start, stop, step):
            while start <= stop:
                yield start
                start += step

        def scan_to_points(scan_data):
            angle = scan_data["angle_min"]
            angle_inc = scan_data["angle_increment"]
            ranges = scan_data["ranges"]
            points = []
            for r in ranges:
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

        def find_best_pose(scan_data, ogm_set):
            scan_points = scan_to_points(scan_data)
            best_score = -1
            best_pose = (0, 0, 0)
            for tx in frange(-2, 2, 0.1):
                for ty in frange(-2, 2, 0.1):
                    for theta in frange(-math.pi, math.pi, math.radians(15)):
                        score = compute_matching_score(scan_points, ogm_set, tx, ty, theta)
                        if score > best_score:
                            best_score = score
                            best_pose = (tx, ty, theta)
            print(f"✅ Best match: {best_pose} với score = {best_score}")
            return best_pose

        best_x, best_y, best_theta = find_best_pose(scan, self.ogm_set)
        px = int(best_x * MAP_SCALE + MAP_SIZE_PIXELS // 2)
        py = int(MAP_SIZE_PIXELS // 2 - best_y * MAP_SCALE)
        global_draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill="red")
        print(f"📍 Đã định vị robot tại ({px}, {py}) (m: {best_x:.2f}, {best_y:.2f})")

        canvas = getattr(self, "main_map", None)
        if canvas:
            img_resized = global_map_image.resize((canvas.winfo_width(), canvas.winfo_height()))
            tk_img = ImageTk.PhotoImage(img_resized)
            canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img
            self.lidar_image = global_map_image.copy()

        self.robot_start = (best_x, best_y)
        self.start_theta = best_theta

        # Định vị xong: chuyển label xanh
        if hasattr(self, "lidar_status_label"):
            self.lidar_status_label.config(text="Đã nhận dữ liệu LiDAR", bg="green")

        messagebox.showinfo("Định vị robot", f"Robot đã được định vị tại ({best_x:.2f} m, {best_y:.2f} m)")

    def update_robot_status(self, status):
        if status == "moving":
            self.robot_status_label.config(text="Trạng thái: Di chuyển", bg="green")
        elif status == "stuck":
            self.robot_status_label.config(text="Trạng thái: Mắc kẹt", bg="red")
