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
WHEEL_DISTANCE = 0.34   # <-- chỉnh lại cho đúng thực tế, tăng dần lên nếu ODO báo góc lớn hơn thực tế
SCALE_LEFT = 0.169
SCALE_RIGHT = 0.156
SCALE_ROT_LEFT = 0.201   # scale xoay riêng nếu cần
SCALE_ROT_RIGHT = 0.213

# === VỊ TRÍ ROBOT ===
robot_x = 0.0
robot_y = 0.0
robot_theta = 0.0
last_positions = positions.copy()

# === OFFSET ĐỊNH VỊ THỦ CÔNG (DÙNG CHO SCAN MATCHING) ===
offset_x = 0.0
offset_y = 0.0
offset_theta = 0.0

def set_offset(x, y, theta):
    global offset_x, offset_y, offset_theta
    offset_x = x
    offset_y = y
    offset_theta = theta
    print(f"[OFFSET] ✅ Gán vị trí robot = ({x:.2f}, {y:.2f}) góc {math.degrees(theta):.1f}°")

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

# === TÍNH TOÁN POSE ROBOT ===
def get_robot_pose():
    global robot_x, robot_y, robot_theta, last_positions

    with lock:
        delta_E1 = positions['E1'] - last_positions['E1']
        delta_E2 = positions['E2'] - last_positions['E2']
        delta_E3 = positions['E3'] - last_positions['E3']
        delta_E4 = positions['E4'] - last_positions['E4']
        last_positions = positions.copy()

    delta_left = (delta_E1 + delta_E2) / 2
    delta_right = (delta_E3 + delta_E4) / 2
    is_rotating = abs(delta_left + delta_right) < 0.5 * max(abs(delta_left), abs(delta_right))

    if is_rotating:
        d_left = SCALE_ROT_LEFT * delta_left * (2 * math.pi * WHEEL_RADIUS) / CPR
        d_right = SCALE_ROT_RIGHT * delta_right * (2 * math.pi * WHEEL_RADIUS) / CPR
    else:
        d_left = SCALE_LEFT * delta_left * (2 * math.pi * WHEEL_RADIUS) / CPR
        d_right = SCALE_RIGHT * delta_right * (2 * math.pi * WHEEL_RADIUS) / CPR

    delta_theta = (d_right - d_left) / WHEEL_DISTANCE
    robot_theta += delta_theta
    robot_theta = (robot_theta + math.pi) % (2 * math.pi) - math.pi

    d_center = (d_left + d_right) / 2
    robot_x += d_center * math.cos(robot_theta)
    robot_y += d_center * math.sin(robot_theta)

    return (
        robot_x + offset_x,
        robot_y + offset_y,
        robot_theta + offset_theta,
        positions['E1'], positions['E2'], positions['E3'], positions['E4']
    )

# === TEST THỰC TẾ ===
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
                print(f"      ➤ Vị trí: x = {x:.2f} m | y = {y:.2f} m | góc = {math.degrees(theta):.1f}° (Δθ = {dtheta_deg:.1f}°)")
                print(f"      ➤ Trái = {e1 + e2:.0f} counts | Phải = {e3 + e4:.0f} counts\n")

            prev_x, prev_y, prev_theta = x, y, theta
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[TEST] Dừng lại.")
    finally:
        cleanup_encoders()
