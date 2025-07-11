import time
import math
from encoder_handler import init_encoders, cleanup_encoders, get_robot_pose

def test_rotation():
    print("[TEST] Bắt đầu đo quay trái/phải. Nhấn Ctrl+C để dừng.\n")

    try:
        init_encoders()
        prev_theta = 0
        total_rotation_deg = 0
        start_time = time.time()

        while True:
            _, _, theta, left_avg, right_avg = get_robot_pose()
            deg = math.degrees(theta)

            # Xoay bao nhiêu từ lần đo trước
            delta = deg - prev_theta
            # Xử lý vòng tròn 360 độ
            if delta > 180:
                delta -= 360
            elif delta < -180:
                delta += 360

            total_rotation_deg += delta
            prev_theta = deg

            print(f"[GÓC] Hiện tại: {deg:.2f}° | Tích lũy: {total_rotation_deg:.2f}°")
            print(f"      ➤ Trái : {left_avg:.1f} counts | {left_avg/171:.2f} vòng")
            print(f"      ➤ Phải: {right_avg:.1f} counts | {right_avg/171:.2f} vòng\n")
            time.sleep(0.2)

    except KeyboardInterrupt:
        duration = time.time() - start_time
        print("\n[TEST] Kết thúc đo.")
        print(f"Tổng thời gian: {duration:.1f} giây")
        print(f"Góc quay tích lũy: {total_rotation_deg:.2f}°")
    finally:
        cleanup_encoders()

if __name__ == "__main__":
    test_rotation()
