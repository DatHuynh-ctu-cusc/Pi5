import tkinter as tk
import threading
from app import SimpleApp
from encoder_handler import init_encoders, cleanup_encoders
from limit_switch_handler import cleanup_switches
from data_sender import send_to_pi4
from lidar_receiver import receive_lidar
from bluetooth_client import BluetoothClient

PI4_BT_MAC = "D8:3A:DD:E7:AD:76"   # Địa chỉ MAC Bluetooth của Pi4

app = None
bt_client = None

if __name__ == "__main__":
    try:
        # === Khởi động Encoder ===
        init_encoders()

        # === Khởi tạo BluetoothClient và kết nối tới Pi4 ===
        bt_client = BluetoothClient(server_mac=PI4_BT_MAC)
        bt_client.connect()   # Nếu connect() tự động trong __init__, có thể bỏ dòng này

        # === Giao diện chính, truyền bt_client vào để gửi lệnh điều khiển ===
        root = tk.Tk()
        app = SimpleApp(root, bt_client=bt_client)

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
        # === Giải phóng GPIO và Bluetooth ===
        if app is not None:
            app.running.clear()
            cleanup_switches()
            cleanup_encoders()
        if bt_client is not None:
            try:
                bt_client.close()
            except:
                pass
