import tkinter as tk
import threading
from gui.app import SimpleApp
from encoder_handler import init_encoders, cleanup_encoders
from limit_switch_handler import cleanup_switches
from data_sender import send_to_pi4
from lidar_receiver import start_lidar_receiver
from bluetooth_client import BluetoothClient

PI4_BT_MAC = "D8:3A:DD:E7:AD:76"

if __name__ == "__main__":
    try:
        init_encoders()
        bt_client = BluetoothClient(server_mac=PI4_BT_MAC)
        bt_client.connect()

        root = tk.Tk()
        app = SimpleApp(root, bt_client=bt_client)
        app.running = threading.Event()
        app.running.set()

        # Gửi encoder & công tắc tới Pi4
        threading.Thread(target=send_to_pi4, args=(app.running,), daemon=True).start()

        # Chỉ gọi 1 lần duy nhất để nhận LiDAR
        threading.Thread(
            target=start_lidar_receiver,
            args=(app.running,),  # callbacks sẽ được đăng ký riêng ở các Tab
            daemon=True
        ).start()

        root.mainloop()
    except KeyboardInterrupt:
        print("[App] ⛔ Đóng ứng dụng.")
    finally:
        if app is not None:
            app.running.clear()
            cleanup_switches()
            cleanup_encoders()
        if bt_client is not None:
            try:
                bt_client.close()
            except:
                pass
