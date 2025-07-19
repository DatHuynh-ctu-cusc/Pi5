# app.py
import tkinter as tk
from PIL import Image, ImageTk
from lidar_map_drawer import draw_lidar_on_canvas, draw_zoomed_lidar_map, reset_lidar_map  # ✅ Import đúng hàm vẽ bản đồ
import datetime
import os
from tkinter import messagebox , filedialog
from bluetooth_client import BluetoothClient
from datetime import datetime
import json



def clean_lidar_data(data):
        import math
        d = dict(data)
        d["ranges"] = [None if (isinstance(v, float) and (math.isinf(v) or math.isnan(v))) else v for v in data["ranges"]]
        return d

class SimpleApp:
    def __init__(self, root, bt_client=None):
        self.root = root
        self.bt_client = bt_client
        self.root.title("App Robot")
        self.root.geometry("900x600")

        self.sidebar = tk.Frame(root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="📋 MENU", bg="#2c3e50", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=20)

        self.buttons = []
        self.active_button = None
        self.send_text = None
        self.recv_text = None

        self.add_sidebar_button("🏠 Trang chu", self.show_home)
        self.add_sidebar_button("🗺️ Ban do", self.show_map)
        self.add_sidebar_button("📶 Quet ban do", self.show_scan_map)
        self.add_sidebar_button("💾 Du lieu", self.show_data)
        self.add_sidebar_button("📁 Thu muc", self.show_folder)
        self.add_sidebar_button("🤖 Robot", self.show_robot)
        self.add_sidebar_button("🛠️ Cai dat", self.show_settings)

        self.main_content = tk.Frame(root, bg="white")
        self.main_content.pack(side="left", fill="both", expand=True)
                # Hiển thị mặc định là Trang chủ khi mở app
        self.show_home()


    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def add_sidebar_button(self, text, command):
        btn = tk.Label(self.sidebar, text=text, bg="#34495e", fg="white",
                       font=("Arial", 12), padx=10, pady=8, cursor="hand2")
        btn.pack(fill="x", padx=15, pady=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#1abc9c"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#34495e"))
        btn.bind("<Button-1>", lambda e: command())
        self.buttons.append(btn)

    def show_home(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="ĐỒ ÁN TỐT NGHIỆP",
                 font=("Arial", 24, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
        try:
            img = Image.open("bach_khoa.jpg")
            img = img.resize((600, 300), Image.Resampling.LANCZOS)
            self.home_image = ImageTk.PhotoImage(img)
            tk.Label(self.main_content, image=self.home_image, bg="white").pack(pady=10)
        except Exception as e:
            tk.Label(self.main_content, text=f"Lỗi ảnh: {e}", fg="red", bg="white").pack()

        topic_label = tk.Label(self.main_content,
                               text="HỆ THỐNG XE TỰ HÀNH TRÁNH VẬT CẢN DÙNG LIDAR",
                               font=("Arial", 14, "bold"), bg="white", fg="#34495e")
        topic_label.pack(pady=(10, 2))

        bottom_frame = tk.Frame(self.main_content, bg="white")
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

    def show_map(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="BẢN ĐỒ HOẠT ĐỘNG CỦA ROBOT",
                font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        self.main_map = tk.Canvas(self.main_content, width=680, height=300, bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.main_map.pack(pady=5)

        bottom_frame = tk.Frame(self.main_content, bg="white")
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.sub_map = tk.Canvas(bottom_frame, width=300, height=200, bg="#dfe6e9", highlightbackground="#bdc3c7")
        self.sub_map.pack(side="left", padx=5)

        control_frame = tk.Frame(bottom_frame, bg="white")
        control_frame.pack(side="left", fill="both", expand=True, padx=10)

        # === Các nút điều khiển ===
        tk.Button(control_frame, text="🗂 Chọn bản đồ", font=("Arial", 11), width=20, command=self.select_map).pack(pady=4)
        tk.Button(control_frame, text="🗑 Xoá bản đồ", font=("Arial", 11), width=20, command=self.clear_map).pack(pady=4)
        tk.Button(control_frame, text="✏️ Vẽ đường đi", font=("Arial", 11), width=20, command=self.draw_path).pack(pady=4)
        tk.Button(control_frame, text="❌ Xoá đường đi", font=("Arial", 11), width=20, command=self.clear_path).pack(pady=4)

        # === Hai nút mới ===
        tk.Button(control_frame, text="📍 Vị trí hiện tại", font=("Arial", 11), width=20, command=self.set_start_point).pack(pady=4)
        tk.Button(control_frame, text="🎯 Đích đến", font=("Arial", 11), width=20, command=self.set_goal_point).pack(pady=4)

        self.robot_status_label = tk.Label(control_frame, text="Trạng thái: Di chuyển", font=("Arial", 11, "bold"),
                                        bg="green", fg="white", width=20)
        self.robot_status_label.pack(pady=10)


    def show_scan_map(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="CHẾ ĐỘ QUÉT BẢN ĐỒ", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # Canvas để vẽ bản đồ quét
        self.scan_canvas = tk.Canvas(self.main_content, width=700, height=400, bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.scan_canvas.pack(pady=5)

        button_frame = tk.Frame(self.main_content, bg="white")
        button_frame.pack(fill="x", pady=(15, 10))
        tk.Button(button_frame, text="▶️ Bắt đầu", font=("Arial", 11), width=15, command=self.start_scan).pack(side="left", padx=10)
        tk.Button(button_frame, text="⏹ STOP", font=("Arial", 11, "bold"), width=12, fg="white", bg="red", command=self.stop_scan).pack(side="left", padx=10)
        tk.Button(button_frame, text="🔄 Làm mới bản đồ", font=("Arial", 11), width=18, command=self.refresh_scan_map).pack(side="left", padx=10)
        tk.Button(button_frame, text="💾 Lưu bản đồ", font=("Arial", 11), width=15, command=self.save_scan_map).pack(side="left", padx=10)

        self.scan_status_label = tk.Label(button_frame, text="Đang chờ...", width=20,
                                        font=("Arial", 11, "bold"), bg="gray", fg="white")
        self.scan_status_label.pack(side="left", padx=20)

    def stop_scan(self):
        print("⏹ Dừng quét bản đồ...")
        self.scan_status_label.config(text="Đã dừng", bg="gray")
        # Gửi lệnh STOP qua Bluetooth nếu đã kết nối
        if hasattr(self, "bt_client") and self.bt_client:
            self.bt_client.send("stop")  # Gửi lệnh dừng sang Pi4
        else:
            print("[App] ⚠️ Chưa có kết nối Bluetooth!")

    def start_scan(self):
        print("▶️ Bắt đầu quét bản đồ...")
        self.scan_status_label.config(text="Đang quét...", bg="red")
        # --- THÊM DÒNG NÀY ---
        if hasattr(self, "bt_client") and self.bt_client:
            self.bt_client.send("start_scan")  # gửi lệnh sang Pi4
        else:
            print("[App] ⚠️ Chưa có kết nối Bluetooth!")
    
    def update_lidar_map(self, lidar_data):
        global global_map_image
        if not isinstance(lidar_data, dict) or "ranges" not in lidar_data or not lidar_data["ranges"]:
            print("[App] ❌ Dữ liệu LiDAR không hợp lệ hoặc rỗng.")
            return
        try:
            print(f"[App] ✅ Cập nhật bản đồ với {len(lidar_data['ranges'])} điểm")
            # ----> Gán lại dữ liệu lidar cho lần lưu tiếp theo
            self.last_lidar_data = lidar_data.copy()

            # Nếu draw_lidar_on_canvas trả về ảnh PIL:
            if hasattr(self, "scan_canvas") and self.scan_canvas.winfo_exists():
                img = draw_lidar_on_canvas(self.scan_canvas, lidar_data)
                print("[DEBUG] img trả về từ draw_lidar_on_canvas:", type(img))
                if img is not None:
                    self.lidar_image = img    # <-- Gán ảnh PIL để lưu sau này

            # Vẽ bản đồ phụ nếu có
            if hasattr(self, "sub_map") and self.sub_map.winfo_exists():
                from lidar_map_drawer import draw_zoomed_lidar_map
                draw_zoomed_lidar_map(self.sub_map, lidar_data, radius=2.0)
        except Exception as e:
            print("[App] ⚠️ Lỗi khi vẽ bản đồ LiDAR:", e)
            return global_map_image

    def refresh_scan_map(self):
        print("🔄 Làm mới bản đồ...")
        reset_lidar_map(self.scan_canvas)  # ✅ reset ảnh tích lũy
        self.scan_status_label.config(text="Đang chờ...", bg="gray")

    def clean_lidar_data(self, data):
        import math
        clean = dict(data)
        clean_ranges = []
        for v in data.get("ranges", []):
            if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
                clean_ranges.append(None)
            else:
                clean_ranges.append(v)
        clean["ranges"] = clean_ranges
        return clean

    def save_scan_map(self):
        from datetime import datetime
        import os, json

        from lidar_map_drawer import global_map_image, drawn_points, MAP_SIZE_PIXELS, MAP_SCALE

        folder = "data/maps"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # --- Lưu ảnh PNG từ global_map_image ---
        img_filename = f"scan_map_{timestamp}.png"
        img_path = os.path.join(folder, img_filename)
        saved_img = False
        if global_map_image:
            try:
                global_map_image.save(img_path)
                print(f"💾 Đã lưu ảnh bản đồ vào: {img_path}")
                self.scan_status_label.config(text=f"Đã lưu: {img_filename}", bg="green")
                saved_img = True
            except Exception as e:
                print(f"[App] ⚠️ Lỗi khi lưu ảnh bản đồ: {e}")
                messagebox.showerror("Lỗi lưu ảnh", str(e))
        else:
            print("[App] ⚠️ Không tìm thấy ảnh bản đồ để lưu!")
            messagebox.showwarning("Thiếu ảnh", "Chưa có bản đồ hình ảnh để lưu.")

        # --- Lưu OGM thành JSON ---
        ogm_filename = f"scan_map_{timestamp}.json"
        ogm_path = os.path.join(folder, ogm_filename)
        saved_ogm = False
        try:
            ogm_data = {
                "size_pixels": MAP_SIZE_PIXELS,
                "scale": MAP_SCALE,
                "occupied_points": list(drawn_points)  # dạng [(x, y), ...]
            }
            with open(ogm_path, "w") as f:
                json.dump(ogm_data, f)
            print(f"💾 Đã lưu bản đồ OGM vào: {ogm_path}")
            saved_ogm = True
        except Exception as e:
            print(f"[App] ⚠️ Lỗi khi lưu dữ liệu OGM: {e}")
            messagebox.showerror("Lỗi lưu dữ liệu", str(e))

        # --- Thông báo trạng thái ---
        if saved_img and saved_ogm:
            print("[App] ✅ Đã lưu đầy đủ ảnh và OGM!")
            messagebox.showinfo("Thành công", "Đã lưu ảnh và bản đồ OGM!")
        elif not saved_img and not saved_ogm:
            self.scan_status_label.config(text=f"Lỗi khi lưu bản đồ!", bg="red")



    def select_map(self):
        import os, json
        from tkinter import filedialog
        from lidar_map_drawer import MAP_SIZE_PIXELS, reset_lidar_map
        from PIL import ImageTk, Image, ImageDraw

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Bản đồ (*.json, *.png)", "*.json *.png"),
                ("Dữ liệu quét LiDAR (*.json)", "*.json"),
                ("Ảnh bản đồ (*.png)", "*.png"),
                ("Tất cả các tệp", "*.*"),
            ]
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        canvas = getattr(self, "main_map", None)
        if canvas:
            canvas.delete("all")

        def show_png_on_map(png_path):
            try:
                img = Image.open(png_path)
                img_resized = img.resize((canvas.winfo_width(), canvas.winfo_height()))
                tk_img = ImageTk.PhotoImage(img_resized)
                canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
                canvas.image = tk_img
                print(f"🖼️ Hiển thị ảnh PNG: {png_path}")
            except Exception as e:
                print(f"❌ Lỗi hiển thị ảnh PNG: {e}")
        def draw_ogm_from_json(data):
            if "occupied_points" not in data:
                print("⚠️ File JSON không chứa dữ liệu OGM!")
                return

            # ✅ GÁN self.ogm_set TẠI ĐÂY
            self.ogm_set = set(tuple(p) for p in data["occupied_points"])

            # Reset bản đồ cũ
            reset_lidar_map(canvas)

            from lidar_map_drawer import global_map_image, global_draw, drawn_points

            for px, py in data["occupied_points"]:
                if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                    global_draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="black")
                    drawn_points.add((px, py))

            # Vẽ lại lên canvas
            img_resized = global_map_image.resize((canvas.winfo_width(), canvas.winfo_height()))
            tk_img = ImageTk.PhotoImage(img_resized)
            canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
            canvas.image = tk_img
            print("✅ Đã vẽ lại bản đồ OGM từ JSON.")

        def draw_lidar_scan(data):
            from lidar_map_drawer import draw_lidar_on_canvas
            for i, v in enumerate(data.get("ranges", [])):
                if v is None:
                    data["ranges"][i] = float("inf")
            img = draw_lidar_on_canvas(canvas, data)
            if img:
                self.lidar_image = img
                print(f"✅ Đã vẽ lại bản đồ từ dữ liệu quét LiDAR.")

        if ext == ".png":
            json_path = file_path.replace('.png', '.json')
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r") as f:
                        data = json.load(f)
                    if "occupied_points" in data:
                        draw_ogm_from_json(data)
                    elif "ranges" in data:
                        draw_lidar_scan(data)
                except Exception as e:
                    print(f"❌ Lỗi khi đọc file JSON đi kèm PNG: {e}")
                    show_png_on_map(file_path)
            else:
                show_png_on_map(file_path)

        elif ext == ".json":
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                if "occupied_points" in data:
                    draw_ogm_from_json(data)
                elif "ranges" in data:
                    draw_lidar_scan(data)
                else:
                    print("⚠️ File JSON không hợp lệ.")
            except Exception as e:
                print(f"❌ Lỗi khi đọc file JSON: {e}")
        else:
            print("⚠️ Chỉ hỗ trợ file PNG hoặc JSON!")


    def show_png_on_map(self, file_path):
        try:
            image = Image.open(file_path)
            image = image.resize((680, 300), Image.Resampling.LANCZOS)
            self.map_image = ImageTk.PhotoImage(image)
            # XÓA CANVAS trước khi vẽ mới (cực kỳ quan trọng!)
            self.main_map.delete("all")
            # LUÔN tạo lại image mới!
            self.main_map.create_image(0, 0, anchor="nw", image=self.map_image)
            print(f"🖼 Đã chọn bản đồ: {file_path}")
        except Exception as e:
            print("❌ Lỗi khi mở bản đồ PNG:", e)

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
        print("✏️ Vẽ đường đi")

        # === Kiểm tra đủ điều kiện ===
        if not hasattr(self, "robot_start") or not hasattr(self, "robot_goal"):
            print("⚠️ Bạn cần chọn cả vị trí hiện tại và đích đến trước.")
            return

        if not hasattr(self, "ogm_set") or not self.ogm_set:
            print("⚠️ Chưa có bản đồ OGM để tìm đường.")
            return

        from lidar_map_drawer import world_to_pixel, MAP_SIZE_PIXELS

        # === Chuyển tọa độ thực sang pixel OGM ===
        start_px, start_py = world_to_pixel(*self.robot_start)
        goal_px, goal_py = world_to_pixel(*self.robot_goal)

        print(f"Start (px): {start_px}, {start_py}")
        print(f"Goal (px): {goal_px}, {goal_py}")
        print(f"OGM size: {len(self.ogm_set)} điểm vật cản")

        if (start_px, start_py) in self.ogm_set:
            print("⚠️ Vị trí bắt đầu nằm trên vật cản.")
            return
        if (goal_px, goal_py) in self.ogm_set:
            print("⚠️ Vị trí đích đến nằm trên vật cản.")
            return

        # === A* Algorithm ===
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def a_star(start, goal, ogm_set):
            import heapq
            frontier = []
            heapq.heappush(frontier, (0, start))
            came_from = {start: None}
            cost_so_far = {start: 0}
            while frontier:
                _, current = heapq.heappop(frontier)
                if current == goal:
                    break
                x, y = current
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < MAP_SIZE_PIXELS and 0 <= ny < MAP_SIZE_PIXELS:
                        if (nx, ny) in ogm_set:
                            continue
                        new_cost = cost_so_far[current] + 1
                        if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                            cost_so_far[(nx, ny)] = new_cost
                            priority = new_cost + heuristic((nx, ny), goal)
                            heapq.heappush(frontier, (priority, (nx, ny)))
                            came_from[(nx, ny)] = current
            # Truy vết
            if goal not in came_from:
                return []
            path = []
            curr = goal
            while curr:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            return path

        path = a_star((start_px, start_py), (goal_px, goal_py), self.ogm_set)
        if not path:
            print("❌ Không tìm được đường đi!")
            return

        # === Vẽ đường lên canvas ===
        canvas = self.main_map
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        scale_x = width / MAP_SIZE_PIXELS
        scale_y = height / MAP_SIZE_PIXELS

        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            canvas.create_line(x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y,
                            fill="blue", width=2)

        print("✅ Đã vẽ đường đi.")
        self.path_pixels = path


    def clear_path(self):
        if not hasattr(self, "main_map"):
            print("⚠️ Không tìm thấy canvas để xoá đường đi.")
            return

        canvas = self.main_map

        # Xoá các item đã vẽ lên canvas cho đường đi
        # Ta chỉ xoá các item "vẽ thêm" (điểm start/goal, đường nối...)
        # Giả sử bạn có lưu các ID của các phần tử đường đi trong self.path_items
        if hasattr(self, "path_items"):
            for item_id in self.path_items:
                canvas.delete(item_id)
            self.path_items.clear()
        else:
            self.path_items = []

        # Xoá biến vị trí start và goal nếu muốn reset hoàn toàn
        self.robot_start = None
        self.robot_goal = None
        self.path = []

        print("🧹 Đã xoá đường đi và các điểm chấm trên bản đồ.")



    def set_start_point(self):
        print("🟢 Hãy click vào bản đồ để chọn vị trí robot hiện tại.")
        
        def on_click(event):
            canvas = self.main_map
            # Lấy kích thước hiển thị
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Lấy tọa độ pixel trên ảnh
            click_x = event.x
            click_y = event.y

            # Tính tọa độ thực tế theo mét (dựa trên MAP_SCALE)
            from lidar_map_drawer import MAP_SCALE, MAP_SIZE_PIXELS
            x_m = (click_x / canvas_width) * MAP_SIZE_PIXELS
            y_m = (click_y / canvas_height) * MAP_SIZE_PIXELS

            # Chuyển ngược lại sang hệ trục thực tế: (0,0) là giữa bản đồ
            real_x = (x_m - MAP_SIZE_PIXELS / 2) / MAP_SCALE
            real_y = (MAP_SIZE_PIXELS / 2 - y_m) / MAP_SCALE

            # Lưu lại vị trí
            self.robot_start = (real_x, real_y)
            print(f"✅ Vị trí robot đặt tại: x = {real_x:.2f} m, y = {real_y:.2f} m")

            # Vẽ điểm xanh lá lên bản đồ
            r = 5
            canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill="green", outline="black")
            
            # Hủy bind sau khi click
            canvas.unbind("<Button-1>")

        self.main_map.bind("<Button-1>", on_click)

    def set_goal_point(self):
        print("🔴 Hãy click vào bản đồ để chọn vị trí đích đến.")

        def on_click(event):
            canvas = self.main_map
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Vị trí pixel click
            click_x = event.x
            click_y = event.y

            # Chuyển sang toạ độ thực tế (mét)
            from lidar_map_drawer import MAP_SCALE, MAP_SIZE_PIXELS
            x_m = (click_x / canvas_width) * MAP_SIZE_PIXELS
            y_m = (click_y / canvas_height) * MAP_SIZE_PIXELS

            # Tọa độ thực tế trong bản đồ OGM
            real_x = (x_m - MAP_SIZE_PIXELS / 2) / MAP_SCALE
            real_y = (MAP_SIZE_PIXELS / 2 - y_m) / MAP_SCALE

            # Lưu lại điểm đích
            self.robot_goal = (real_x, real_y)
            print(f"🎯 Đích đến được đặt tại: x = {real_x:.2f} m, y = {real_y:.2f} m")

            # Vẽ điểm đỏ lên bản đồ
            r = 5
            canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill="red", outline="black")

            # Hủy bắt sự kiện click
            canvas.unbind("<Button-1>")

        self.main_map.bind("<Button-1>", on_click)



    def update_robot_status(self, status):
        if status == "moving":
            self.robot_status_label.config(text="Trạng thái: Di chuyển", bg="green")
        elif status == "stuck":
            self.robot_status_label.config(text="Trạng thái: Mắc kẹt", bg="red")

    def show_data(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="DỮ LIỆU TRAO ĐỔI", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10))

        recv_frame = tk.Frame(self.main_content, bg="white")
        recv_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(recv_frame, text="Dữ liệu nhận", font=("Arial", 12, "bold"), bg="white", anchor="w").pack(anchor="w")
        self.recv_text = tk.Text(recv_frame, height=10, width=90, bg="#ecf0f1", relief="solid", bd=1, font=("Courier", 10))
        self.recv_text.pack(pady=5, fill="x")

        send_frame = tk.Frame(self.main_content, bg="white")
        send_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(send_frame, text="Dữ liệu gửi", font=("Arial", 12, "bold"), bg="white", anchor="w").pack(anchor="w")
        self.send_text = tk.Text(send_frame, height=10, width=90, bg="#ecf0f1", relief="solid", bd=1, font=("Courier", 10))
        self.send_text.pack(pady=5, fill="x")

    def show_folder(self):
        maps_folder = "data/maps"
        if not os.path.exists(maps_folder):os.makedirs(maps_folder)
        self.clear_main_content()
        tk.Label(self.main_content, text="🗂 DANH SÁCH BẢN ĐỒ ĐÃ LƯU", font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
        image_frame = tk.Frame(self.main_content, bg="white")
        image_frame.pack(pady=5, padx=10, fill="both", expand=True)

        tk.Button(self.main_content, text="🗑 Xoá tất cả bản đồ đã lưu", font=("Arial", 11), bg="#e74c3c", fg="white",
                command=self.delete_all_maps).pack(pady=(5, 15))

        png_files = sorted(
            [f for f in os.listdir(maps_folder) if f.startswith("scan_map_") and f.endswith(".png")],
            reverse=True
        )

        if not png_files:
            tk.Label(image_frame, text="⚠️ Không có bản đồ nào được lưu.", font=("Arial", 12), bg="white", fg="red").pack()
            return

        for i, filename in enumerate(png_files[:3]):
            try:
                img_path = os.path.join(maps_folder, filename)
                img = Image.open(img_path)
                img = img.resize((250, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                panel = tk.Label(image_frame, image=photo, bg="white", cursor="hand2")
                panel.image = photo
                panel.grid(row=0, column=i, padx=10, pady=5)

                label = tk.Label(image_frame, text=filename, font=("Arial", 10), bg="white")
                label.grid(row=1, column=i)

                # Bind click để mở ảnh
                panel.bind("<Button-1>", lambda e, path=img_path: self.open_full_image(path))

            except Exception as e:
                print(f"[Folder] ❌ Lỗi khi tải ảnh {filename}:", e)

    def open_full_image(self, path):
        from PIL import Image, ImageTk
        import tkinter as tk
        try:
            top = tk.Toplevel(self.root)
            top.title(f"🖼 Xem bản đồ: {path}")

            img = Image.open(path)
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(top, image=photo)
            lbl.image = photo
            lbl.pack(padx=10, pady=10)
        except Exception as e:
            tk.messagebox.showerror("Lỗi", f"Không thể mở ảnh: {e}")

    def delete_all_maps(self):
        import os
        from tkinter import messagebox
        maps_folder = "data/maps"
        confirm = messagebox.askyesno("Xác nhận xoá", "Bạn có chắc chắn muốn xoá tất cả bản đồ?")
        if confirm:
            deleted = 0
            for f in os.listdir(maps_folder):
                if f.startswith("scan_map_") and f.endswith(".png"):
                    try:
                        os.remove(os.path.join(maps_folder, f))
                        deleted += 1
                    except Exception as e:
                        print(f"Lỗi khi xoá {f}: {e}")
            messagebox.showinfo("Đã xoá", f"Đã xoá {deleted} bản đồ.")
            self.show_folder()

    def show_robot(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Thông tin Robot", font=("Arial", 16), bg="white").pack(pady=50)

    def show_settings(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Cài đặt hệ thống", font=("Arial", 16), bg="white").pack(pady=50)

# ==== Run app ====
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
