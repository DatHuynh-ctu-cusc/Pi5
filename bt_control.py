# bluetooth_receiver.py
import socket
import os

def receive_bluetooth_map(save_path="/home/dat/LuanVan/received_map.png"):
    # Tạo thư mục nếu chưa có
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Thiết lập Bluetooth RFCOMM socket
    server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server.bind(("", 1))  # Channel 1
    server.listen(1)
    print("[Pi5] 🔊 Đang chờ nhận bản đồ từ Pi4...")

    try:
        client, address = server.accept()
        print(f"[Pi5] ✅ Đã kết nối Bluetooth từ {address}")

        with open(save_path, "wb") as f:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                f.write(data)

        print(f"[Pi5] 💾 Đã lưu bản đồ vào {save_path}")
        client.close()

    except Exception as e:
        print(f"[Pi5] ❌ Lỗi khi nhận bản đồ: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    receive_bluetooth_map()
