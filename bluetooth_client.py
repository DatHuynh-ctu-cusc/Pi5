# bluetooth_client.py
import bluetooth
import threading

class BluetoothClient:
    def __init__(self, server_mac, port=1, on_receive=None):
        self.server_mac = server_mac
        self.port = port
        self.sock = None
        self.running = threading.Event()
        self.running.set()
        self.on_receive = on_receive  # callback khi nhận dữ liệu mới

    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        print(f"🔗 Đang kết nối tới {self.server_mac}:{self.port} ...")
        self.sock.connect((self.server_mac, self.port))
        print("✅ Đã kết nối tới Pi4!")
        threading.Thread(target=self.handle_receive, daemon=True).start()

    def handle_receive(self):
        while self.running.is_set():
            try:
                data = self.sock.recv(1024)
                if data:
                    msg = data.decode()
                    print("📥 Nhận từ Pi4:", msg)
                    if self.on_receive:
                        self.on_receive(msg)
            except:
                break

    def send(self, msg):
        if self.sock:
            self.sock.send(msg.encode())
            print("📤 Đã gửi:", msg)

    def close(self):
        self.running.clear()
        if self.sock:
            self.sock.close()
            print("🔌 Đã đóng kết nối.")

# --- Test nhanh khi chạy riêng lẻ ---
if __name__ == "__main__":
    def on_recv(msg):
        print("[DEBUG] Nhận:", msg)
    bt = BluetoothClient(server_mac="D8:3A:DD:E7:AD:76", on_receive=on_recv)
    bt.connect()
    while True:
        msg = input("Nhập lệnh gửi đến Pi4 (q để thoát): ")
        if msg.lower() == "q":
            bt.close()
            break
        bt.send(msg)
