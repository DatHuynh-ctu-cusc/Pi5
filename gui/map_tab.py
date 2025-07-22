import json
import math
import tkinter as tk
from tkinter import Image, filedialog, messagebox
from lidar_map_drawer import draw_lidar_on_canvas, reset_lidar_map
from encoder_handler import get_robot_pose
from lidar_map_drawer import world_to_pixel, MAP_SIZE_PIXELS, MAP_SCALE

class MapTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        self.app = app  # để gọi sang app khi cần
        self.ogm_set = set()
        self.path_lines = []
        self.robot_goal = None
        self.robot_start = None

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
        tk.Button(control_frame, text="🎯 Đích đến", font=("Arial", 11), width=20, command=self.set_goal_point).pack(pady=4)

        self.robot_status_label = tk.Label(control_frame, text="Trạng thái: Di chuyển", font=("Arial", 11, "bold"),
                                           bg="green", fg="white", width=20)
        self.robot_status_label.pack(pady=10)

        # === Các hàm xử lý tab bản đồ ===
    def select_map(self):
        import os, json, math, time
        from tkinter import filedialog
        from PIL import ImageTk, ImageDraw, Image
        from lidar_map_drawer import (
            MAP_SIZE_PIXELS, MAP_SCALE,
            reset_lidar_map, global_map_image, global_draw, drawn_points
        )

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

            # Lưu lại OGM set để callback khác có thể dùng
            self.ogm_set = ogm_set

            # --- Lấy LiDAR scan mới nhất ---
            scan = getattr(self, "last_lidar_scan", None)
            print("DEBUG | LiDAR scan nhận được:", scan)
            if scan and isinstance(scan, dict) and "ranges" in scan:
                best_x, best_y, best_theta = find_best_pose(scan, ogm_set)
                px = int(best_x * MAP_SCALE + MAP_SIZE_PIXELS // 2)
                py = int(MAP_SIZE_PIXELS // 2 - best_y * MAP_SCALE)
                global_draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill="red")
                print(f"📍 Đã vẽ vị trí robot lên OGM tại ({px}, {py}) (m: {best_x:.2f}, {best_y:.2f})")
            else:
                print("⚠️ Chưa có vòng quét LiDAR để định vị robot!")
                print("⚠️ Gợi ý: Chạy robot Pi4, đợi nhận dữ liệu LiDAR, rồi bấm lại 'Chọn bản đồ'.")

            # Hiển thị lại ảnh lên canvas
            img_resized = global_map_image.resize((canvas.winfo_width(), canvas.winfo_height()))
            tk_img = ImageTk.PhotoImage(img_resized)
            canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img
            self.lidar_image = global_map_image.copy()

        except Exception as e:
            print(f"❌ Lỗi khi đọc hoặc xử lý JSON: {e}")



    def clear_map(self):
        print("🗑 Đã xoá bản đồ chính!")
        # Xoá toàn bộ đối tượng trên canvas bản đồ chính 
        if hasattr(self, "main_map"):
            self.main_map.delete("all")
        # Xoá biến lưu ảnh bản đồ chính trong app
        self.map_image = None
        self.lidar_image = None
        self.last_lidar_data = None
        # Reset lại bản đồ tích lũy (nếu bạn dùng ảnh toàn cục vẽ tích lũy)
        from lidar_map_drawer import reset_lidar_map
        reset_lidar_map(self.main_map)
        # Thông báo popup cho user
        from tkinter import messagebox
        messagebox.showinfo("Xoá bản đồ", "Bản đồ chính đã được xoá khỏi giao diện.")



    def draw_path(self):
        from encoder_handler import get_robot_pose
        from lidar_map_drawer import world_to_pixel, MAP_SIZE_PIXELS
        import math

        canvas = self.main_map
        if not canvas or not hasattr(self, "ogm_set"):
            print("⚠️ Chưa có bản đồ OGM để vẽ đường.")
            return

        # 1. Xóa overlay cũ nếu có
        if hasattr(self, "path_items"):
            for item in self.path_items:
                canvas.delete(item)
        self.path_items = []

        # 2. Lấy vị trí robot hiện tại (tính theo encoder)
        try:
            x, y, theta = get_robot_pose()[:3]
        except Exception as e:
            print("❌ Không thể lấy vị trí robot từ encoder:", e)
            return

        # 3. Chuyển sang pixel ảnh → pixel canvas
        px, py = world_to_pixel(x, y)
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        cx = px * canvas_w / MAP_SIZE_PIXELS
        cy = py * canvas_h / MAP_SIZE_PIXELS

        # 4. Vẽ điểm đầu (màu đỏ) và lưu lại
        r = 4
        dot = canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="red", outline="")
        self.path_items = [dot]
        self._last_path_xy = (cx, cy)

        print(f"🚩 Vị trí robot bắt đầu: ({x:.2f}, {y:.2f}) → canvas ({cx:.1f}, {cy:.1f})")
        print("✏️ Click từng điểm trên bản đồ để nối đường đi...")

        # 5. Gắn sự kiện click vào canvas
        def on_canvas_click(event):
            x1, y1 = self._last_path_xy
            x2, y2 = event.x, event.y

            # Vẽ đoạn thẳng
            line = canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
            # Vẽ điểm tròn
            dot = canvas.create_oval(x2 - 3, y2 - 3, x2 + 3, y2 + 3, fill="green", outline="")

            self.path_items += [line, dot]
            self._last_path_xy = (x2, y2)

            print(f"➕ Đã thêm điểm ({x2}, {y2}) trên canvas")

        # 6. Kết nối sự kiện click chuột
        canvas.bind("<Button-1>", on_canvas_click)



    def draw_robot_pose(x, y, theta, draw_obj):
        px, py = world_to_pixel(x, y)

        # Vẽ thân robot (chấm đỏ)
        draw_obj.ellipse((px - 5, py - 5, px + 5, py + 5), fill="red")

        # Vẽ mũi tên chỉ hướng robot
        arrow_len = 20
        end_x = px + arrow_len * math.cos(theta)
        end_y = py - arrow_len * math.sin(theta)  # Trục y đảo
        draw_obj.line((px, py, end_x, end_y), fill="green", width=2)




    def set_goal_point(self):
        print("🔴 Hãy click vào bản đồ để chọn vị trí đích đến.")

        def on_click(event):
            canvas = self.main_map

            # Kiểm tra canvas hợp lệ
            if not canvas or not canvas.winfo_exists():
                print("⚠️ Không tìm thấy canvas bản đồ.")
                return

            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Vị trí pixel click
            click_x = event.x
            click_y = event.y

            # Chuyển sang toạ độ thực tế (mét)
            from lidar_map_drawer import MAP_SCALE, MAP_SIZE_PIXELS

            x_pixel = (click_x / canvas_width) * MAP_SIZE_PIXELS
            y_pixel = (click_y / canvas_height) * MAP_SIZE_PIXELS

            real_x = (x_pixel - MAP_SIZE_PIXELS / 2) / MAP_SCALE
            real_y = (MAP_SIZE_PIXELS / 2 - y_pixel) / MAP_SCALE

            # Lưu lại vị trí đích
            self.robot_goal = (real_x, real_y)
            print(f"🎯 Đích đến được đặt tại: x = {real_x:.2f} m, y = {real_y:.2f} m")

            # Xóa điểm cũ nếu có
            if hasattr(self, "goal_dot"):
                canvas.delete(self.goal_dot)

            # Vẽ điểm đỏ tại vị trí chuột
            r = 5
            self.goal_dot = canvas.create_oval(click_x - r, click_y - r, click_x + r, click_y + r,
                                            fill="red", outline="black")

            # Hủy bắt sự kiện sau khi click
            canvas.unbind("<Button-1>")

        # Bắt đầu lắng nghe click chuột trái
        self.main_map.bind("<Button-1>", on_click)

    def clear_path(self):
        if not hasattr(self, "main_map"):
            print("⚠️ Không tìm thấy canvas để xoá đường đi.")
            return

        # Xoá các đoạn line đường đi đã lưu
        for line in getattr(self, "path_lines", []):
            self.main_map.delete(line)
        self.path_lines = []

        if hasattr(self, "goal_dot"):
            self.main_map.delete(self.goal_dot)
            del self.goal_dot

        # Xoá biến vị trí start/goal nếu muốn (tùy bạn)
        self.robot_start = None
        self.robot_goal = None
        print("🧹 Đã xoá đường đi.")

    def update_robot_position_on_loaded_map(self):
            from lidar_map_drawer import draw_robot_realtime
            if hasattr(self, "lidar_image") and hasattr(self, "main_map"):
                draw_robot_realtime(self.main_map, self.lidar_image)
            if hasattr(self, "root"):
                self.root.after(300, self.update_robot_position_on_loaded_map)

    def show_png_on_map(self, file_path):
        try:
            image = Image.open(file_path)
            image = image.resize((680, 300), Image.Resampling.LANCZOS)
            self.map_image = Image.PhotoImage(image)
            # XÓA CANVAS trước khi vẽ mới (cực kỳ quan trọng!)
            self.main_map.delete("all")
            # LUÔN tạo lại image mới!
            self.main_map.create_image(0, 0, anchor="nw", image=self.map_image)
            print(f"🖼 Đã chọn bản đồ: {file_path}")
        except Exception as e:
            print("❌ Lỗi khi mở bản đồ PNG:", e)

    def draw_ogm_from_json(self, data):
            from lidar_map_drawer import global_map_image, global_draw, drawn_points, MAP_SIZE_PIXELS
            from PIL import ImageTk

            if "occupied_points" not in data:
                print("⚠️ Không có dữ liệu occupied_points!")
                return

            self.ogm_set = set(tuple(p) for p in data["occupied_points"])
            reset_lidar_map(self.main_map)
            drawn_points.clear()

            for px, py in self.ogm_set:
                if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                    global_draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="black")
                    drawn_points.add((px, py))

            img_resized = global_map_image.resize((self.main_map.winfo_width(), self.main_map.winfo_height()))
            tk_img = ImageTk.PhotoImage(img_resized)
            self.main_map.map_image = self.main_map.create_image(0, 0, anchor="nw", image=tk_img)
            self.main_map.image = tk_img

            self.lidar_image = global_map_image.copy()
            print("✅ Đã hiển thị bản đồ OGM.")
            

    def load_lidar_map_from_file(self, json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
        # Chuyển None (trong ranges) thành math.inf để tái sử dụng vẽ lại
        ranges = []
        for v in data["ranges"]:
            if v is None:
                ranges.append(float("inf"))
            else:
                ranges.append(v)
        data["ranges"] = ranges

        # Vẽ lại lên canvas
        if hasattr(self, "scan_canvas") and self.scan_canvas.winfo_exists():
            draw_lidar_on_canvas(self.scan_canvas, data)
            print(f"[App] 🖼️ Đã tải lại bản đồ từ: {json_path}")
        # Nếu muốn lưu lại vào self.last_lidar_data cũng được:
        self.last_lidar_data = data        

    def update_robot_status(self, status):
        if status == "moving":
            self.robot_status_label.config(text="Trạng thái: Di chuyển", bg="green")
        elif status == "stuck":
            self.robot_status_label.config(text="Trạng thái: Mắc kẹt", bg="red")

