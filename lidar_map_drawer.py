import math
from PIL import Image, ImageTk, ImageDraw
from encoder_handler import get_robot_pose

# === CẤU HÌNH BẢN ĐỒ ===
MAP_SIZE_METERS = 10
MAP_SCALE = 100  # 1m = 100 pixels
MAP_SIZE_PIXELS = int(MAP_SIZE_METERS * MAP_SCALE)

# === BẢN ĐỒ TÍCH LŨY ===
global_map_image = Image.new("RGB", (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), "white")
global_draw = ImageDraw.Draw(global_map_image)
drawn_points = set()

def world_to_pixel(x, y):
    px = int(x * MAP_SCALE + MAP_SIZE_PIXELS // 2)
    py = int(MAP_SIZE_PIXELS // 2 - y * MAP_SCALE)
    return px, py

def draw_lidar_on_canvas(canvas, data):
    global global_map_image, global_draw, drawn_points

    if not canvas or "ranges" not in data:
        print("[DRAW] ❌ Dữ liệu không hợp lệ.")
        return

    robot_x, robot_y, robot_theta, _, _ = get_robot_pose()

    # === Vẽ các điểm quét (tích lũy)
    angle = data.get("angle_min", -math.pi)
    angle_increment = data.get("angle_increment", 0.01)
    for r in data["ranges"]:
        if 0.05 < r < 6.0:
            scan_angle = robot_theta + angle
            obs_x = robot_x + r * math.cos(scan_angle)
            obs_y = robot_y + r * math.sin(scan_angle)
            px, py = world_to_pixel(obs_x, obs_y)
            if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                if (px, py) not in drawn_points:
                    global_draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="black")
                    drawn_points.add((px, py))
        angle += angle_increment

    # === Vẽ robot lên ảnh gốc ===
    robot_px, robot_py = world_to_pixel(robot_x, robot_y)
    draw = global_draw
    draw.ellipse((robot_px - 6, robot_py - 6, robot_px + 6, robot_py + 6), fill="red")
    arrow_len = 20
    arrow_x = robot_px + arrow_len * math.cos(robot_theta)
    arrow_y = robot_py - arrow_len * math.sin(robot_theta)
    draw.line((robot_px, robot_py, arrow_x, arrow_y), fill="green", width=2)

    # === Resize để hiển thị vừa với canvas ===
    resized_image = global_map_image.resize((canvas.winfo_width(), canvas.winfo_height()))
    tk_img = ImageTk.PhotoImage(resized_image)

    if hasattr(canvas, "map_image"):
        canvas.itemconfig(canvas.map_image, image=tk_img)
    else:
        canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img

def draw_zoomed_lidar_map(canvas, data, radius=2.0):
    if not canvas or "ranges" not in data:
        print("[DRAW-ZOOM] ❌ Dữ liệu không hợp lệ.")
        return

    robot_x, robot_y, robot_theta, _, _ = get_robot_pose()
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    center_x = width // 2
    center_y = height // 2
    scale = 100  # pixels per meter

    angle = data.get("angle_min", -math.pi)
    angle_increment = data.get("angle_increment", 0.01)
    for r in data["ranges"]:
        if 0.05 < r < radius:
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

def reset_lidar_map(canvas):
    global global_map_image, global_draw, drawn_points
    global_map_image = Image.new("RGB", (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), "white")
    global_draw = ImageDraw.Draw(global_map_image)
    drawn_points.clear()
    if canvas:
        canvas.delete("all")
    print("[RESET] 🔄 Đã reset bản đồ.")
