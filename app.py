# app.py
import tkinter as tk
import threading
import numpy as np
from encoder_handler import positions, get_robot_pose
from lidar_map_drawer import update_ogm_map, draw_ogm_on_canvas, draw_zoomed_lidar_map
from PIL import Image, ImageTk
import time

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Robot")
        self.root.geometry("1100x700")

        self.running = threading.Event()
        self.running.set()

        self.sidebar = tk.Frame(root, width=250, bg="#2c3e50")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.buttons = []
        self.active_button = None

        tk.Label(self.sidebar, text="\U0001F4CB MENU", bg="#2c3e50", fg="white", font=("Arial", 14, "bold")).pack(pady=20)
        self.add_sidebar_button("\U0001F3E1 Trang chu", self.show_home)
        self.add_sidebar_button("\U0001F6F9 Ban do", self.show_map)
        self.add_sidebar_button("\U0001F4F6 Quet ban do", self.show_scan_map)
        self.add_sidebar_button("\U0001F4BE Du lieu", self.show_data)
        self.add_sidebar_button("\U0001F4C2 Thu muc", self.show_folder)
        self.add_sidebar_button("\U0001F916 Robot", self.show_robot)
        self.add_sidebar_button("\U0001F6E0 Cai dat", self.show_settings)

        self.content = tk.Frame(root, bg="white")
        self.content.pack(side="right", expand=True, fill="both")

        self.encoder_labels = {}
        self.main_map_canvas = None
        self.zoom_map_canvas = None
        self.scan_canvas = None
        self.path_label = None

        self.map_size = 10.0
        self.resolution = 0.1
        self.cells = int(self.map_size / self.resolution)
        self.ogm_map = np.ones((self.cells, self.cells), dtype=np.uint8) * 255
        self.visited_map = np.zeros((60, 60), dtype=np.uint8)
        self.robot_pose = (5.0, 5.0, 0.0)
        self.robot_pos_xy = [30, 30]
        self.visited_map[self.robot_pos_xy[1]][self.robot_pos_xy[0]] = 255

        # === Visited cells ===
        self.step_size = 0.2
        self.visited_cells = set()
        self.last_save_time = time.time()

        self.show_home()

    def add_sidebar_button(self, label, command):
        btn = tk.Button(self.sidebar, text=label, bg="#34495e", fg="white", font=("Arial", 12), height=2, anchor="w", padx=20, relief="flat")
        btn.pack(fill="x", pady=2)
        btn.config(command=lambda b=btn, c=command: self.on_sidebar_click(b, c))
        self.buttons.append(btn)

    def on_sidebar_click(self, button, command):
        if self.active_button:
            self.active_button.config(bg="#34495e")
        button.config(bg="#1abc9c")
        self.active_button = button
        command()

    def show_home(self):
        self.update_content("\U0001F3E1 Đây là Trang chủ")

    def show_map(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        map_frame = tk.Frame(self.content, bg="white")
        map_frame.pack(fill="both", expand=True)
        map_frame.grid_rowconfigure(0, weight=3)
        map_frame.grid_rowconfigure(1, weight=1)
        map_frame.grid_columnconfigure(0, weight=1)
        map_frame.grid_columnconfigure(1, weight=1)

        self.main_map_canvas = tk.Canvas(map_frame, bg="white")
        self.main_map_canvas.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.zoom_map_canvas = tk.Canvas(map_frame, bg="white", width=200, height=200)
        self.zoom_map_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        btn_frame = tk.Frame(map_frame, bg="white")
        btn_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.save_btn = tk.Button(btn_frame, text="Lưu bản đồ", width=15)
        self.save_btn.pack(pady=5)

        self.clear_btn = tk.Button(btn_frame, text="Xóa bản đồ", width=15)
        self.clear_btn.pack(pady=5)

        self.path_btn = tk.Button(btn_frame, text="Vẽ đường đi", width=15)
        self.path_btn.pack(pady=5)

        self.save_png_btn = tk.Button(btn_frame, text="Lưu PNG Map", command=self.save_visited_png, width=15)  # 🔄 NEW
        self.save_png_btn.pack(pady=5)  # 🔄 NEW

        self.path_label = tk.Label(btn_frame, text="Số đường đi: 0", bg="white", font=("Arial", 11))
        self.path_label.pack(pady=10)

    def show_scan_map(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.content, bg="white")
        frame.pack(fill="both", expand=True)

        self.scan_canvas = tk.Canvas(frame, bg="white")
        self.scan_canvas.pack(expand=True, fill="both")

        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🧹 Làm mới", command=self.update_scan_map, width=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="💾 Lưu bản đồ", command=self.save_scan_map, width=15).pack(side="left", padx=10)

        self.update_scan_map()

    def update_scan_map(self):
        self.visited_map[self.robot_pos_xy[1]][self.robot_pos_xy[0]] = 255
        img = Image.fromarray(self.visited_map, mode='L').resize((400, 400))
        img = img.convert("RGB")
        self.tk_scan_img = ImageTk.PhotoImage(img)
        self.scan_canvas.delete("all")
        self.scan_canvas.create_image(0, 0, anchor="nw", image=self.tk_scan_img)

    def save_scan_map(self):
        img = Image.fromarray(self.visited_map, mode='L')
        img.save("/home/dat/LuanVan/visited_cells_map.png")
        print("✅ Đã lưu visited_map.png")

    def save_visited_png(self):  # 🔄 NEW
        size = 60
        img = Image.new("L", (size, size), 0)
        for x, y in self.visited_cells:
            if 0 <= x < size and 0 <= y < size:
                img.putpixel((x, y), 255)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img = img.resize((400, 400), resample=Image.NEAREST)
        img.save("/home/dat/LuanVan/visited_cells_map.png")
        print("✅ Đã lưu visited_cells_map.png")

    def show_data(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        tk.Label(self.content, text="\U0001F4BE Dữ liệu robot", font=("Arial", 20), bg="white").pack(pady=20)

    def show_folder(self):
        self.update_content("\U0001F4C2 Thư mục lưu file")

    def show_robot(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.canvas = tk.Canvas(self.content, bg="white")
        self.canvas.pack(expand=True, fill="both")
        self.encoder_labels = {}
        self.canvas.bind("<Configure>", self.draw_robot_centered)

    def show_settings(self):
        self.update_content("\U0001F6E0 Cài đặt hệ thống")

    def update_content(self, text):
        for widget in self.content.winfo_children():
            widget.destroy()
        tk.Label(self.content, text=text, font=("Arial", 20), bg="white").pack(expand=True)

    def draw_robot_centered(self, event):
        self.canvas.delete("all")
        for lbl in self.encoder_labels.values():
            lbl.destroy()
        self.encoder_labels.clear()
        width, height = event.width, event.height
        car_w, car_h = 200, 300
        x0 = (width - car_w) // 2
        y0 = (height - car_h) // 2
        x1 = x0 + car_w
        y1 = y0 + car_h
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="#bdc3c7", outline="black", width=2)
        wheel_pos = {
            "E1": (x0 - 45, y0 + 10),
            "E2": (x0 - 45, y1 - 40),
            "E3": (x1 + 5, y0 + 10),
            "E4": (x1 + 5, y1 - 40),
        }
        for name, (x, y) in wheel_pos.items():
            self.canvas.create_rectangle(x, y, x + 40, y + 30, fill="#2c3e50")
            self.canvas.create_text(x + 20, y - 10, text=name, font=("Arial", 9))
            lbl = tk.Label(self.canvas, text=f"Encoder: {positions[name]}", bg="white", font=("Arial", 9))
            lbl.place(x=x - 5, y=y + 35)
            self.encoder_labels[name] = lbl

    def update_lidar_map(self, data):
        try:
            pose = data.get("pose", {})
            if "x" in pose and "y" in pose:
                cell = (int(pose["x"] / self.step_size), int(pose["y"] / self.step_size))
                self.visited_cells.add(cell)
                if 0 <= cell[0] < 60 and 0 <= cell[1] < 60:
                    self.visited_map[cell[1]][cell[0]] = 255

                if time.time() - self.last_save_time > 10:
                    with open("visited_map.txt", "w") as f:
                        for c in self.visited_cells:
                            f.write(f"{c[0]} {c[1]}\n")
                    self.last_save_time = time.time()
                    print("[App] 💾 Đã lưu visited_map.txt")

            self.robot_pose = get_robot_pose()

            if self.main_map_canvas and self.main_map_canvas.winfo_exists():
                draw_ogm_on_canvas(self.main_map_canvas, self.ogm_map, self.robot_pose, visited_cells=self.visited_cells)

            if self.zoom_map_canvas and self.zoom_map_canvas.winfo_exists():
                draw_zoomed_lidar_map(self.zoom_map_canvas, data)

        except Exception as e:
            print("[App] ⚠️ Lỗi khi cập nhật bản đồ:", e)

    def draw_path(self):
        print("[App] 🚗 Đã bấm nút vẽ đường đi")
        if self.path_label:
            current = int(self.path_label.cget("text").split(":")[-1].strip())
            self.path_label.config(text=f"Số thứ tự: {current + 1}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
