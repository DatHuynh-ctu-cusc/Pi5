from gpiozero import DigitalInputDevice
import threading
import math
import time

# === CẤU HÌNH ENCODER ===
ENCODERS = {
    'E1': {'A': 20, 'B': 21},  # Trái trước
    'E2': {'A': 5,  'B': 6},   # Trái sau
    'E4': {'A': 18, 'B': 12},  # Phải trước
    'E3': {'A': 24, 'B': 23}   # Phải sau
}

positions = {key: 0 for key in ENCODERS}
encoders = {}
lock = threading.Lock()

# === THÔNG SỐ ROBOT ===
CPR = 171               # Counts Per Revolution
WHEEL_RADIUS = 0.03     # mét
WHEEL_DISTANCE = 0.23   # mét giữa bánh trái và phải

# === VỊ TRÍ ROBOT ===
robot_x = 0.0
robot_y = 0.0
robot_theta = 0.0  # radian
last_positions = positions.copy()

# === CALLBACK ĐỌC CHIỀU QUAY DỰA TRÊN A & B ===
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

# === DỌN DẸP ENCODER ===
def cleanup_encoders():
    for enc in encoders.values():
        enc['A'].close()
        enc['B'].close()

# === TRẢ VỀ VỊ TRÍ ROBOT (x, y, góc theta) ===
def get_robot_pose():
    global robot_x, robot_y, robot_theta, last_positions

    with lock:
        # === Tính giá trị trung bình mỗi bên ===
        left_now = (positions['E1'] + positions['E2']) / 2
        right_now = (positions['E4'] + positions['E3']) / 2

        left_last = (last_positions['E1'] + last_positions['E2']) / 2
        right_last = (last_positions['E4'] + last_positions['E3']) / 2

        d_left = (left_now - left_last) * (2 * math.pi * WHEEL_RADIUS) / CPR
        d_right = (right_now - right_last) * (2 * math.pi * WHEEL_RADIUS) / CPR

        last_positions = positions.copy()

    d_center = (d_left + d_right) / 2
    delta_theta = (d_right - d_left) / WHEEL_DISTANCE

    robot_theta += delta_theta
    robot_theta = (robot_theta + math.pi) % (2 * math.pi) - math.pi

    dx = d_center * math.cos(robot_theta)
    dy = d_center * math.sin(robot_theta)

    robot_x += dx
    robot_y += dy

    # 👉 Trả về thêm trung bình encoder mỗi bên
    return (robot_x, robot_y, robot_theta, left_now, right_now)


if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] Đang đọc dữ liệu encoder... Nhấn Ctrl+C để dừng.")
        while True:
            x, y, theta, left_avg, right_avg = get_robot_pose()
            print(f"[ODO] x={x:.2f} m | y={y:.2f} m | góc={math.degrees(theta):.1f}°")
            print(f"      ➤ Trung bình bên trái: {left_avg:.1f} counts | bên phải: {right_avg:.1f} counts\n")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[TEST] Dừng lại.")
    finally:
        cleanup_encoders()

