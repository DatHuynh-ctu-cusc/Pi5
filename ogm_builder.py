import math
import numpy as np

def update_ogm_map(ogm_map, data, robot_pose, resolution=0.1):
    """
    Cập nhật bản đồ OGM tích lũy (giữ nguyên điểm cũ).
    - ogm_map: numpy 2D (uint8), 255 = trắng, 200 = free, 0 = occupied
    - data: dict chứa ranges, angle_min, angle_increment
    - robot_pose: (x, y, heading) theo mét
    - resolution: kích thước mỗi cell (m)
    """
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

            steps = max(abs(gx1 - gx0), abs(gy1 - gy0))
            for i in range(steps):
                x = int(gx0 + (gx1 - gx0) * i / steps)
                y = int(gy0 + (gy1 - gy0) * i / steps)
                if 0 <= x < cells and 0 <= y < cells:
                    if ogm_map[y, x] == 255:
                        ogm_map[y, x] = 200  # Free space

            # Vật cản cuối
            if 0 <= gx1 < cells and 0 <= gy1 < cells:
                if ogm_map[gy1, gx1] == 255:
                    ogm_map[gy1, gx1] = 0

        angle += angle_inc
