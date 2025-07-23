import socket
import json
import time

def safe_insert_json(widget, data):
    try:
        if widget.winfo_exists():
            widget.insert("end", json.dumps(data) + "\n")
            widget.see("end")
    except Exception as e:
        print(f"[App] ⚠️ safe_insert_json lỗi: {e}")

def start_lidar_receiver(running_flag, callbacks=None, get_text_widget=None, port=8899):
    """
    Chỉ nhận dữ liệu LiDAR thô từ Pi4, gửi cho các callback trong callbacks (list).
    Không xử lý nội dung, không lưu vào biến thành viên của bất kỳ class nào.
    """
    if callbacks is None:
        callbacks = []
    if not isinstance(callbacks, list):
        callbacks = [callbacks]    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    print(f"[App] 📡 Đang chờ dữ liệu LiDAR từ Pi4 tại cổng {port}...")

    last_data_time = 0
    receiving = False
    NOTIFY_INTERVAL = 2.0

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
                                last_data_time = time.time()
                                if not receiving:
                                    print("🟢 Đang nhận dữ liệu LiDAR...")
                                    receiving = True

                                # Gửi cho toàn bộ callback
                                for cb in callbacks:
                                    if callable(cb):
                                        try:
                                            #print(f"[App] Gọi callback: {cb}")
                                            cb(parsed)
                                        except Exception as e:
                                            print(f"[App] ⚠️ Callback lỗi: {e}")

                                # Nếu muốn log text ra 1 widget nào đó:
                                if get_text_widget:
                                    text_widget = get_text_widget()
                                    if text_widget and text_widget.winfo_exists():
                                        text_widget.after(0, lambda: safe_insert_json(text_widget, parsed))
                            except json.JSONDecodeError:
                                print("[App] ❌ Không phải JSON:", line)
                    except Exception as e:
                        print("[App] ⚠️ Lỗi nhận dữ liệu:", e)
                        break
                    if time.time() - last_data_time > NOTIFY_INTERVAL and receiving:
                        print("🔴 Không nhận được dữ liệu LiDAR!")
                        receiving = False
        except Exception as e:
            print("[App] ⚠️ Lỗi kết nối Pi4:", e)
    server.close()
