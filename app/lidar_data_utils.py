# app/lidar_data_utils.py
import math

def clean_lidar_data(data):
    d = dict(data)
    d["ranges"] = [None if (isinstance(v, float) and (math.isinf(v) or math.isnan(v))) else v for v in data["ranges"]]
    return d
