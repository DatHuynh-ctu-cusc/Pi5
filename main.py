import tkinter as tk
import threading
from app import SimpleApp
from encoder_handler import init_encoders, cleanup_encoders
from limit_switch_handler import cleanup_switches
from data_sender import send_to_pi4
from lidar_receiver import receive_lidar

if __name__ == "__main__":
    try:
        init_encoders()
        root = tk.Tk()
        app = SimpleApp(root)

        # Truyền send_text và recv_text từ GUI vào các luồng
        threading.Thread(target=send_to_pi4, args=(app.running, lambda: app.send_text), daemon=True).start()
        threading.Thread(target=receive_lidar, args=(app.running, app.update_lidar_map, lambda: app.recv_text), daemon=True).start()

        root.mainloop()
    except KeyboardInterrupt:
        print("[App] ⛔ Đóng ứng dụng.")
    finally:
        cleanup_switches()
        cleanup_encoders()
