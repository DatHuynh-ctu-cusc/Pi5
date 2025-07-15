# app/folder_view.py
import tkinter as tk
import os
from PIL import Image, ImageTk
from tkinter import messagebox

def show_folder(app):
    maps_folder = "data/maps"
    app.clear_main_content()
    tk.Label(app.main_content, text="🗂 DANH SÁCH BẢN ĐỒ ĐÃ LƯU", font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

    image_frame = tk.Frame(app.main_content, bg="white")
    image_frame.pack(pady=5, padx=10, fill="both", expand=True)

    tk.Button(
        app.main_content,
        text="🗑 Xoá tất cả bản đồ đã lưu",
        font=("Arial", 11),
        bg="#e74c3c", fg="white",
        command=lambda: delete_all_maps(app)
    ).pack(pady=(5, 15))

    # Hiển thị tối đa 3 ảnh gần nhất
    if not os.path.exists(maps_folder):
        os.makedirs(maps_folder)
    png_files = sorted(
        [f for f in os.listdir(maps_folder) if f.startswith("scan_map_") and f.endswith(".png")],
        reverse=True
    )

    if not png_files:
        tk.Label(image_frame, text="⚠️ Không có bản đồ nào được lưu.", font=("Arial", 12), bg="white", fg="red").pack()
        return

    for i, filename in enumerate(png_files[:3]):
        try:
            img_path = os.path.join(maps_folder, filename)
            img = Image.open(img_path)
            img = img.resize((250, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            panel = tk.Label(image_frame, image=photo, bg="white", cursor="hand2")
            panel.image = photo  # giữ tham chiếu ảnh
            panel.grid(row=0, column=i, padx=10, pady=5)
            label = tk.Label(image_frame, text=filename, font=("Arial", 10), bg="white")
            label.grid(row=1, column=i)
            panel.bind("<Button-1>", lambda e, path=img_path: open_full_image(app, path))
        except Exception as e:
            print(f"[Folder] ❌ Lỗi khi tải ảnh {filename}:", e)

def open_full_image(app, path):
    try:
        top = tk.Toplevel(app.root)
        top.title(f"🖼 Xem bản đồ: {path}")
        img = Image.open(path)
        img = img.resize((800, 600), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(top, image=photo)
        lbl.image = photo
        lbl.pack(padx=10, pady=10)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể mở ảnh: {e}")

def delete_all_maps(app):
    maps_folder = "data/maps"
    confirm = messagebox.askyesno("Xác nhận xoá", "Bạn có chắc chắn muốn xoá tất cả bản đồ?")
    if confirm:
        deleted = 0
        for f in os.listdir(maps_folder):
            if f.startswith("scan_map_") and f.endswith(".png"):
                try:
                    os.remove(os.path.join(maps_folder, f))
                    deleted += 1
                except Exception as e:
                    print(f"Lỗi khi xoá {f}: {e}")
        messagebox.showinfo("Đã xoá", f"Đã xoá {deleted} bản đồ.")
        show_folder(app)
