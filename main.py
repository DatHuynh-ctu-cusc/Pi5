# main.py - Pi5
import tkinter as tk
import threading
from app import SimpleApp
from encoder_handler import init_encoders, cleanup_encoders
from limit_switch_handler import cleanup_switches
from data_sender import send_to_pi4
from lidar_receiver import receive_lidar
from bluetooth_client import BluetoothClient


if __name__ == "__main__":
    try:
        # === Khởi động Encoder ===
        init_encoders()

        # === Giao diện chính ===
        root = tk.Tk()
        app = SimpleApp(root)

        # === Cờ điều khiển luồng chạy ===
        app.running = threading.Event()
        app.running.set()

        # === Luồng gửi dữ liệu encoder + limit switch về Pi4 ===
        threading.Thread(target=send_to_pi4, args=(app.running,), daemon=True).start()

        # === Luồng nhận dữ liệu LiDAR từ Pi4 ===
        threading.Thread(target=receive_lidar, args=(app.running, app.update_lidar_map), daemon=True).start()

        # === Chạy giao diện chính ===
        root.mainloop()

    except KeyboardInterrupt:
        print("[App] ⛔ Đóng ứng dụng.")
    finally:
        # === Giải phóng GPIO ===
        app.running.clear()
        cleanup_switches()
        cleanup_encoders()
