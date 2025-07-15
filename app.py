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
        tk.Label(sv2_frame, text="MSSV: B200000", font=("Arial", 11), bg="white", anchor="w", fg="gray30").pack(anchor="w")
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

        tk.Button(control_frame, text="🗂 Chọn bản đồ", font=("Arial", 11), width=20, command=self.select_map).pack(pady=4)
        tk.Button(control_frame, text="🗑 Xoá bản đồ", font=("Arial", 11), width=20, command=self.clear_map).pack(pady=4)
        tk.Button(control_frame, text="✏️ Vẽ đường đi", font=("Arial", 11), width=20, command=self.draw_path).pack(pady=4)
        tk.Button(control_frame, text="❌ Xoá đường đi", font=("Arial", 11), width=20, command=self.clear_path).pack(pady=4)

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
        # === THÊM NÚT STOP TẠI ĐÂY ===
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

    def update_lidar_map(self, lidar_data):
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
                if img is not None:
                    self.lidar_image = img    # <-- Gán ảnh PIL để lưu sau này

            # Vẽ bản đồ phụ nếu có
            if hasattr(self, "sub_map") and self.sub_map.winfo_exists():
                from lidar_map_drawer import draw_zoomed_lidar_map
                draw_zoomed_lidar_map(self.sub_map, lidar_data, radius=2.0)
        except Exception as e:
            print("[App] ⚠️ Lỗi khi vẽ bản đồ LiDAR:", e)


    def start_scan(self):
        print("▶️ Bắt đầu quét bản đồ...")
        self.scan_status_label.config(text="Đang quét...", bg="red")
        # --- THÊM DÒNG NÀY ---
        if hasattr(self, "bt_client") and self.bt_client:
            self.bt_client.send("start_scan")  # gửi lệnh sang Pi4
        else:
            print("[App] ⚠️ Chưa có kết nối Bluetooth!")

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
        import os, json
        from datetime import datetime

        folder = "data/maps"
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # --- Lưu ảnh PNG ---
        img_filename = f"scan_map_{timestamp}.png"
        img_path = os.path.join(folder, img_filename)
        saved_img = False
        if hasattr(self, 'lidar_image') and self.lidar_image is not None:
            try:
                self.lidar_image.save(img_path)
                print(f"💾 Đã lưu ảnh bản đồ vào: {img_path}")
                self.scan_status_label.config(text=f"Đã lưu: {img_filename}", bg="green")
                saved_img = True
            except Exception as e:
                print(f"[App] ⚠️ Lỗi khi lưu ảnh bản đồ: {e}")
        else:
            print("[App] ⚠️ Không tìm thấy ảnh bản đồ để lưu!")

        # --- Lưu dữ liệu LiDAR JSON ---
        data_filename = f"scan_map_{timestamp}.json"
        data_path = os.path.join(folder, data_filename)
        saved_data = False
        if hasattr(self, "last_lidar_data") and self.last_lidar_data:
            # Chuyển các giá trị Infinity/NaN thành None
            import math
            def clean_lidar_data(data):
                clean = dict(data)
                clean_ranges = []
                for v in data.get("ranges", []):
                    if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
                        clean_ranges.append(None)
                    else:
                        clean_ranges.append(v)
                clean["ranges"] = clean_ranges
                return clean

            save_data = clean_lidar_data(self.last_lidar_data)
            try:
                with open(data_path, "w") as f:
                    json.dump(save_data, f, indent=2)
                print(f"💾 Đã lưu dữ liệu bản đồ vào: {data_path}")
                saved_data = True
            except Exception as e:
                print(f"[App] ⚠️ Lỗi khi lưu dữ liệu bản đồ: {e}")
        else:
            print("[App] ⚠️ Không có dữ liệu LiDAR để lưu!")

        # --- Thông báo nếu cả hai đều OK ---
        if saved_img and saved_data:
            print("[App] ✅ Đã lưu đầy đủ ảnh và dữ liệu bản đồ!")
        elif not saved_img and not saved_data:
            self.scan_status_label.config(text=f"Lỗi khi lưu bản đồ!", bg="red")

        def select_map(self):
            file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
            if file_path:
                try:
                    image = Image.open(file_path)
                    image = image.resize((680, 300), Image.Resampling.LANCZOS)
                    self.map_image = ImageTk.PhotoImage(image)
                    self.main_map.create_image(0, 0, anchor="nw", image=self.map_image)
                    print(f"🖼 Đã chọn bản đồ: {file_path}")
                except Exception as e:
                    print("❌ Lỗi khi mở bản đồ:", e)

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
        print("🗑 Đã xoá bản đồ!")

    def draw_path(self):
        print("✏️ Vẽ đường đi")

    def clear_path(self):
        print("❌ Đã xoá đường đi")

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
