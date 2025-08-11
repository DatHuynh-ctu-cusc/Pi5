# send_switch_to_pi4.py (chạy trên Pi5)
import socket
import time
from gpiozero import Button

# Cấu hình công tắc
LIMIT_SWITCHES = {
    'L1': Button(4),
    'L2': Button(17),
    'L3': Button(22),
    'L4': Button(13),
}

def get_limit_states():
    return {k: '1' if sw.is_pressed else '0' for k, sw in LIMIT_SWITCHES.items()}

def main():
    HOST_PI4 = '192.168.100.1'  # IP của Pi4
    PORT = 9999

    while True:
        try:
            print(f"[Pi5] 🔄 Đang kết nối tới Pi4 tại {HOST_PI4}:{PORT}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST_PI4, PORT))
                print("[Pi5] ✅ Đã kết nối Pi4.")

                while True:
                    limits = get_limit_states()
                    limit_str = ';'.join([f"{k}:{v}" for k, v in limits.items()])
                    msg = f"LIMITS{{{limit_str}}}\n"
                    s.sendall(msg.encode())
                    print(f"[Pi5] 📤 Gửi: {msg.strip()}")
                    time.sleep(0.2)
        except Exception as e:
            print(f"[Pi5] ❌ Lỗi kết nối Pi4: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
