# app/robot_view.py

import tkinter as tk

def show_robot(app):
    app.clear_main_content()
    tk.Label(app.main_content, text="THÔNG TIN ROBOT", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

    # Frame chính
    robot_frame = tk.Frame(app.main_content, bg="white")
    robot_frame.pack(pady=10)

    # Sơ đồ robot + encoder
    left_frame = tk.Frame(robot_frame, bg="white")
    left_frame.grid(row=0, column=0, padx=15)

    canvas = tk.Canvas(left_frame, width=280, height=180, bg="#ecf0f1", highlightbackground="#bdc3c7")
    canvas.pack()
    # Vẽ thân robot
    canvas.create_rectangle(80, 40, 200, 140, outline="#2c3e50", width=3, fill="#bdc3c7")
    # Bánh xe
    canvas.create_rectangle(70, 30, 90, 60, fill="#27ae60")  # Trái trước
    canvas.create_rectangle(190, 30, 210, 60, fill="#27ae60") # Phải trước
    canvas.create_rectangle(70, 120, 90, 150, fill="#27ae60") # Trái sau
    canvas.create_rectangle(190, 120, 210, 150, fill="#27ae60") # Phải sau
    # Nhãn vị trí bánh xe
    canvas.create_text(60, 45, text="E1", font=("Arial", 10, "bold"), fill="#2980b9")
    canvas.create_text(220, 45, text="E3", font=("Arial", 10, "bold"), fill="#2980b9")
    canvas.create_text(60, 135, text="E2", font=("Arial", 10, "bold"), fill="#2980b9")
    canvas.create_text(220, 135, text="E4", font=("Arial", 10, "bold"), fill="#2980b9")

    # Giá trị encoder (hiển thị phải liên tục cập nhật)
    enc_frame = tk.Frame(robot_frame, bg="white")
    enc_frame.grid(row=0, column=1, padx=20, sticky="n")

    tk.Label(enc_frame, text="Giá trị Encoder:", font=("Arial", 13, "bold"), bg="white", fg="#34495e").pack(anchor="w", pady=(0,8))
    label_names = ["E1 (Trái trước)", "E2 (Trái sau)", "E3 (Phải trước)", "E4 (Phải sau)"]
    if not hasattr(app, "encoder_labels"):
        app.encoder_labels = []
    app.encoder_labels.clear()
    for name in label_names:
        lbl = tk.Label(enc_frame, text=f"{name}: --", font=("Arial", 12), bg="white", fg="#34495e", anchor="w")
        lbl.pack(anchor="w")
        app.encoder_labels.append(lbl)

    # Hiển thị pin/nhiệt độ
    info_frame = tk.Frame(enc_frame, bg="white")
    info_frame.pack(anchor="w", pady=(18,0), fill="x")

    app.battery_label = tk.Label(info_frame, text="Pin: -- V", font=("Arial", 12), bg="white", fg="#d35400", anchor="w")
    app.battery_label.pack(anchor="w")
    app.temp_label = tk.Label(info_frame, text="Nhiệt độ: -- °C", font=("Arial", 12), bg="white", fg="#e74c3c", anchor="w")
    app.temp_label.pack(anchor="w")

    # Hàm cập nhật giá trị realtime
    def update_robot_status():
        # Encoder
        vals = getattr(app, "encoder_values", [0,0,0,0])
        for i in range(4):
            value = vals[i] if isinstance(vals, list) and len(vals) > i else (vals.get(f"E{i+1}", 0) if isinstance(vals, dict) else 0)
            app.encoder_labels[i].config(text=f"{label_names[i]}: {value}")
        # Pin
        voltage = getattr(app, "battery_voltage", 0)
        app.battery_label.config(text=f"Pin: {voltage:.2f} V" if voltage else "Pin: -- V")
        # Nhiệt độ
        temp = getattr(app, "temperature", 0)
        app.temp_label.config(text=f"Nhiệt độ: {temp:.1f} °C" if temp else "Nhiệt độ: -- °C")
        app.root.after(500, update_robot_status)
    update_robot_status()

    # Có thể thêm các nút điều khiển nếu cần ở đây

