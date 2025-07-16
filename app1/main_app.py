# app/main_app.py

import tkinter as tk
from app.sidebar import Sidebar
from app.home_view import HomeView
from app.map_view import MapView
from app.scan_map_view import show_scan_map
from app.data_view import show_data   
from app.folder_view import show_folder
from app.robot_view import show_robot
from app.settings_view import show_settings
from app.bluetooth_handler import BluetoothHandler

class MainApp:
    def __init__(self, root, bt_client=None):
        self.root = root
        self.bt_client = bt_client
        self.root.title("App Robot")
        self.root.geometry("900x600")

        # Bluetooth handler (nếu cần)
        self.bt_client = BluetoothHandler()

        # Sidebar/menu
        self.sidebar = Sidebar(self.root, self)

        # Khung nội dung chính
        self.main_content = tk.Frame(self.root, bg="white")
        self.main_content.pack(side="left", fill="both", expand=True)

        # Mặc định vào home
        self.show_home()

    def update_lidar_map(self, lidar_data):
        self.root.after(0, lambda: self._update_lidar_map_safe(lidar_data))

    def _update_lidar_map_safe(self, lidar_data):
        from app.scan_map_view import update_lidar_map
        update_lidar_map(self, lidar_data)
    

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # ==== Các hàm chuyển tab (gọi view tương ứng) ====
    def show_home(self):
        self.clear_main_content()
        HomeView(self.main_content, self)

    def show_map(self):
        self.clear_main_content()
        MapView(self.main_content, self)

    def show_scan_map(self):
        self.clear_main_content()
        show_scan_map(self)  # truyền self là app


    def show_data(self):
        self.clear_main_content()
        show_data(self)


    def show_folder(self):
        self.clear_main_content()
        show_folder(self)

    def show_robot(self):
        self.clear_main_content()
        show_robot(self)


    def show_settings(self):
        self.clear_main_content()
        show_settings(self)


# ==== Chạy ứng dụng ====
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
