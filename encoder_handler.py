from gpiozero import DigitalInputDevice  
import threading
import math
import time

# === CẤU HÌNH ENCODER ===
ENCODERS = {
    'E1': {'A': 20, 'B': 21},  # Trái trước
    'E2': {'A': 5,  'B': 6},   # Trái sau (chỉ đọc)
    'E4': {'A': 18, 'B': 12},  # Phải trước (chỉ đọc)
    'E3': {'A': 24, 'B': 23}   # Phải sau
}

positions = {key: 0 for key in ENCODERS}
encoders = {}
lock = threading.Lock()

# === THÔNG SỐ ROBOT ===
CPR = 171               # Counts Per Revolution
WHEEL_RADIUS = 0.03     # mét
WHEEL_DISTANCE = 0.23   # mét giữa bánh trái và phải

# === HỆ SỐ HIỆU CHỈNH (cập nhật theo thực tế) ===
SCALE_LEFT = 0.189      # điều chỉnh từ 0.300
SCALE_RIGHT = 0.183     # điều chỉnh từ 0.2901
SCALE_THETA = 3.0       # điều chỉnh từ 2.0

# === VỊ TRÍ ROBOT ===
robot_x = 0.0
robot_y = 0.0
robot_theta = 0.0
last_positions = positions.copy()

# === Bộ đệm trung bình trượt cho robot_theta ===
theta_history = []
MAX_HISTORY = 9

# === CALLBACK ĐỌC CHIỀU QUAY ===
def make_callback(key):
    def callback():
        A = encoders[key]['A'].value
        B = encoders[key]['B'].value
        with lock:
            if A == B:
                positions[key] += 1
            else:
                positions[key] -= 1
    return callback

# === KHỞI TẠO ENCODERS ===
def init_encoders():
    for key, pins in ENCODERS.items():
        encoders[key] = {
            'A': DigitalInputDevice(pins['A']),
            'B': DigitalInputDevice(pins['B'])
        }
        encoders[key]['A'].when_activated = make_callback(key)
        encoders[key]['A'].when_deactivated = make_callback(key)

# === DỌN DẸP ENCODERS ===
def cleanup_encoders():
    for enc in encoders.values():
        enc['A'].close()
        enc['B'].close()

# === TRẢ VỀ VỊ TRÍ ROBOT ===
def get_robot_pose():
    global robot_x, robot_y, robot_theta, last_positions, theta_history

    with lock:
        left_now = positions['E1']
        right_now = positions['E3']
        left_last = last_positions['E1']
        right_last = last_positions['E3']

        d_left = SCALE_LEFT * (left_now - left_last) * (2 * math.pi * WHEEL_RADIUS) / CPR
        d_right = SCALE_RIGHT * (right_now - right_last) * (2 * math.pi * WHEEL_RADIUS) / CPR

        last_positions['E1'] = left_now
        last_positions['E3'] = right_now

    d_center = (d_left + d_right) / 2
    delta_theta = SCALE_THETA * (d_right - d_left) / WHEEL_DISTANCE

    # Làm mượt robot_theta
    raw_theta = robot_theta + delta_theta
    raw_theta = (raw_theta + math.pi) % (2 * math.pi) - math.pi

    theta_history.append(raw_theta)
    if len(theta_history) > MAX_HISTORY:
        theta_history.pop(0)

    robot_theta = sum(theta_history) / len(theta_history)

    dx = d_center * math.cos(robot_theta)
    dy = d_center * math.sin(robot_theta)

    robot_x += dx
    robot_y += dy

    return (robot_x, robot_y, robot_theta, left_now, right_now)

# === TEST TRỰC TIẾP ===
if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] Đang đọc dữ liệu encoder... Nhấn Ctrl+C để dừng.")
        prev_x, prev_y, prev_theta, _, _ = get_robot_pose()
        while True:
            x, y, theta, left, right = get_robot_pose()
            dx = x - prev_x
            dy = y - prev_y
            dtheta_deg = math.degrees(theta - prev_theta)
            if abs(dx) > 0.01 or abs(dy) > 0.01 or abs(dtheta_deg) > 2:
                if abs(dtheta_deg) > 4:
                    action = "⟲ Xoay trái" if dtheta_deg > 0 else "⟳ Xoay phải"
                elif dx > 0 or dy > 0:
                    action = "↑ Tiến"
                else:
                    action = "↓ Lùi"
                print(f"[ODO] {action}")
                print(f"      ➤ x = {x:.2f} m | y = {y:.2f} m | góc = {math.degrees(theta):.1f}°")
                print(f"      ➤ Trái = {left:.0f} counts | Phải = {right:.0f} counts\n")
            prev_x, prev_y, prev_theta = x, y, theta
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[TEST] Dừng lại.")
    finally:
        cleanup_encoders()
