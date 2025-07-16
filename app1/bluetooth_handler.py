# app/bluetooth_handler.py

import threading
import bluetooth  # PyBluez (pip install pybluez)

class BluetoothHandler:
    def __init__(self, mac_address=None, port=1):
        self.mac_address = mac_address   # Địa chỉ MAC của thiết bị Pi4
        self.port = port
        self.socket = None
        self.is_connected = False
        self.lock = threading.Lock()

    def connect(self):
        """Kết nối Bluetooth đến thiết bị Pi4."""
        if not self.mac_address:
            print("[BT] ⚠️ Chưa cấu hình địa chỉ MAC Pi4!")
            return False
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.mac_address, self.port))
            self.is_connected = True
            print(f"[BT] ✅ Đã kết nối {self.mac_address}:{self.port}")
            return True
        except Exception as e:
            print(f"[BT] ❌ Lỗi kết nối Bluetooth: {e}")
            self.is_connected = False
            return False

    def send(self, msg):
        """Gửi chuỗi lệnh hoặc dữ liệu sang Pi4."""
        if self.is_connected and self.socket:
            try:
                with self.lock:
                    if isinstance(msg, str):
                        msg = msg.encode()
                    self.socket.send(msg)
                print(f"[BT] ➡️ Đã gửi: {msg}")
            except Exception as e:
                print(f"[BT] ❌ Gửi lỗi: {e}")
                self.is_connected = False
        else:
            print("[BT] ⚠️ Chưa kết nối!")

    def receive(self, bufsize=1024):
        """Nhận dữ liệu từ Pi4 (blocking)."""
        if self.is_connected and self.socket:
            try:
                data = self.socket.recv(bufsize)
                print(f"[BT] ⬅️ Nhận: {data}")
                return data
            except Exception as e:
                print(f"[BT] ❌ Nhận lỗi: {e}")
                self.is_connected = False
        return None

    def close(self):
        """Ngắt kết nối Bluetooth."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.is_connected = False
        print("[BT] Đã ngắt kết nối.")

# ======= Ví dụ sử dụng trong app =======
# from app.bluetooth_handler import BluetoothHandler
# bt = BluetoothHandler(mac_address="XX:XX:XX:XX:XX:XX")
# bt.connect()
# bt.send("start_scan")
# data = bt.receive()
# bt.close()
