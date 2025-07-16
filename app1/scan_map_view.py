# app/scan_map_view.py
import tkinter as tk
import os, json
from datetime import datetime
from lidar_map_drawer import draw_lidar_on_canvas, draw_zoomed_lidar_map, reset_lidar_map
from app.lidar_data_utils import clean_lidar_data

def show_scan_map(app):
    app.clear_main_content()
    tk.Label(app.main_content, text="CHẾ ĐỘ QUÉT BẢN ĐỒ", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
    app.scan_canvas = tk.Canvas(app.main_content, width=700, height=400, bg="#ecf0f1", highlightbackground="#bdc3c7")
    app.scan_canvas.pack(pady=5)
    button_frame = tk.Frame(app.main_content, bg="white")
    button_frame.pack(fill="x", pady=(15, 10))
    tk.Button(button_frame, text="▶️ Bắt đầu", font=("Arial", 11), width=15, command=lambda: start_scan(app)).pack(side="left", padx=10)
    tk.Button(button_frame, text="⏹ STOP", font=("Arial", 11, "bold"), width=12, fg="white", bg="red", command=lambda: stop_scan(app)).pack(side="left", padx=10)
    tk.Button(button_frame, text="🔄 Làm mới bản đồ", font=("Arial", 11), width=18, command=lambda: refresh_scan_map(app)).pack(side="left", padx=10)
    tk.Button(button_frame, text="💾 Lưu bản đồ", font=("Arial", 11), width=15, command=lambda: save_scan_map(app)).pack(side="left", padx=10)
    app.scan_status_label = tk.Label(button_frame, text="Đang chờ...", width=20, font=("Arial", 11, "bold"), bg="gray", fg="white")
    app.scan_status_label.pack(side="left", padx=20)

def start_scan(app):
    print("▶️ Bắt đầu quét bản đồ...")
    app.scan_status_label.config(text="Đang quét...", bg="red")
    if hasattr(app, "bt_client") and app.bt_client and getattr(app.bt_client, "sock", None):
        app.bt_client.send("start_scan")
    else:
        print("[App] ⚠️ Chưa có kết nối Bluetooth!")

def stop_scan(app):
    print("⏹ Dừng quét bản đồ...")
    app.scan_status_label.config(text="Đã dừng", bg="gray")
    if hasattr(app, "bt_client") and app.bt_client:
        app.bt_client.send("stop")
    else:
        print("[App] ⚠️ Chưa có kết nối Bluetooth!")

def refresh_scan_map(app):
    print("🔄 Làm mới bản đồ...")
    reset_lidar_map(app.scan_canvas)
    app.scan_status_label.config(text="Đang chờ...", bg="gray")

def update_lidar_map(app, lidar_data):
    if not isinstance(lidar_data, dict) or "ranges" not in lidar_data or not lidar_data["ranges"]:
        print("[App] ❌ Dữ liệu LiDAR không hợp lệ hoặc rỗng.")
        return
    try:
        print(f"[App] ✅ Cập nhật bản đồ với {len(lidar_data['ranges'])} điểm")
        app.last_lidar_data = lidar_data.copy()
        if hasattr(app, "scan_canvas") and app.scan_canvas.winfo_exists():
            img = draw_lidar_on_canvas(app.scan_canvas, lidar_data)
            if img is not None:
                app.lidar_image = img
        if hasattr(app, "sub_map") and app.sub_map.winfo_exists():
            draw_zoomed_lidar_map(app.sub_map, lidar_data, radius=2.0)
    except Exception as e:
        print("[App] ⚠️ Lỗi khi vẽ bản đồ LiDAR:", e)

def save_scan_map(app):
    folder = "data/maps"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    img_filename = f"scan_map_{timestamp}.png"
    img_path = os.path.join(folder, img_filename)
    saved_img = False
    if hasattr(app, 'lidar_image') and app.lidar_image is not None:
        try:
            app.lidar_image.save(img_path)
            print(f"💾 Đã lưu ảnh bản đồ vào: {img_path}")
            app.scan_status_label.config(text=f"Đã lưu: {img_filename}", bg="green")
            saved_img = True
        except Exception as e:
            print(f"[App] ⚠️ Lỗi khi lưu ảnh bản đồ: {e}")
    else:
        print("[App] ⚠️ Không tìm thấy ảnh bản đồ để lưu!")

    data_filename = f"scan_map_{timestamp}.json"
    data_path = os.path.join(folder, data_filename)
    saved_data = False
    if hasattr(app, "last_lidar_data") and app.last_lidar_data:
        save_data = clean_lidar_data(app.last_lidar_data)
        try:
            with open(data_path, "w") as f:
                json.dump(save_data, f, indent=2)
            print(f"💾 Đã lưu dữ liệu bản đồ vào: {data_path}")
            saved_data = True
        except Exception as e:
            print(f"[App] ⚠️ Lỗi khi lưu dữ liệu bản đồ: {e}")
    else:
        print("[App] ⚠️ Không có dữ liệu LiDAR để lưu!")
    if saved_img and saved_data:
        print("[App] ✅ Đã lưu đầy đủ ảnh và dữ liệu bản đồ!")
    elif not saved_img and not saved_data:
        app.scan_status_label.config(text=f"Lỗi khi lưu bản đồ!", bg="red")
