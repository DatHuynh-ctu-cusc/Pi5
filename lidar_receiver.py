import socket
import json

def receive_lidar(running_flag, update_callback):
    PORT = 8899
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(1)
    print("[App] 📡 Đang chờ dữ liệu LiDAR từ Pi4...")

    while running_flag.is_set():
        try:
            conn, addr = server.accept()
            print(f"[App] ✅ Kết nối Pi4: {addr}")
            with conn:
                buffer = ""
                while running_flag.is_set():
                    try:
                        chunk = conn.recv(4096).decode()
                        if not chunk:
                            break
                        buffer += chunk
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            if not line:
                                continue
                            if line == "PING":
                                conn.sendall(b"PONG\n")
                                continue
                            try:
                                parsed = json.loads(line)
                                if callable(update_callback):
                                    update_callback(parsed)
                            except json.JSONDecodeError:
                                print("[App] ❌ Không phải JSON:", line)
                    except Exception as e:
                        print("[App] ⚠️ Lỗi nhận dữ liệu:", e)
                        break
        except Exception as e:
            print("[App] ⚠️ Lỗi kết nối Pi4:", e)
