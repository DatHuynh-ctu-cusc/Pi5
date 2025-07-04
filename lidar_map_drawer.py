import math
from PIL import Image, ImageTk, ImageDraw

def update_ogm_map(ogm_map, data, robot_pose, resolution=0.1):
    angle = data.get("angle_min", 0)
    angle_inc = data.get("angle_increment", 0.01)
    ranges = data.get("ranges", [])

    rx, ry, heading = robot_pose
    cells = ogm_map.shape[0]

    for r in ranges:
        if 0.05 < r < 6.0:
            theta = heading + angle
            x_end = rx + r * math.cos(theta)
            y_end = ry + r * math.sin(theta)

            gx0 = int(rx / resolution)
            gy0 = int(ry / resolution)
            gx1 = int(x_end / resolution)
            gy1 = int(y_end / resolution)

            # Vẽ tia xám từ robot -> vật cản (ray-casting)
            steps = max(abs(gx1 - gx0), abs(gy1 - gy0))
            for i in range(steps):
                xi = int(gx0 + (gx1 - gx0) * i / steps)
                yi = int(gy0 + (gy1 - gy0) * i / steps)
                if 0 <= xi < cells and 0 <= yi < cells and ogm_map[yi, xi] == 255:
                    ogm_map[yi, xi] = 200  # free space

            # Vật cản tại cuối tia
            if 0 <= gx1 < cells and 0 <= gy1 < cells:
                ogm_map[gy1, gx1] = 0

        angle += angle_inc


def draw_ogm_on_canvas(canvas, ogm_map, robot_pose, visited_cells=None):
    if not canvas.winfo_exists():
        return

    canvas.delete("all")
    width, height = canvas.winfo_width(), canvas.winfo_height()
    if width < 10 or height < 10:
        return

    # === Resize OGM map để hiển thị ===
    ogm_img = Image.fromarray(ogm_map)
    ogm_img = ogm_img.transpose(Image.FLIP_TOP_BOTTOM)
    ogm_img = ogm_img.resize((width, height), resample=Image.NEAREST)
    draw = ImageDraw.Draw(ogm_img)

    # === Vẽ các ô đã đi qua (visited_cells) nếu có ===
    if visited_cells:
        for cx, cy in visited_cells:
            px = int(cx * width / ogm_map.shape[1])
            py = int((ogm_map.shape[0] - cy - 1) * height / ogm_map.shape[0])
            draw.rectangle([px, py, px + 1, py + 1], fill=180)

    # === Vẽ robot (vị trí tính từ encoder) ===
    x_m, y_m, theta = robot_pose  # x, y theo mét
    map_w_m = ogm_map.shape[1] * 0.1  # resolution = 0.1
    map_h_m = ogm_map.shape[0] * 0.1

    px = int(x_m / map_w_m * width)
    py = int((1 - y_m / map_h_m) * height)

    r = 4  # bán kính robot vẽ
    draw.ellipse([px - r, py - r, px + r, py + r], fill="red")

    arrow_len = 12
    fx = int(px + arrow_len * math.cos(theta))
    fy = int(py - arrow_len * math.sin(theta))
    draw.line([(px, py), (fx, fy)], fill="green", width=2)

    # Hiển thị lên canvas
    tk_img = ImageTk.PhotoImage(ogm_img)
    canvas.image = tk_img
    canvas.create_image(0, 0, anchor="nw", image=tk_img)


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
