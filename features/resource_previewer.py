import os
import tkinter as tk
from tkinter import filedialog, PhotoImage
from ttkbootstrap import ttk
from PIL import Image, ImageTk

SUPPORTED_IMG = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
SUPPORTED_TXT = ('.txt', '.json', '.xml', '.cfg', '.ini')

def ResourcePreviewerPanel(parent):
    frame = ttk.Frame(parent, padding=12)
    frame.pack(fill="both", expand=True)

    top = ttk.Frame(frame)
    top.pack(fill="x")
    ttk.Button(top, text="Open File...", command=lambda: open_file()).pack(side="left", padx=4, pady=6)

    preview_frame = ttk.Frame(frame)
    preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
    img_label = ttk.Label(preview_frame)
    img_label.pack()
    text_box = tk.Text(preview_frame, height=24, wrap="word")
    text_box.pack(fill="both", expand=True)
    text_box.config(state="disabled")

    def clear_preview():
        img_label.config(image="", text="")
        text_box.config(state="normal")
        text_box.delete('1.0', 'end')
        text_box.config(state="disabled")

    def open_file():
        path = filedialog.askopenfilename(
            title="Preview Resource",
            filetypes=[
                ("All Supported", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.txt;*.json;*.xml;*.cfg;*.ini;*.wav;*.mp3;*.ogg"),
                ("All Files", "*.*")]
        )
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        clear_preview()

        if ext in SUPPORTED_IMG:
            try:
                img = Image.open(path)
                img.thumbnail((320, 320))
                tkimg = ImageTk.PhotoImage(img)
                img_label.image = tkimg  # Prevent garbage collection
                img_label.config(image=tkimg)
            except Exception as e:
                img_label.config(text=f"Image failed to load: {e}")
        elif ext in SUPPORTED_TXT:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                text_box.config(state="normal")
                text_box.insert("end", txt)
                text_box.config(state="disabled")
            except Exception as e:
                text_box.config(state="normal")
                text_box.insert("end", f"Text failed to load: {e}")
                text_box.config(state="disabled")
        elif ext in ('.wav', '.mp3', '.ogg'):
            img_label.config(text=f"Audio File: {os.path.basename(path)}\n(size: {os.path.getsize(path)} bytes)")
            # (Optional: Use pygame or playsound to preview)
        else:
            img_label.config(text=f"File: {os.path.basename(path)}\n(size: {os.path.getsize(path)} bytes)")

    return frame
