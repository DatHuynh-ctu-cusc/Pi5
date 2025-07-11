# bt_client_pi5.py
import bluetooth
import threading

def handle_receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data:
                print("📥 Nhận từ Pi4:", data.decode())
        except:
            break

def handle_send(sock):
    while True:
        msg = input("Nhập lệnh gửi đến Pi4 (q để thoát): ")
        if msg.lower() == "q":
            break
        sock.send(msg.encode())
        print("📤 Đã gửi:", msg)

server_mac = "D8:3A:DD:E7:AD:76"  # MAC address của Pi4
port = 1

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print(f"🔗 Đang kết nối tới {server_mac}:{port} ...")
sock.connect((server_mac, port))
print("✅ Đã kết nối tới Pi4!")

# Khởi tạo 2 luồng
threading.Thread(target=handle_receive, args=(sock,), daemon=True).start()
handle_send(sock)

sock.close()
print("🔌 Đã đóng kết nối.")
