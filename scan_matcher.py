# scan_matcher.py

def find_best_pose(lidar_data, ogm_set):
    """
    Tìm vị trí (x, y, theta) khớp nhất giữa quét LiDAR và bản đồ OGM.
    Đây là mẫu đơn giản, bạn có thể cải tiến.
    """
    import math

    def frange(start, stop, step):
        while start <= stop:
            yield start
            start += step

    def scan_to_points(scan_data):
        angle = scan_data.get("angle_min", 0)
        angle_inc = scan_data.get("angle_increment", math.radians(1))
        ranges = scan_data.get("ranges", [])
        points = []
        for r in ranges:
            if 0.1 < r < 6.0:
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                points.append((x, y))
            angle += angle_inc
        return points

    def compute_matching_score(scan_points, ogm_set, tx, ty, theta, MAP_SIZE_PIXELS=1000, MAP_SCALE=100):
        score = 0
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        for x, y in scan_points:
            x_map = x * cos_t - y * sin_t + tx
            y_map = x * sin_t + y * cos_t + ty
            px = int(x_map * MAP_SCALE + MAP_SIZE_PIXELS // 2)
            py = int(MAP_SIZE_PIXELS // 2 - y_map * MAP_SCALE)
            if (px, py) in ogm_set:
                score += 1
        return score

    scan_points = scan_to_points(lidar_data)
    best_score = -1
    best_pose = (0, 0, 0)
    for tx in frange(-2, 2, 0.1):
        for ty in frange(-2, 2, 0.1):
            for theta in frange(-math.pi, math.pi, math.radians(15)):
                score = compute_matching_score(scan_points, ogm_set, tx, ty, theta)
                if score > best_score:
                    best_score = score
                    best_pose = (tx, ty, theta)
    print(f"[scan_matcher] ✅ Best match: {best_pose} với score = {best_score}")
    return best_pose
