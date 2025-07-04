import tkinter as tk

def hien_thi_user_screen(username, callback_logout):
    win = tk.Toplevel()
    win.title(f"User: {username}")
    win.attributes("-fullscreen", True)
    win.resizable(True, True)

    fullscreen = [True]

    sidebar = tk.Frame(win, width=200, bg="#34495e")
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(win, bg="#ecf0f1")
    content.pack(side="right", expand=True, fill="both")

    tk.Label(sidebar, text=f"👤 {username}", fg="white", bg="#34495e", font=("Arial", 14, "bold")).pack(pady=20)

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    def show_map():
        clear_content()
        frame_map = tk.Frame(content, bg="white", bd=1, relief="solid")
        frame_map.pack(expand=True, fill="both")

        label_map = tk.Label(frame_map, text="Hiển thị bản đồ", font=("Arial", 16), bg="white")
        label_map.place(relx=0.5, rely=0.5, anchor="center")

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

        frame_control.columnconfigure((0, 1, 2, 3), weight=1)

    def show_lora():
        clear_content()
        tk.Label(content, text="Dữ liệu Lora (demo)", font=("Arial", 16), bg="#ecf0f1").pack(pady=10)

        log_text = tk.Text(content, wrap="word", height=15, width=60)
        log_text.pack(padx=20, pady=10)

        sample_data = [
            "[LORA] 10:10 → Tín hiệu nhận được từ robot.",
            "[LORA] 10:12 → Cảnh báo vật cản phía trước.",
            "[LORA] 10:15 → RSSI ổn định ở -68dBm.",
        ]
        for line in sample_data:
            log_text.insert("end", line + "\n")

        log_text.config(state="disabled")

    def toggle_fullscreen():
        fullscreen[0] = not fullscreen[0]
        win.attributes("-fullscreen", fullscreen[0])

    tk.Button(sidebar, text="📍 Bản đồ", width=20, command=show_map).pack(pady=10)
    tk.Button(sidebar, text="📡 Lora", width=20, command=show_lora).pack(pady=10)

    tk.Button(sidebar, text="🔒 Đăng xuất", width=20, fg="red", command=lambda: logout()).pack(side="bottom", pady=(0, 20))
    tk.Button(sidebar, text="🖥️ Toàn màn hình", width=20, command=toggle_fullscreen).pack(side="bottom", pady=(0, 0))

    def logout():
        win.destroy()
        callback_logout()

    show_map()
