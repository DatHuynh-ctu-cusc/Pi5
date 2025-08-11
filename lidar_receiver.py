# lidar_receiver.py
import socket
import json
import time

registered_callbacks = []

def register_lidar_callback(cb):
    if callable(cb) and cb not in registered_callbacks:
        registered_callbacks.append(cb)

def safe_insert_json(widget, data):
    try:
        if widget and widget.winfo_exists():
            widget.insert("end", json.dumps(data) + "\n")
            widget.see("end")
    except Exception as e:
        print(f"[App] ⚠️ safe_insert_json lỗi: {e}")

def start_lidar_receiver(running_flag, callbacks=None, get_text_widget=None, port=8899):
    """
    Gọi 1 lần duy nhất trong app. Tự động gửi dữ liệu đến các callback đã đăng ký.
    """
    if callbacks is None:
        callbacks = []
    if not isinstance(callbacks, list):
        callbacks = [callbacks]
    callbacks += registered_callbacks

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    server.settimeout(1.0)

    print(f"[App] 📡 Đang chờ dữ liệu LiDAR từ Pi4 tại cổng {port}...")

    last_data_time = 0
    receiving = False
    NOTIFY_INTERVAL = 2.0

    while running_flag.is_set():
        try:
            conn, addr = server.accept()
            print(f"[App] ✅ Đã kết nối với Pi4: {addr}")
            with conn:
                conn.settimeout(2.0)
                buffer = ""
                while running_flag.is_set():
                    try:
                        chunk = conn.recv(4096)
                        if not chunk:
                            print("[App] 🔌 Mất kết nối Pi4.")
                            break

                        buffer += chunk.decode(errors='ignore')

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

                                # Gọi callback
                                for cb in callbacks:
                                    if callable(cb):
                                        try:
                                            cb(parsed)
                                        except Exception as e:
                                            print(f"[App] ⚠️ Callback lỗi: {e}")

                                # Cập nhật GUI nếu có
                                if get_text_widget:
                                    try:
                                        text_widget = get_text_widget()
                                        if text_widget and text_widget.winfo_exists():
                                            text_widget.after(0, lambda: safe_insert_json(text_widget, parsed))
                                    except Exception as e:
                                        print(f"[App] ⚠️ Text widget lỗi: {e}")

                            except json.JSONDecodeError:
                                # Không in lại lỗi JSON liên tục
                                continue

                        if time.time() - last_data_time > NOTIFY_INTERVAL and receiving:
                            print("🔴 Không còn nhận dữ liệu LiDAR!")
                            receiving = False

                    except socket.timeout:
                        if time.time() - last_data_time > NOTIFY_INTERVAL and receiving:
                            print("🔴 Mất dữ liệu LiDAR!")
                            receiving = False
                    except Exception as e:
                        print(f"[App] ⚠️ Lỗi khi nhận dữ liệu: {e}")
                        break

        except socket.timeout:
            continue
        except Exception as e:
            print(f"[App] ⚠️ Lỗi kết nối socket: {e}")

    server.close()
