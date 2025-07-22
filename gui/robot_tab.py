import tkinter as tk

class RobotTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        tk.Label(self, text="Thông tin Robot", font=("Arial", 16), bg="white").pack(pady=50)
        # Bạn có thể bổ sung thêm trạng thái encoder, trạng thái robot v.v. nếu muốn
