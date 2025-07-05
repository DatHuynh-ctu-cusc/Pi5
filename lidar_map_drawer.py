import math
from PIL import Image, ImageTk, ImageDraw

def bresenham(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x1, y1))
    return points

def update_ogm_map(ogm_map, lidar_data, robot_pose, resolution=0.1):
    if lidar_data is None:
        return

    x0, y0, theta = robot_pose
    angle = lidar_data["angle_min"]
    angle_inc = lidar_data["angle_increment"]

    for r in lidar_data["ranges"]:
        if 0.05 < r < 6.0:
            angle_world = theta + angle
            x1 = x0 + r * math.cos(angle_world)
            y1 = y0 + r * math.sin(angle_world)

            x0_cell = int(x0 / resolution)
            y0_cell = int(y0 / resolution)
            x1_cell = int(x1 / resolution)
            y1_cell = int(y1 / resolution)

            points = bresenham(x0_cell, y0_cell, x1_cell, y1_cell)
            for i, (x, y) in enumerate(points):
                if 0 <= x < ogm_map.shape[1] and 0 <= y < ogm_map.shape[0]:
                    if i < len(points) - 1:
                        if ogm_map[y, x] == 0:
                            ogm_map[y, x] = 1  # free
                    else:
                        ogm_map[y, x] = 2  # occupied
        angle += angle_inc

def draw_ogm_on_canvas(canvas, ogm_map, robot_pose, visited_cells=None, visited_map=None):
    if not canvas.winfo_exists():
        return

    width, height = canvas.winfo_width(), canvas.winfo_height()
    if width < 10 or height < 10:
        return

    img = Image.new("RGB", (ogm_map.shape[1], ogm_map.shape[0]), "gray")
    pixels = img.load()

    for y in range(ogm_map.shape[0]):
        for x in range(ogm_map.shape[1]):
            val = ogm_map[y][x]
            if val == 1:
                pixels[x, y] = (255, 255, 255)
            elif val == 2:
                pixels[x, y] = (0, 0, 0)

    if visited_map is not None:
        for y in range(min(visited_map.shape[0], ogm_map.shape[0])):
            for x in range(min(visited_map.shape[1], ogm_map.shape[1])):
                if visited_map[y][x] == 255:
                    pixels[x, y] = (180, 180, 180)

    draw = ImageDraw.Draw(img)
    x_m, y_m, theta = robot_pose
    px = int(x_m / 0.1)
    py = ogm_map.shape[0] - int(y_m / 0.1)

    draw.ellipse((px-2, py-2, px+2, py+2), fill="red")
    fx = int(px + 6 * math.cos(theta))
    fy = int(py - 6 * math.sin(theta))
    draw.line((px, py, fx, fy), fill="blue", width=1)

    resized_img = img.resize((width, height), resample=Image.NEAREST)
    tk_img = ImageTk.PhotoImage(resized_img)
    canvas.image = tk_img

    if hasattr(canvas, "ogm_img_id"):
        canvas.itemconfig(canvas.ogm_img_id, image=tk_img)
    else:
        canvas.ogm_img_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)

def draw_zoomed_lidar_map(canvas, data, max_range=2.0):
    if not canvas or data is None:
        return

    width = canvas.winfo_width()
    height = canvas.winfo_height()
    map_size = 2.0
    resolution = 0.05
    cells = int(map_size / resolution)

    img = Image.new("RGB", (cells, cells), "white")
    pixels = img.load()

    robot_x = cells // 2
    robot_y = cells // 2

    angle = data.get("angle_min", 0)
    angle_inc = data.get("angle_increment", 0.01)
    ranges = data.get("ranges", [])

    for r in ranges:
        if 0.05 < r <= max_range:
            x_m = r * math.cos(angle)
            y_m = r * math.sin(angle)
            gx = int((x_m + map_size / 2) / resolution)
            gy = int((y_m + map_size / 2) / resolution)

            if 0 <= gx < cells and 0 <= gy < cells:
                pixels[gx, gy] = (0, 0, 0)
        angle += angle_inc

    img = img.resize((width, height), resample=Image.NEAREST)
    tk_img = ImageTk.PhotoImage(img)
    canvas.update_idletasks()

    canvas_w = canvas.winfo_width()
    canvas_h = canvas.winfo_height()
    x = (canvas_w - tk_img.width()) // 2
    y = (canvas_h - tk_img.height()) // 2

    if hasattr(canvas, 'zoomed_map'):
        canvas.itemconfig(canvas.zoomed_map, image=tk_img)
        canvas.coords(canvas.zoomed_map, x, y)
    else:
        canvas.zoomed_map = canvas.create_image(x, y, anchor="nw", image=tk_img)
    canvas.image = tk_img
