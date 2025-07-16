# app/lidar_data_utils.py

import math

def clean_lidar_data(data):
    """
    Loại bỏ các giá trị không hợp lệ trong mảng ranges của LiDAR (NaN, Inf thành None).
    """
    d = dict(data)  # Tạo bản sao
    d["ranges"] = [
        None if (isinstance(v, float) and (math.isinf(v) or math.isnan(v))) else v
        for v in data.get("ranges", [])
    ]
    return d

# Có thể bổ sung thêm các hàm chuyển đổi khác nếu cần
def polar_to_cartesian(angle_deg, distance):
    """
    Chuyển đổi từ góc (độ) + khoảng cách sang tọa độ (x, y) trên mặt phẳng.
    """
    angle_rad = math.radians(angle_deg)
    x = distance * math.cos(angle_rad)
    y = distance * math.sin(angle_rad)
    return x, y

# ... Thêm các hàm filter, normalize, crop data nếu muốn
