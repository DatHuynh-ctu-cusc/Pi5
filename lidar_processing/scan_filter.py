# lidar_processing/scan_filter.py
import numpy as np

def median_filter(ranges, kernel=3):
    arr = np.array(ranges)
    filtered = np.copy(arr)
    for i in range(len(arr)):
        start = max(0, i - kernel//2)
        end = min(len(arr), i + kernel//2 + 1)
        filtered[i] = np.median(arr[start:end])
    return filtered.tolist()

def density_filter(points, radius=0.05, min_count=2):
    # Có thể bổ sung lọc mật độ, hiện tạm trả lại nguyên
    return points
