import math
import numpy as np
from PIL import Image, ImageTk, ImageDraw
from encoder_handler import get_robot_pose, get_robot_velocity

# === CẤU HÌNH BẢN ĐỒ ===
MAP_SIZE_METERS = 10
MAP_SCALE = 100  # 1m = 100 pixels
MAP_SIZE_PIXELS = int(MAP_SIZE_METERS * MAP_SCALE)

# === BẢN ĐỒ TÍCH LŨY ===
global_map_image = Image.new("RGB", (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), "white")
global_draw = ImageDraw.Draw(global_map_image)
drawn_points = set()
occupancy_grid = np.zeros((MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), dtype=np.uint8)
drawing_enabled = True

# === THAM SỐ LỌC NHẸ ===
DENSITY_THRESHOLD = 2
MIN_NEIGHBORS = 2

def set_drawing_enabled(flag: bool):
    global drawing_enabled
    drawing_enabled = flag

def world_to_pixel(x, y):
    px = int(x * MAP_SCALE + MAP_SIZE_PIXELS // 2)
    py = int(MAP_SIZE_PIXELS // 2 - y * MAP_SCALE)
    return px, py

def draw_lidar_on_canvas(canvas, data, pose=None, moving_state="forward"):
    global global_map_image, global_draw, drawn_points, occupancy_grid, drawing_enabled

    if not canvas or "ranges" not in data or not drawing_enabled:
        return

    # === LẤY VỊ TRÍ & HƯỚNG TỪ ENCODER + VẬN TỐC ===
    robot_x, robot_y, robot_theta, *_ = get_robot_pose()
    vx, vy, vtheta = get_robot_velocity()

    angle = data.get("angle_min", -math.pi)
    angle_increment = data.get("angle_increment", 0.01)
    ranges = data["ranges"]
    scan_time = data.get("scan_time", 0.1)
    dt_per_point = scan_time / len(ranges)

    for i, r in enumerate(ranges):
        if 0.2 < r < 3.0:  # ✅ Giới hạn khoảng cách tin cậy
            if abs(angle) > math.radians(135):  # ✅ Bỏ vùng sau lưng
                angle += angle_increment
                continue

            # Dự đoán vị trí robot tại thời điểm đo điểm này
            dt = i * dt_per_point
            est_x = robot_x + vx * dt
            est_y = robot_y + vy * dt
            est_theta = robot_theta + vtheta * dt

            scan_angle = est_theta + angle
            obs_x = est_x + r * math.cos(scan_angle)
            obs_y = est_y + r * math.sin(scan_angle)
            px, py = world_to_pixel(obs_x, obs_y)

            if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                occupancy_grid[py, px] += 1
                if occupancy_grid[py, px] == DENSITY_THRESHOLD:
                    global_draw.point((px, py), fill="black")
                    drawn_points.add((px, py))

        angle += angle_increment

    # === VẼ ROBOT ===
    if canvas.winfo_width() < 10 or canvas.winfo_height() < 10:
        return

    robot_px, robot_py = world_to_pixel(robot_x, robot_y)
    arrow_len = 20
    arrow_x = robot_px + arrow_len * math.cos(robot_theta)
    arrow_y = robot_py - arrow_len * math.sin(robot_theta)

    display_image = global_map_image.copy()
    draw = ImageDraw.Draw(display_image)
    draw.ellipse((robot_px - 6, robot_py - 6, robot_px + 6, robot_py + 6), fill="red")
    draw.line((robot_px, robot_py, arrow_x, arrow_y), fill="green", width=2)

    resized = display_image.resize((canvas.winfo_width(), canvas.winfo_height()))
    tk_img = ImageTk.PhotoImage(resized)

    if hasattr(canvas, "map_image"):
        canvas.itemconfig(canvas.map_image, image=tk_img)
    else:
        canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img
    return tk_img

def reset_lidar_map(canvas=None):
    global global_map_image, global_draw, drawn_points, occupancy_grid
    global_map_image = Image.new("RGB", (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), "white")
    global_draw = ImageDraw.Draw(global_map_image)
    drawn_points.clear()
    occupancy_grid = np.zeros((MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), dtype=np.uint8)
    if canvas:
        canvas.delete("all")
    print("[RESET] 🔄 Đã reset bản đồ.")

def draw_zoomed_lidar_map(canvas, data, radius=2.0):
    if not canvas or "ranges" not in data:
        return

    robot_x, robot_y, robot_theta, *_ = get_robot_pose()
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    center_x = width // 2
    center_y = height // 2
    scale = MAP_SCALE

    angle = data.get("angle_min", -math.pi)
    angle_increment = data.get("angle_increment", 0.01)
    for r in data["ranges"]:
        if 0.2 < r < radius:
            scan_angle = robot_theta + angle
            x = center_x + r * scale * math.cos(scan_angle)
            y = center_y - r * scale * math.sin(scan_angle)
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill="black")
        angle += angle_increment

    draw.ellipse((center_x - 5, center_y - 5, center_x + 5, center_y + 5), fill="red")
    arrow_len = 20
    draw.line((center_x, center_y,
               center_x + arrow_len * math.cos(robot_theta),
               center_y - arrow_len * math.sin(robot_theta)),
              fill="green", width=2)

    tk_img = ImageTk.PhotoImage(image)
    if hasattr(canvas, "zoom_image"):
        canvas.itemconfig(canvas.zoom_image, image=tk_img)
    else:
        canvas.zoom_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img
