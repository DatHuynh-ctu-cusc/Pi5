import time
import math
import os
from encoder_handler import init_encoders, cleanup_encoders, get_robot_pose, positions

def clear_screen():
    os.system('clear')  # dùng 'cls' nếu chạy trên Windows

def format_deg(rad):
    return (math.degrees(rad) + 360) % 360  # chuyển -π~π → 0~360°

if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] Đang đọc encoder + vị trí robot... Nhấn Ctrl+C để thoát.")
        time.sleep(1)

        while True:
            x, y, theta = get_robot_pose()
            clear_screen()
            print("=== TEST ENCODER + VỊ TRÍ ROBOT ===\n")
            print(f"[Robot] x = {x:.2f} m | y = {y:.2f} m | θ = {format_deg(theta):.1f}°")
            print()
            print(f"[Encoders] E1 = {positions['E1']:>5}   (Trái trước)")
            print(f"           E2 = {positions['E2']:>5}   (Trái sau)")
            print(f"           E4 = {positions['E4']:>5}   (Phải trước)")
            print(f"           E3 = {positions['E3']:>5}   (Phải sau)")
            print("\n==============================\n")
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n[TEST] Dừng test encoder.")
        cleanup_encoders()
