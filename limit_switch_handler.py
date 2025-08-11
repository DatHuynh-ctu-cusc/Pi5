# limit_switch_handler.py
import time
from gpiozero import Button

# === KHAI BÁO CÔNG TẮC GIỚI HẠN ===
LIMIT_SWITCHES = {
    'L1': Button(4),
    'L2': Button(17),
    'L3': Button(22),
    'L4': Button(13),
}

def get_limit_states():
    try:
        return {k: '1' if sw.is_pressed else '0' for k, sw in LIMIT_SWITCHES.items()}
    except Exception as e:
        print("[App] ⚠️ Limit switch lỗi:", e)
        return {k: '0' for k in LIMIT_SWITCHES}

def cleanup_switches():
    for sw in LIMIT_SWITCHES.values():
        sw.close()

# === CHẠY TEST TRỰC TIẾP ===
if __name__ == "__main__":
    print("📟 Đang kiểm tra trạng thái công tắc giới hạn... Nhấn Ctrl+C để thoát.\n")
    try:
        while True:
            states = get_limit_states()
            state_str = " | ".join([f"{k}: {'🟥' if v == '1' else '⬜'}" for k, v in states.items()])
            print(f"\r{state_str}", end="", flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n🛑 Dừng kiểm tra.")
    finally:
        cleanup_switches()
        print("🧹 Đã giải phóng tài nguyên.")
