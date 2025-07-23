import tkinter as tk
from tkinter import messagebox
from lidar_map_drawer import draw_lidar_on_canvas, reset_lidar_map, global_map_image, drawn_points, MAP_SIZE_PIXELS, MAP_SCALE
from datetime import datetime
import os, json

# Import các hàm xử lý từ lidar_processing
from lidar_processing import parser, scan_filter

class ScanTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        self.app = app

        tk.Label(self, text="CHẾ ĐỘ QUÉT BẢN ĐỒ",
                 font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        # Canvas để vẽ bản đồ quét
        self.scan_canvas = tk.Canvas(self, width=700, height=400, bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.scan_canvas.pack(pady=5)

        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(fill="x", pady=(15, 10))
        tk.Button(button_frame, text="▶️ Bắt đầu", font=("Arial", 11), width=15, command=self.start_scan).pack(side="left", padx=10)
        tk.Button(button_frame, text="⏹ STOP", font=("Arial", 11, "bold"), width=12, fg="white", bg="red", command=self.stop_scan).pack(side="left", padx=10)
        tk.Button(button_frame, text="🔄 Làm mới bản đồ", font=("Arial", 11), width=18, command=self.refresh_scan_map).pack(side="left", padx=10)
        tk.Button(button_frame, text="💾 Lưu bản đồ", font=("Arial", 11), width=15, command=self.save_scan_map).pack(side="left", padx=10)

        self.scan_status_label = tk.Label(button_frame, text="Đang chờ...", width=20,
                                          font=("Arial", 11, "bold"), bg="gray", fg="white")
        self.scan_status_label.pack(side="left", padx=20)

    # ==== Các hàm xử lý ====
    def on_lidar_scan(self, line):
        data = parser.parse_lidar_line(line)
        if not data:
            print("[ScanTab] ⚠️ Dữ liệu LiDAR không hợp lệ (parse lỗi).")
            return

        # Lọc nhiễu
        data["ranges"] = scan_filter.median_filter(data["ranges"])
        points = scan_filter.scan_to_points(data)
        points = scan_filter.density_filter(points)

        self.last_lidar_scan = data
        self.last_lidar_points = points
        self.update_lidar_map(data)


    def start_scan(self):
        print("▶️ Bắt đầu quét bản đồ...")
        self.scan_status_label.config(text="Đang quét...", bg="red")
        if self.app.bt_client:
            self.app.bt_client.send("start_scan")
        else:
            print("[App] ⚠️ Chưa có kết nối Bluetooth!")

    def stop_scan(self):
        print("⏹ Dừng quét bản đồ...")
        self.scan_status_label.config(text="Đã dừng", bg="gray")
        if self.app.bt_client:
            self.app.bt_client.send("stop")
        else:
            print("[App] ⚠️ Chưa có kết nối Bluetooth!")

    def refresh_scan_map(self):
        print("🔄 Làm mới bản đồ...")
        reset_lidar_map(self.scan_canvas)
        self.scan_status_label.config(text="Đang chờ...", bg="gray")

    def save_scan_map(self):
        folder = "data/maps"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

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

        ogm_filename = f"scan_map_{timestamp}.json"
        ogm_path = os.path.join(folder, ogm_filename)
        saved_ogm = False
        try:
            ogm_data = {
                "size_pixels": MAP_SIZE_PIXELS,
                "scale": MAP_SCALE,
                "occupied_points": list(drawn_points)
            }
            with open(ogm_path, "w") as f:
                json.dump(ogm_data, f)
            print(f"💾 Đã lưu bản đồ OGM vào: {ogm_path}")
            saved_ogm = True
        except Exception as e:
            print(f"[App] ⚠️ Lỗi khi lưu dữ liệu OGM: {e}")
            messagebox.showerror("Lỗi lưu dữ liệu", str(e))

        if saved_img and saved_ogm:
            print("[App] ✅ Đã lưu đầy đủ ảnh và OGM!")
            messagebox.showinfo("Thành công", "Đã lưu ảnh và bản đồ OGM!")
        elif not saved_img and not saved_ogm:
            self.scan_status_label.config(text=f"Lỗi khi lưu bản đồ!", bg="red")

    def update_lidar_map(self, lidar_data):
        import math
        if not isinstance(lidar_data, dict) or "ranges" not in lidar_data or not lidar_data["ranges"]:
            print("[App] ❌ Dữ liệu LiDAR không hợp lệ hoặc rỗng.")
            return
        try:
            #print(f"[App] ✅ Cập nhật bản đồ với {len(lidar_data['ranges'])} điểm")
            self.last_lidar_scan = lidar_data.copy()

            if self.scan_canvas.winfo_exists():
                img = draw_lidar_on_canvas(self.scan_canvas, lidar_data)
                #print("[DEBUG] img trả về từ draw_lidar_on_canvas:", type(img))
                if img is not None:
                    self.lidar_image = img

            # Nếu có logic scan-matching tại đây thì xử lý thêm...
            # Ví dụ: định vị robot từ lidar_data nếu cần

        except Exception as e:
            print("[App] ⚠️ Lỗi khi vẽ bản đồ LiDAR:", e)
