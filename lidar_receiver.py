# lidar_receiver.py
import socket
import json

def safe_insert_json(widget, data):
    if widget.winfo_exists():
        widget.insert("end", json.dumps(data) + "\n")
        widget.see("end")

def receive_lidar(running_flag, update_callback, get_text_widget=None):
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

                                # ✅ Lưu vòng quét mới nhất vào thuộc tính app
                                if hasattr(update_callback.__self__, "last_lidar_scan"):
                                    update_callback.__self__.last_lidar_scan = parsed

                                # ✅ Gọi cập nhật bản đồ
                                if callable(update_callback):
                                    update_callback(parsed)

                                # ✅ Ghi log vào giao diện nếu có
                                if get_text_widget:
                                    text_widget = get_text_widget()
                                    if text_widget and text_widget.winfo_exists():
                                        text_widget.after(0, lambda: safe_insert_json(text_widget, parsed))

                            except json.JSONDecodeError:
                                print("[App] ❌ Không phải JSON:", line)
                    except Exception as e:
                        print("[App] ⚠️ Lỗi nhận dữ liệu:", e)
                        break
        except Exception as e:
            print("[App] ⚠️ Lỗi kết nối Pi4:", e)
    server.close()
