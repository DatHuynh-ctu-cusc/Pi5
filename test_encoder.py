# test_encoder_pose.py
import time
import math
from encoder_handler import init_encoders, cleanup_encoders, get_robot_pose

def detect_motion(dx, dy, dtheta_deg, threshold=0.01, angle_thresh=3):
    if abs(dtheta_deg) > angle_thresh:
        return "⟲ Xoay trái" if dtheta_deg > 0 else "⟳ Xoay phải"
    elif abs(dx) > threshold or abs(dy) > threshold:
        return "↑ Tiến" if dx > 0 or dy > 0 else "↓ Lùi"
    else:
        return None

if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] Đang đọc dữ liệu encoder... Nhấn Ctrl+C để dừng.\n")

        prev_x, prev_y, prev_theta, _, _ = get_robot_pose()

        while True:
            x, y, theta, left, right = get_robot_pose()

            dx = x - prev_x
            dy = y - prev_y
            dtheta = theta - prev_theta
            dtheta_deg = math.degrees(dtheta)

            motion = detect_motion(dx, dy, dtheta_deg)

            if motion:
                print(f"[ODO] {motion}")
                print(f"      ➤ Vị trí: x = {x:.2f} m | y = {y:.2f} m | góc = {math.degrees(theta):.1f}°")
                print(f"      ➤ Trái = {left:.0f} counts | Phải = {right:.0f} counts\n")

            prev_x, prev_y, prev_theta = x, y, theta
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n[TEST] Dừng lại.")
    finally:
        cleanup_encoders()
