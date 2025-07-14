from gpiozero import DigitalInputDevice  
import threading
import math
import time

# === CẤU HÌNH ENCODER ===
ENCODERS = {
    'E1': {'A': 20, 'B': 21},  # Trái trước
    'E2': {'A': 5,  'B': 6},   # Trái sau
    'E3': {'A': 24, 'B': 23},  # Phải sau
    'E4': {'A': 18, 'B': 12},  # Phải trước
}

positions = {key: 0 for key in ENCODERS}
encoders = {}
lock = threading.Lock()

# === THÔNG SỐ ROBOT ===
CPR = 171               # Counts Per Revolution
WHEEL_RADIUS = 0.03     # mét
WHEEL_DISTANCE = 0.23   # mét giữa bánh trái và phải

# === HỆ SỐ HIỆU CHỈNH ===
SCALE_LEFT = 0.1895
SCALE_RIGHT = 0.1832
SCALE_THETA = 3.5   # Cập nhật để xoay đúng 90°

# === VỊ TRÍ ROBOT ===
robot_x = 0.0
robot_y = 0.0
robot_theta = 0.0
last_positions = positions.copy()

# === LÀM MƯỢT GÓC ===
theta_history = []
MAX_HISTORY = 9

# === CALLBACK ĐỌC ENCODER ===
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

# === KHỞI TẠO ENCODER ===
def init_encoders():
    for key, pins in ENCODERS.items():
        encoders[key] = {
            'A': DigitalInputDevice(pins['A']),
            'B': DigitalInputDevice(pins['B']),
        }
        encoders[key]['A'].when_activated = make_callback(key)
        encoders[key]['A'].when_deactivated = make_callback(key)

# === DỌN DẸP ===
def cleanup_encoders():
    for enc in encoders.values():
        enc['A'].close()
        enc['B'].close()

# === TÍNH POSE ROBOT ===
def get_robot_pose():
    global robot_x, robot_y, robot_theta, last_positions, theta_history

    with lock:
        left_now = (positions['E1'] + positions['E2']) / 2
        right_now = (positions['E3'] + positions['E4']) / 2
        left_last = (last_positions['E1'] + last_positions['E2']) / 2
        right_last = (last_positions['E3'] + last_positions['E4']) / 2

        d_left = SCALE_LEFT * (left_now - left_last) * (2 * math.pi * WHEEL_RADIUS) / CPR
        d_right = SCALE_RIGHT * (right_now - right_last) * (2 * math.pi * WHEEL_RADIUS) / CPR

        last_positions['E1'] = positions['E1']
        last_positions['E2'] = positions['E2']
        last_positions['E3'] = positions['E3']
        last_positions['E4'] = positions['E4']

    # === TÍNH GÓC XOAY ===
    delta_theta = SCALE_THETA * (d_right - d_left) / WHEEL_DISTANCE
    raw_theta = robot_theta + delta_theta
    raw_theta = (raw_theta + math.pi) % (2 * math.pi) - math.pi

    # Làm mượt
    theta_history.append(raw_theta)
    if len(theta_history) > MAX_HISTORY:
        theta_history.pop(0)
    robot_theta = sum(theta_history) / len(theta_history)

    # === TÍNH X, Y ===
    if (d_left > 0 and d_right < 0) or (d_left < 0 and d_right > 0):
        d_center = 0  # xoay tại chỗ
    else:
        d_center = (d_left + d_right) / 2

    dx = d_center * math.cos(robot_theta)
    dy = d_center * math.sin(robot_theta)

    robot_x += dx
    robot_y += dy

    return (robot_x, robot_y, robot_theta,
            positions['E1'], positions['E2'], positions['E3'], positions['E4'])

# === TEST TRỰC TIẾP ===
if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] Đang đọc dữ liệu encoder... Nhấn Ctrl+C để dừng.")
        prev_x, prev_y, prev_theta, *_ = get_robot_pose()
        while True:
            x, y, theta, e1, e2, e3, e4 = get_robot_pose()
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
                print(f"      ➤ x = {x:.2f} m | y = {y:.2f} m | góc = {math.degrees(theta):.1f}° (Δθ = {dtheta_deg:.1f}°)")
                print(f"      ➤ E1={e1:.0f} | E2={e2:.0f} | E3={e3:.0f} | E4={e4:.0f}\n")

            prev_x, prev_y, prev_theta = x, y, theta
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[TEST] Dừng lại.")
    finally:
        cleanup_encoders()
