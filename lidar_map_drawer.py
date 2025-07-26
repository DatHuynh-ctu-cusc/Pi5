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

# === GRID ĐẾM SỐ LẦN PHÁT HIỆN (Density Filter) ===
occupancy_grid = [[0 for _ in range(MAP_SIZE_PIXELS)] for _ in range(MAP_SIZE_PIXELS)]

DENSITY_THRESHOLD = 4
NEIGHBOR_FILTER = True

# === BẬT/TẮT vẽ realtime vào bản đồ (để tránh ghi đè JSON) ===
drawing_enabled = True

def set_drawing_enabled(flag: bool):
    global drawing_enabled
    drawing_enabled = flag

def world_to_pixel(x, y):
    px = int(x * MAP_SCALE + MAP_SIZE_PIXELS // 2)
    py = int(MAP_SIZE_PIXELS // 2 - y * MAP_SCALE)
    return px, py

def draw_lidar_on_canvas(canvas, data, moving_state="forward"):
    global global_map_image, global_draw, drawn_points, occupancy_grid, drawing_enabled

    if not canvas or "ranges" not in data:
        print("[DRAW] ❌ Dữ liệu không hợp lệ.")
        return

    if not drawing_enabled:
        # 🚫 Không vẽ nếu đang ở MapTab đã mở JSON
        return

    robot_x, robot_y, robot_theta, *_ = get_robot_pose()
    angle = data.get("angle_min", -math.pi)
    angle_increment = data.get("angle_increment", 0.01)

    for r in data["ranges"]:
        if 0.05 < r < 6.0:
            scan_angle = robot_theta + angle
            obs_x = robot_x + r * math.cos(scan_angle)
            obs_y = robot_y + r * math.sin(scan_angle)
            px, py = world_to_pixel(obs_x, obs_y)
            if 0 <= px < MAP_SIZE_PIXELS and 0 <= py < MAP_SIZE_PIXELS:
                occupancy_grid[py][px] += 1
                if occupancy_grid[py][px] == DENSITY_THRESHOLD:
                    global_draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill="black")
                    drawn_points.add((px, py))
        angle += angle_increment

    display_image = global_map_image.copy()
    draw = ImageDraw.Draw(display_image)
    robot_px, robot_py = world_to_pixel(robot_x, robot_y)
    draw.ellipse((robot_px - 6, robot_py - 6, robot_px + 6, robot_py + 6), fill="red")
    arrow_len = 20
    arrow_x = robot_px + arrow_len * math.cos(robot_theta)
    arrow_y = robot_py - arrow_len * math.sin(robot_theta)
    draw.line((robot_px, robot_py, arrow_x, arrow_y), fill="green", width=2)

    if canvas.winfo_width() < 10 or canvas.winfo_height() < 10:
        return
    resized_image = display_image.resize((canvas.winfo_width(), canvas.winfo_height()))
    tk_img = ImageTk.PhotoImage(resized_image)

    if hasattr(canvas, "map_image"):
        canvas.itemconfig(canvas.map_image, image=tk_img)
    else:
        canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img

    return global_map_image

def postprocess_map():
    global global_map_image, occupancy_grid, drawn_points
    print("[Filter] Bắt đầu lọc median/neighbor")
    min_neighbors = 4

    new_image = global_map_image.copy()
    new_draw = ImageDraw.Draw(new_image)
    count = 0
    for y in range(1, MAP_SIZE_PIXELS - 1):
        for x in range(1, MAP_SIZE_PIXELS - 1):
            if occupancy_grid[y][x] >= DENSITY_THRESHOLD:
                neighbors = sum([
                    occupancy_grid[yy][xx] >= DENSITY_THRESHOLD
                    for yy in range(y - 1, y + 2)
                    for xx in range(x - 1, x + 2)
                    if not (yy == y and xx == x)
                ])
                if neighbors < min_neighbors:
                    new_draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill="white")
                    count += 1
    global_map_image.paste(new_image)
    print(f"[Filter] Đã loại {count} điểm nhiễu lẻ.")

def reset_lidar_map(canvas=None):
    global global_map_image, global_draw, drawn_points, occupancy_grid
    global_map_image = Image.new("RGB", (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), "white")
    global_draw = ImageDraw.Draw(global_map_image)
    drawn_points.clear()
    occupancy_grid = [[0 for _ in range(MAP_SIZE_PIXELS)] for _ in range(MAP_SIZE_PIXELS)]
    if canvas:
        canvas.delete("all")
    print("[RESET] 🔄 Đã reset bản đồ.")

def draw_zoomed_lidar_map(canvas, data, radius=2.0):
    if not canvas or "ranges" not in data:
        print("[DRAW-ZOOM] ❌ Dữ liệu không hợp lệ.")
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

def draw_robot_realtime(canvas, base_image):
    try:
        robot_x, robot_y, robot_theta, *_ = get_robot_pose()
        robot_px = int(robot_x * MAP_SCALE + MAP_SIZE_PIXELS // 2)
        robot_py = int(MAP_SIZE_PIXELS // 2 - robot_y * MAP_SCALE)
        image = base_image.copy()
        draw = ImageDraw.Draw(image)
        draw.ellipse((robot_px - 6, robot_py - 6, robot_px + 6, robot_py + 6), fill="red")
        arrow_len = 20
        arrow_x = robot_px + arrow_len * math.cos(robot_theta)
        arrow_y = robot_py - arrow_len * math.sin(robot_theta)
        draw.line((robot_px, robot_py, arrow_x, arrow_y), fill="green", width=2)
        resized_image = image.resize((canvas.winfo_width(), canvas.winfo_height()))
        tk_img = ImageTk.PhotoImage(resized_image)
        if hasattr(canvas, "map_image"):
            canvas.itemconfig(canvas.map_image, image=tk_img)
        else:
            canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)
        canvas.image = tk_img
    except Exception as e:
        print(f"[draw_robot_realtime] ❌ Lỗi: {e}")