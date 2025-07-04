from tkinter import simpledialog
import tkinter as tk
from tkinter import ttk, messagebox
import os

def hien_thi_admin_screen(username, callback_logout):
    win = tk.Toplevel()
    win.title(f"Admin: {username}")
    win.attributes("-fullscreen", True)
    win.resizable(True, True)

    fullscreen = [True]
    DATA_FOLDER = "data/maps"

    sidebar = tk.Frame(win, width=200, bg="#2c3e50")
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(win, bg="#ecf0f1")
    content.pack(side="right", expand=True, fill="both")

    tk.Label(sidebar, text=f"👤 Admin", fg="white", bg="#2c3e50", font=("Arial", 14, "bold")).pack(pady=20)

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    def doc_trang_thai_robot():
    # Đọc đúng từ data/robot_last.txt
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "../../data/robot_last.txt")
        path = os.path.abspath(path)

        if not os.path.exists(path):
            return False, "Chưa có dữ liệu"
        try:
            with open(path, "r") as f:
                data = f.read().strip()
            if data:
                return True, data
            else:
                return False, "File trống"
        except Exception as e:
            return False, f"Lỗi: {e}"

    def show_status():
        clear_content()
        tk.Label(content, text="📊 Trạng thái Pi5", font=("Arial", 16), bg="#ecf0f1").pack(pady=10)

        import socket
        def lay_dia_chi_ip_thuc():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except:
                return "Không xác định"

        ip_pi5 = lay_dia_chi_ip_thuc()

        import subprocess
        def ping(ip):
            try:
                subprocess.check_output(["ping", "-c", "1", "-W", "1", ip], stderr=subprocess.DEVNULL)
                return True
            except:
                return False

        connected_pi4 = ping("192.168.1.44")

        tk.Label(content, text=f"Địa chỉ IP: {ip_pi5}", font=("Arial", 12), bg="#ecf0f1").pack(pady=2)
        tk.Label(content, text=f"Tình trạng kết nối: {'🟢 Đã kết nối với Pi4' if connected_pi4 else '⚪ Không kết nối'}", font=("Arial", 12), bg="#ecf0f1").pack(pady=2)

        tk.Label(content, text="Tình trạng động cơ: Chưa rõ", font=("Arial", 12), bg="#ecf0f1").pack(pady=2)
        tk.Label(content, text="Tình trạng cảm biến: Chưa rõ", font=("Arial", 12), bg="#ecf0f1").pack(pady=2)
        tk.Label(content, text="Trạng thái xe: Đang xác định...", font=("Arial", 12), bg="#ecf0f1").pack(pady=2)

        trang_thai, du_lieu = doc_trang_thai_robot()
        if trang_thai:
            text = f"📨 Dữ liệu từ robot: {du_lieu}"
            fg = "green"
        else:
            text = f"⚠️ Dữ liệu từ robot: {du_lieu}"
            fg = "orange"

        du_lieu_label = tk.Label(content, text=text, font=("Arial", 12), fg=fg, bg="#ecf0f1")
        du_lieu_label.pack(pady=10)

    def show_map():
        clear_content()
        toado = [(0.5, 0.5), (1.0, 0.8), (1.2, 0.6)]
        frame_map = tk.Frame(content, bg="white", bd=1, relief="solid")
        frame_map.pack(expand=True, fill="both")
        label_map = tk.Label(frame_map, text="Hiển thị bản đồ", font=("Arial", 16), bg="white")
        label_map.place(relx=0.5, rely=0.05, anchor="n")
        canvas = tk.Canvas(frame_map, bg="white")
        canvas.pack(expand=True, fill="both", padx=10, pady=10)
        for x, y in toado:
            px = int(x * 50 + 200)
            py = int(y * 50 + 200)
            canvas.create_oval(px - 2, py - 2, px + 2, py + 2, fill="red")
        frame_control = tk.Frame(content, bg="#ddd", bd=1, relief="solid")
        frame_control.pack(fill="x")
        btn_start = tk.Button(frame_control, text="Start", width=15)
        btn_stop = tk.Button(frame_control, text="Stop", width=15)
        btn_reset = tk.Button(frame_control, text="Reset", width=15)
        label_status = tk.Label(frame_control, text="Trạng thái: ---", width=20, anchor="w")
        btn_start.grid(row=0, column=0, padx=5, pady=5)
        btn_stop.grid(row=0, column=1, padx=5, pady=5)
        btn_reset.grid(row=0, column=2, padx=5, pady=5)
        label_status.grid(row=0, column=3, padx=5, pady=5)
        def luu_ban_do():
            if not toado:
                messagebox.showwarning("Chưa có dữ liệu", "Chưa có điểm nào để lưu.")
                return
            filename = simpledialog.askstring("Lưu bản đồ", "Nhập tên file:")
            if not filename:
                return
            if not os.path.exists(DATA_FOLDER):
                os.makedirs(DATA_FOLDER)
            path = os.path.join(DATA_FOLDER, f"{filename}.txt")
            try:
                with open(path, "w") as f:
                    for x, y in toado:
                        f.write(f"{x},{y}\n")
                messagebox.showinfo("Thành công", f"Đã lưu bản đồ vào {path}")
            except Exception as e:
                messagebox.showerror("Lỗi khi lưu", str(e))
        btn_save = tk.Button(frame_control, text="Lưu bản đồ", width=15, command=luu_ban_do)
        btn_save.grid(row=0, column=4, padx=5, pady=5)
        frame_control.columnconfigure((0, 1, 2, 3, 4), weight=1)

    def show_logs():
        clear_content()
        tk.Label(content, text="Nhật ký hoạt động", font=("Arial", 16), bg="#ecf0f1").pack(pady=10)
        table = ttk.Treeview(content, columns=("user", "action", "time"), show="headings", height=8)
        table.pack(padx=10, pady=10)
        table.heading("user", text="Người dùng")
        table.heading("action", text="Hành động")
        table.heading("time", text="Thời gian")
        logs = [("admin", "Đăng nhập", "10:15"), ("user", "Xem bản đồ", "10:17"), ("admin", "Xóa dữ liệu", "10:18")]
        for row in logs:
            table.insert("", "end", values=row)

    def show_settings():
        clear_content()
        tk.Label(content, text="Cài đặt hệ thống (đang phát triển)", font=("Arial", 16), bg="#ecf0f1").pack(pady=50)

    def show_data_files():
        clear_content()
        tk.Label(content, text="📂 Dữ liệu", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)
        main_frame = tk.Frame(content)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        left_frame = tk.Frame(main_frame, width=200)
        left_frame.pack(side="left", fill="y")
        tk.Label(left_frame, text="Tên file bản đồ đã vẽ", font=("Arial", 12)).pack()
        listbox = tk.Listbox(left_frame, height=25, width=30)
        listbox.pack(pady=10, padx=5, fill="y")
        right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
        right_frame.pack(side="left", expand=True, fill="both", padx=10)
        tk.Label(right_frame, text="Hiển thị bản đồ từ file", font=("Arial", 12)).pack()
        canvas = tk.Canvas(right_frame, bg="white")
        canvas.pack(expand=True, fill="both", padx=10, pady=10)
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".txt") or f.endswith(".csv")]
        for f in files:
            listbox.insert("end", f)
        def xem_lai():
            selected = listbox.get("anchor")
            if not selected:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn một bản đồ.")
                return
            filepath = os.path.join(DATA_FOLDER, selected)
            try:
                canvas.delete("all")
                with open(filepath, "r") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if len(parts) >= 2:
                            x = int(float(parts[0]) * 50 + 200)
                            y = int(float(parts[1]) * 50 + 200)
                            canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")
            except Exception as e:
                messagebox.showerror("Lỗi khi đọc file", str(e))
        tk.Button(left_frame, text="Xem lại", command=xem_lai).pack(pady=5)

    def toggle_fullscreen():
        fullscreen[0] = not fullscreen[0]
        win.attributes("-fullscreen", fullscreen[0])

    # Sidebar
    tk.Button(sidebar, text="📍 Bản đồ", width=20, command=show_map).pack(pady=10)
    tk.Button(sidebar, text="📂 Dữ liệu", width=20, command=show_data_files).pack(pady=10)
    tk.Button(sidebar, text="📊 Trạng thái", width=20, command=show_status).pack(pady=10)
    tk.Button(sidebar, text="⚙️ Cài đặt", width=20, command=show_settings).pack(pady=10)
    tk.Button(sidebar, text="📜 Nhật ký", width=20, command=show_logs).pack(side="bottom", pady=(10, 0))
    tk.Button(sidebar, text="🖥️ Toàn màn hình", width=20, command=toggle_fullscreen).pack(side="bottom", pady=(0, 0))
    tk.Button(sidebar, text="🔒 Đăng xuất", width=20, fg="red", command=lambda: logout()).pack(side="bottom", pady=(0, 20))

    def logout():
        win.destroy()
        callback_logout()

    show_map()
