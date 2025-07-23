# lidar_processing/map_utils.py
import math

def scan_to_points(data):
    angle = data.get("angle_min", -math.pi)
    angle_inc = data.get("angle_increment", 0.01)
    ranges = data.get("ranges", [])
    points = []
    for r in ranges:
        if 0.05 < r < 6.0:
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            points.append((x, y))
        angle += angle_inc
    return points

def world_to_pixel(x, y, map_scale, map_size_pixels):
    px = int(x * map_scale + map_size_pixels // 2)
    py = int(map_size_pixels // 2 - y * map_scale)
    return px, py
