import math
from PIL import Image, ImageTk, ImageDraw

def draw_lidar_on_canvas(canvas, data):
    if not canvas or "ranges" not in data:
        print("[DRAW] ❌ Dữ liệu không hợp lệ.")
        return

    # Kích thước canvas
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # Tạo ảnh trắng
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Tâm robot ở giữa ảnh
    center_x = width // 2
    center_y = height // 2

    # Tỉ lệ chuyển đổi: mét → pixel
    scale = 100  # 1m = 100 pixels

    # Góc bắt đầu và bước tăng
    angle = data.get("angle_min", -math.pi)
    angle_increment = data.get("angle_increment", 0.01)

    count = 0
    for r in data["ranges"]:
        if 0.05 < r < 6.0:  # Bỏ giá trị nhiễu
            x = center_x + r * scale * math.cos(angle)
            y = center_y - r * scale * math.sin(angle)  # Y âm vì canvas gốc từ trên xuống
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill="black")
            count += 1
        angle += angle_increment

    print(f"[DRAW] ✅ Đã vẽ {count} điểm LiDAR.")

    # Vẽ thân robot (màu đỏ)
    robot_radius = 6
    draw.ellipse(
        (center_x - robot_radius, center_y - robot_radius,
         center_x + robot_radius, center_y + robot_radius),
        fill="red"
    )

    # Vẽ hướng trước (màu xanh lá)
    arrow_len = 20
    draw.line((center_x, center_y, center_x + arrow_len, center_y), fill="green", width=2)

    # Hiển thị ảnh lên canvas
    tk_img = ImageTk.PhotoImage(image)

    if hasattr(canvas, "map_image"):
        canvas.itemconfig(canvas.map_image, image=tk_img)
    else:
        canvas.map_image = canvas.create_image(0, 0, anchor="nw", image=tk_img)

    canvas.image = tk_img  # giữ tham chiếu ảnh để không bị xóa bởi garbage collector
