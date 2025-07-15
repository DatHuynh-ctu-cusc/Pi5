# app/data_view.py
import tkinter as tk

def show_data(app):
    app.clear_main_content()
    tk.Label(app.main_content, text="DỮ LIỆU TRAO ĐỔI", font=("Arial", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10))
    recv_frame = tk.Frame(app.main_content, bg="white")
    recv_frame.pack(pady=10, padx=20, fill="x")
    tk.Label(recv_frame, text="Dữ liệu nhận", font=("Arial", 12, "bold"), bg="white", anchor="w").pack(anchor="w")
    app.recv_text = tk.Text(recv_frame, height=10, width=90, bg="#ecf0f1", relief="solid", bd=1, font=("Courier", 10))
    app.recv_text.pack(pady=5, fill="x")
    send_frame = tk.Frame(app.main_content, bg="white")
    send_frame.pack(pady=10, padx=20, fill="x")
    tk.Label(send_frame, text="Dữ liệu gửi", font=("Arial", 12, "bold"), bg="white", anchor="w").pack(anchor="w")
    app.send_text = tk.Text(send_frame, height=10, width=90, bg="#ecf0f1", relief="solid", bd=1, font=("Courier", 10))
    app.send_text.pack(pady=5, fill="x")
