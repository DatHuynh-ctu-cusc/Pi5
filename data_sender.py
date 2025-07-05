import socket, time
from encoder_handler import positions, lock
from limit_switch_handler import get_limit_states

def safe_insert(widget, msg):
    if widget.winfo_exists():
        widget.insert("end", msg)
        widget.see("end")

def send_to_pi4(running_flag, get_text_widget=None):
    HOST_PI4 = '192.168.100.1'
    PORT = 9999
    while running_flag.is_set():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST_PI4, PORT))
                print("[App] Ket noi encoder/limit toi Pi4")
                while running_flag.is_set():
                    with lock:
                        pos_str = ';'.join([f"{k}:{v}" for k, v in positions.items()])
                    limits = ';'.join([f"{k}:{v}" for k, v in get_limit_states().items()])
                    msg = f"ENC{{{pos_str}}};LIMITS{{{limits}}}\n"
                    s.sendall(msg.encode())

                    # Ghi vào GUI nếu có
                    if get_text_widget:
                        text_widget = get_text_widget()
                        if text_widget and text_widget.winfo_exists():
                            try:
                                text_widget.after(0, lambda m=msg: safe_insert(text_widget, m))
                            except:
                                pass

                    time.sleep(0.1)
        except Exception as e:
            print("[App] ❌ Lỗi kết nối Pi4:", e)
            time.sleep(2)
