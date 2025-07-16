# app/map_view.py

import tkinter as tk

class MapView:
    def __init__(self, parent, app):
        self.app = app  # truyền xuống nếu cần dùng tới MainApp
        tk.Label(parent, text="BẢN ĐỒ HOẠT ĐỘNG CỦA ROBOT",
                 font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
        # Canvas bản đồ chính
        self.main_map = tk.Canvas(parent, width=680, height=300, bg="#ecf0f1", highlightbackground="#bdc3c7")
        self.main_map.pack(pady=5)

        # Bottom layout
        bottom_frame = tk.Frame(parent, bg="white")
        bottom_frame.pack(fill="x", padx=10, pady=10)

        # Sub-map nhỏ
        self.sub_map = tk.Canvas(bottom_frame, width=300, height=200, bg="#dfe6e9", highlightbackground="#bdc3c7")
        self.sub_map.pack(side="left", padx=5)

        # Khung nút chức năng
        control_frame = tk.Frame(bottom_frame, bg="white")
        control_frame.pack(side="left", fill="both", expand=True, padx=10)

        tk.Button(control_frame, text="🗂 Chọn bản đồ", font=("Arial", 11), width=20,
                  command=self.select_map).pack(pady=4)
        tk.Button(control_frame, text="🗑 Xoá bản đồ", font=("Arial", 11), width=20,
                  command=self.clear_map).pack(pady=4)
        tk.Button(control_frame, text="✏️ Vẽ đường đi", font=("Arial", 11), width=20,
                  command=self.draw_path).pack(pady=4)
        tk.Button(control_frame, text="❌ Xoá đường đi", font=("Arial", 11), width=20,
                  command=self.clear_path).pack(pady=4)

        self.robot_status_label = tk.Label(control_frame, text="Trạng thái: Di chuyển", font=("Arial", 11, "bold"),
                                           bg="green", fg="white", width=20)
        self.robot_status_label.pack(pady=10)

    # ==== Các hàm xử lý nút (bạn sẽ bổ sung thêm nếu cần) ====
    def select_map(self):
        print("🗂 Chọn bản đồ")

    def clear_map(self):
        print("🗑 Đã xoá bản đồ!")

    def draw_path(self):
        print("✏️ Vẽ đường đi")

    def clear_path(self):
        print("❌ Đã xoá đường đi")

    # Nếu muốn cập nhật trạng thái robot từ nơi khác:
    def update_robot_status(self, status):
        if status == "moving":
            self.robot_status_label.config(text="Trạng thái: Di chuyển", bg="green")
        elif status == "stuck":
            self.robot_status_label.config(text="Trạng thái: Mắc kẹt", bg="red")
