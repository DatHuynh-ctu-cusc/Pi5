# app/main_app.py
import tkinter as tk
from app.sidebar import setup_sidebar
from app.home_view import show_home
from app.map_view import show_map
from app.scan_map_view import show_scan_map
from app.data_view import show_data
from app.folder_view import show_folder
from app.robot_view import show_robot
from app.settings_view import show_settings
from bluetooth_client import BluetoothClient

class SimpleApp:
    def __init__(self, root, bt_client=None):
        self.root = root
        self.bt_client = bt_client
        self.root.title("App Robot")
        self.root.geometry("900x600")
        self.sidebar = tk.Frame(root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.main_content = tk.Frame(root, bg="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        self.buttons = []
        setup_sidebar(self)
        self.show_home()

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    # Routing
    def show_home(self): show_home(self)
    def show_map(self): show_map(self)
    def show_scan_map(self): show_scan_map(self)
    def show_data(self): show_data(self)
    def show_folder(self): show_folder(self)
    def show_robot(self): show_robot(self)
    def show_settings(self): show_settings(self)

# ==== Chạy app ====
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
