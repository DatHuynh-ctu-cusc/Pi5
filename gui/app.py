import tkinter as tk
from gui.home_tab import HomeTab
from gui.map_tab import MapTab
from gui.scan_tab import ScanTab
from gui.data_tab import DataTab
from gui.folder_tab import FolderTab
from gui.robot_tab import RobotTab
from gui.settings_tab import SettingsTab
from lidar_map_drawer import set_drawing_enabled

class SimpleApp:
    def __init__(self, root, bt_client=None):
        self.root = root
        self.bt_client = bt_client
        self.root.title("App Robot")
        self.root.geometry("900x600")

        # Sidebar
        self.sidebar = tk.Frame(root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="📋 MENU", bg="#2c3e50", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=20)

        # Các nút menu
        self.menu_buttons = []
        self.tabs = {}
        self.tab_order = [
            ("🏠 Trang chủ", "home"),
            ("🗺️ Bản đồ", "map"),
            ("📶 Quét bản đồ", "scan"),
            ("💾 Dữ liệu", "data"),
            ("📁 Thư mục", "folder"),
            ("🤖 Robot", "robot"),
            ("🛠️ Cài đặt", "settings"),
        ]
        self.main_content = tk.Frame(root, bg="white")
        self.main_content.pack(side="left", fill="both", expand=True)

        # Khởi tạo từng tab, lưu vào self.tabs
        self.tabs["home"] = HomeTab(self.main_content, self)
        self.tabs["map"] = MapTab(self.main_content, self)
        self.tabs["scan"] = ScanTab(self.main_content, self)
        self.tabs["data"] = DataTab(self.main_content, self)
        self.tabs["folder"] = FolderTab(self.main_content, self)
        self.tabs["robot"] = RobotTab(self.main_content, self)
        self.tabs["settings"] = SettingsTab(self.main_content, self)

        # Tạo các button sidebar và bắt sự kiện chuyển tab
        for text, tab_name in self.tab_order:
            btn = tk.Label(self.sidebar, text=text, bg="#34495e", fg="white",
                           font=("Arial", 12), padx=10, pady=8, cursor="hand2")
            btn.pack(fill="x", padx=15, pady=4)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1abc9c"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495e"))
            btn.bind("<Button-1>", lambda e, t=tab_name: self.show_tab(t))
            self.menu_buttons.append(btn)

        # Hiện mặc định là tab Trang chủ
        self.show_tab("home")
        self.tabs["scan"] = ScanTab(self.main_content, self)

    def show_tab(self, tab_name):
        for t in self.tabs.values():
            t.pack_forget()
        self.tabs[tab_name].pack(fill="both", expand=True)

        # ✅ Tự động bật/tắt chế độ vẽ
        if tab_name == "scan":
            set_drawing_enabled(True)
            print("[App] ✅ Bật vẽ LiDAR (ScanTab)")
        elif tab_name == "map":
            set_drawing_enabled(False)
            print("[App] 🚫 Tắt vẽ LiDAR (MapTab)")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()