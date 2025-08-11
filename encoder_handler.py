from gpiozero import DigitalInputDevice  
import threading, math, time

# === ENCODER CONFIG ===
ENCODERS = {
    'E1': {'A': 20, 'B': 21},  # Trái trước
    'E2': {'A': 5,  'B': 6},   # Trái sau
    'E3': {'A': 24, 'B': 23},  # Phải sau
    'E4': {'A': 18, 'B': 12},  # Phải trước
}

positions = {k: 0 for k in ENCODERS}
encoders = {}
lock = threading.Lock()

# === ROBOT PHYSICAL PARAMETERS ===
CPR = 171
WHEEL_RADIUS = 0.03     # meters
WHEEL_DISTANCE = 0.35   # meters between L/R
SCALE_LEFT = 0.133
SCALE_RIGHT = 0.133
SCALE_ROT_LEFT = 0.22
SCALE_ROT_RIGHT = 0.19

# === ROBOT POSE ===
robot_x = robot_y = robot_theta = 0.0
last_positions = positions.copy()

# === OFFSET (FOR LOCALIZATION) ===
offset_x = offset_y = offset_theta = 0.0
def set_offset(x, y, theta):
    global offset_x, offset_y, offset_theta
    offset_x, offset_y, offset_theta = x, y, theta
    print(f"[OFFSET] ✅ Gán vị trí robot = ({x:.2f}, {y:.2f}) góc {math.degrees(theta):.1f}°")

# === CALLBACKS ===
def make_callback(k):
    def cb():
        A, B = encoders[k]['A'].value, encoders[k]['B'].value
        with lock:
            positions[k] += 1 if A == B else -1
    return cb

def init_encoders():
    for k, pins in ENCODERS.items():
        encoders[k] = {
            'A': DigitalInputDevice(pins['A']),
            'B': DigitalInputDevice(pins['B']),
        }
        encoders[k]['A'].when_activated = make_callback(k)
        encoders[k]['A'].when_deactivated = make_callback(k)

def cleanup_encoders():
    for e in encoders.values():
        e['A'].close()
        e['B'].close()

# === VELOCITY TRACKING ===
vx = vy = vtheta = 0.0
last_x = last_y = last_theta = 0.0
last_time = time.time()

def update_velocity(x, y, theta):
    global vx, vy, vtheta, last_x, last_y, last_theta, last_time
    now = time.time()
    dt = now - last_time
    if dt == 0: return
    vx = (x - last_x) / dt
    vy = (y - last_y) / dt
    vtheta = (theta - last_theta) / dt
    last_x, last_y, last_theta, last_time = x, y, theta, now

# === POSE CALCULATION ===
def get_robot_pose():
    global robot_x, robot_y, robot_theta, last_positions
    with lock:
        dE1 = positions['E1'] - last_positions['E1']
        dE2 = positions['E2'] - last_positions['E2']
        dE3 = positions['E3'] - last_positions['E3']
        dE4 = positions['E4'] - last_positions['E4']
        last_positions = positions.copy()

    d_left = (dE1 + dE2) / 2
    d_right = (dE3 + dE4) / 2
    rotating = abs(d_left + d_right) < 0.5 * max(abs(d_left), abs(d_right))

    if rotating:
        l = SCALE_ROT_LEFT * d_left * (2 * math.pi * WHEEL_RADIUS) / CPR
        r = SCALE_ROT_RIGHT * d_right * (2 * math.pi * WHEEL_RADIUS) / CPR
    else:
        l = SCALE_LEFT * d_left * (2 * math.pi * WHEEL_RADIUS) / CPR
        r = SCALE_RIGHT * d_right * (2 * math.pi * WHEEL_RADIUS) / CPR

    dtheta = (r - l) / WHEEL_DISTANCE
    robot_theta = (robot_theta + dtheta + math.pi) % (2 * math.pi) - math.pi
    d_center = (l + r) / 2
    robot_x += d_center * math.cos(robot_theta)
    robot_y += d_center * math.sin(robot_theta)

    update_velocity(robot_x, robot_y, robot_theta)

    return (
        robot_x + offset_x,
        robot_y + offset_y,
        robot_theta + offset_theta,
        positions['E1'], positions['E2'], positions['E3'], positions['E4']
    )

def get_robot_velocity():
    with lock:
        return vx, vy, vtheta

# === TEST ===
if __name__ == "__main__":
    try:
        init_encoders()
        print("[TEST] 🧪 Đang đọc encoder... Ctrl+C để dừng.")
        prev_x, prev_y, prev_theta, *_ = get_robot_pose()

        while True:
            x, y, theta, e1, e2, e3, e4 = get_robot_pose()
            dx, dy = x - prev_x, y - prev_y
            dtheta_deg = math.degrees(theta - prev_theta)

            if abs(dx) > 0.01 or abs(dy) > 0.01 or abs(dtheta_deg) > 2:
                action = "⟲ Xoay trái" if dtheta_deg > 4 else (
                         "⟳ Xoay phải" if dtheta_deg < -4 else (
                         "↑ Tiến" if dx > 0 or dy > 0 else "↓ Lùi"))
                print(f"[ODO] {action}")
                print(f"      ➤ x = {x:.2f} m | y = {y:.2f} m | góc = {math.degrees(theta):.1f}° (Δθ = {dtheta_deg:.1f}°)")
                print(f"      ➤ Trái = {e1 + e2} | Phải = {e3 + e4}\n")

            prev_x, prev_y, prev_theta = x, y, theta
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[TEST] Dừng lại.")
    finally:
        cleanup_encoders()
