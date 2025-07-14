# test_encoders.py
import time
from encoder_handler import init_encoders, cleanup_encoders, positions

def print_encoder_counts(last_counts):
    changed = False
    print("[ENCODER] Giá trị hiện tại:")
    for key in sorted(positions.keys()):
        delta = positions[key] - last_counts.get(key, 0)
        if abs(delta) > 1:
            changed = True
        print(f"  ➤ {key}: {positions[key]} counts (Δ = {delta})")
    return changed

if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] Đang đọc encoder... Nhấn Ctrl+C để dừng.\n")

        last_counts = positions.copy()
        while True:
            if print_encoder_counts(last_counts):
                print("-" * 35)
            last_counts = positions.copy()
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n[TEST] Dừng đọc encoder.")
    finally:
        cleanup_encoders()
