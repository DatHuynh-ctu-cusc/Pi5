# lidar_processing/parser.py
import json

def parse_lidar_line(line):
    try:
        return json.loads(line)
    except Exception as e:
        print(f"[Parse] Lỗi parse JSON: {e}")
        return None
