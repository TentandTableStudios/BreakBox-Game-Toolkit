import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class HexEditorPanel:
    def __init__(self, parent):
        self.parent = parent
        self.file_path = None
        self.bytes_data = b""
        self.create_widgets()

    def create_widgets(self):
        # File open/save controls
        top = tk.Frame(self.parent)
        top.pack(anchor="nw", fill="x", pady=8, padx=8)
        tk.Button(top, text="Open File", command=self.open_file).pack(side="left")
        tk.Button(top, text="Save File", command=self.save_file).pack(side="left", padx=8)
        self.path_label = tk.Label(top, text="No file loaded")
        self.path_label.pack(side="left", padx=10)

        # Hex view
        self.hex_text = scrolledtext.ScrolledText(self.parent, width=80, height=20, font=("Consolas", 10))
        self.hex_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.hex_text.config(state="disabled")

        # Edit controls
        edit_frame = tk.Frame(self.parent)
        edit_frame.pack(anchor="w", pady=2, padx=8)
        tk.Label(edit_frame, text="Offset:").pack(side="left")
        self.offset_entry = tk.Entry(edit_frame, width=8)
        self.offset_entry.pack(side="left", padx=2)
        tk.Label(edit_frame, text="New Byte (hex):").pack(side="left")
        self.byte_entry = tk.Entry(edit_frame, width=4)
        self.byte_entry.pack(side="left", padx=2)
        tk.Button(edit_frame, text="Apply Edit", command=self.edit_byte).pack(side="left", padx=6)

    def open_file(self):
        path = filedialog.askopenfilename(title="Open file", filetypes=[("All files", "*.*")])
        if path:
            try:
                with open(path, "rb") as f:
                    self.bytes_data = f.read()
                self.file_path = path
                self.show_bytes()
                self.path_label.config(text=path)
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to read file:\n{e}")

    def save_file(self):
        if not self.file_path:
            messagebox.showwarning("No File", "No file loaded.")
            return
        try:
            with open(self.file_path, "wb") as f:
                f.write(self.bytes_data)
            messagebox.showinfo("Saved", f"File saved: {self.file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def show_bytes(self):
        self.hex_text.config(state="normal")
        self.hex_text.delete("1.0", "end")
        data = self.bytes_data
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_chunk = ' '.join(f"{b:02X}" for b in chunk)
            ascii_chunk = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:08X}  {hex_chunk:<47}  {ascii_chunk}")
        self.hex_text.insert("end", "\n".join(lines))
        self.hex_text.config(state="disabled")

    def edit_byte(self):
        try:
            offset = int(self.offset_entry.get(), 16 if 'x' in self.offset_entry.get().lower() or self.offset_entry.get().startswith('0x') else 10)
            value = int(self.byte_entry.get(), 16)
            if not (0 <= offset < len(self.bytes_data)):
                raise ValueError("Offset out of range.")
            if not (0 <= value <= 255):
                raise ValueError("Value must be a byte (00-FF).")
            ba = bytearray(self.bytes_data)
            ba[offset] = value
            self.bytes_data = bytes(ba)
            self.show_bytes()
            messagebox.showinfo("Edited", f"Byte at offset {offset:X} set to {value:02X}.")
        except Exception as e:
            messagebox.showerror("Edit Error", str(e))
