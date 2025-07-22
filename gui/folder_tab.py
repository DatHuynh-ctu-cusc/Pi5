import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class FolderTab(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="white")
        self.app = app
        self.maps_folder = "data/maps"

        tk.Label(self, text="🗂 DANH SÁCH BẢN ĐỒ ĐÃ LƯU",
                 font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(pady=10)

        self.image_frame = tk.Frame(self, bg="white")
        self.image_frame.pack(pady=5, padx=10, fill="both", expand=True)

        tk.Button(self, text="🗑 Xoá tất cả bản đồ đã lưu", font=("Arial", 11), bg="#e74c3c", fg="white",
                  command=self.delete_all_maps).pack(pady=(5, 15))

        self.load_saved_maps()

    def load_saved_maps(self):
        # Xóa ảnh cũ
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(self.maps_folder):
            os.makedirs(self.maps_folder)

        png_files = sorted(
            [f for f in os.listdir(self.maps_folder) if f.startswith("scan_map_") and f.endswith(".png")],
            reverse=True
        )

        if not png_files:
            tk.Label(self.image_frame, text="⚠️ Không có bản đồ nào được lưu.", font=("Arial", 12), bg="white", fg="red").pack()
            return

        for i, filename in enumerate(png_files[:3]):
            try:
                img_path = os.path.join(self.maps_folder, filename)
                img = Image.open(img_path)
                img = img.resize((250, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                panel = tk.Label(self.image_frame, image=photo, bg="white", cursor="hand2")
                panel.image = photo
                panel.grid(row=0, column=i, padx=10, pady=5)

                label = tk.Label(self.image_frame, text=filename, font=("Arial", 10), bg="white")
                label.grid(row=1, column=i)

                # Bind click để mở ảnh full
                panel.bind("<Button-1>", lambda e, path=img_path: self.open_full_image(path))

            except Exception as e:
                print(f"[Folder] ❌ Lỗi khi tải ảnh {filename}:", e)

    def open_full_image(self, path):
        try:
            top = tk.Toplevel(self)
            top.title(f"🖼 Xem bản đồ: {path}")

            img = Image.open(path)
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(top, image=photo)
            lbl.image = photo
            lbl.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở ảnh: {e}")

    def delete_all_maps(self):
        confirm = messagebox.askyesno("Xác nhận xoá", "Bạn có chắc chắn muốn xoá tất cả bản đồ?")
        if confirm:
            deleted = 0
            for f in os.listdir(self.maps_folder):
                if f.startswith("scan_map_") and f.endswith(".png"):
                    try:
                        os.remove(os.path.join(self.maps_folder, f))
                        deleted += 1
                    except Exception as e:
                        print(f"Lỗi khi xoá {f}: {e}")
            messagebox.showinfo("Đã xoá", f"Đã xoá {deleted} bản đồ.")
            self.load_saved_maps()
