import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from ttkbootstrap import ttk

MODS_FOLDER = "mods"  # Change as needed

class ModManagerPanel:
    def __init__(self, parent):
        self.parent = parent
        self.create_mods_folder()
        self.mods = []
        self.selected_mod = None
        self.setup_ui()
        self.refresh_mod_list()
        self.setup_drag_and_drop()  # <--- NEW!

    def create_mods_folder(self):
        if not os.path.exists(MODS_FOLDER):
            os.makedirs(MODS_FOLDER)

    def setup_ui(self):
        top = tk.Frame(self.parent)
        top.pack(fill="x", pady=4)
        tk.Button(top, text="Add Mod", command=self.add_mod).pack(side="left", padx=2)
        tk.Button(top, text="Remove Mod", command=self.remove_mod).pack(side="left", padx=2)
        tk.Button(top, text="Enable/Disable", command=self.toggle_mod).pack(side="left", padx=2)
        tk.Button(top, text="Open Mods Folder", command=self.open_mods_folder).pack(side="left", padx=2)

        self.mods_listbox = tk.Listbox(self.parent, height=12)
        self.mods_listbox.pack(fill="both", expand=True, padx=10, pady=6)
        self.mods_listbox.bind("<<ListboxSelect>>", self.show_mod_details)

        self.details_label = tk.Label(self.parent, text="Select a mod to view details.", anchor="w", justify="left")
        self.details_label.pack(fill="x", padx=10, pady=(0, 10))

    def refresh_mod_list(self):
        self.mods = []
        self.mods_listbox.delete(0, "end")
        try:
            for item in os.listdir(MODS_FOLDER):
                if item.endswith(".disabled"):
                    self.mods.append((item[:-9], False))
                else:
                    self.mods.append((item, True))
            for mod, enabled in self.mods:
                self.mods_listbox.insert("end", f"{mod} {'(ENABLED)' if enabled else '(DISABLED)'}")
        except Exception as e:
            messagebox.showerror("Mod Manager", f"Failed to read mods folder:\n{e}")

    def add_mod(self):
        path = filedialog.askopenfilename(title="Add Mod (select file/folder)")
        if not path:
            return
        try:
            dest = os.path.join(MODS_FOLDER, os.path.basename(path))
            if os.path.isdir(path):
                shutil.copytree(path, dest)
            else:
                shutil.copy2(path, dest)
            self.refresh_mod_list()
            messagebox.showinfo("Mod Added", "Mod added successfully.")
        except Exception as e:
            messagebox.showerror("Add Mod", f"Failed to add mod:\n{e}")

    def remove_mod(self):
        idx = self.mods_listbox.curselection()
        if not idx:
            messagebox.showwarning("Remove Mod", "No mod selected.")
            return
        mod, _ = self.mods[idx[0]]
        fullpath = os.path.join(MODS_FOLDER, mod)
        fullpath_disabled = fullpath + ".disabled"
        try:
            if os.path.isdir(fullpath):
                shutil.rmtree(fullpath)
            elif os.path.isdir(fullpath_disabled):
                shutil.rmtree(fullpath_disabled)
            elif os.path.exists(fullpath):
                os.remove(fullpath)
            elif os.path.exists(fullpath_disabled):
                os.remove(fullpath_disabled)
            self.refresh_mod_list()
            messagebox.showinfo("Removed", f"Removed: {mod}")
        except Exception as e:
            messagebox.showerror("Remove Mod", f"Failed to remove mod:\n{e}")

    def toggle_mod(self):
        idx = self.mods_listbox.curselection()
        if not idx:
            messagebox.showwarning("Toggle Mod", "No mod selected.")
            return
        mod, enabled = self.mods[idx[0]]
        fullpath = os.path.join(MODS_FOLDER, mod)
        fullpath_disabled = fullpath + ".disabled"
        try:
            if enabled:
                os.rename(fullpath, fullpath_disabled)
            else:
                os.rename(fullpath_disabled, fullpath)
            self.refresh_mod_list()
        except Exception as e:
            messagebox.showerror("Enable/Disable", f"Failed to toggle mod:\n{e}")

    def open_mods_folder(self):
        try:
            if os.name == "nt":
                os.startfile(os.path.abspath(MODS_FOLDER))
            else:
                import subprocess
                subprocess.Popen(["open", os.path.abspath(MODS_FOLDER)])
        except Exception as e:
            messagebox.showerror("Open Folder", f"Failed to open mods folder:\n{e}")

    def show_mod_details(self, event=None):
        idx = self.mods_listbox.curselection()
        if not idx:
            self.details_label.config(text="Select a mod to view details.")
            return
        mod, enabled = self.mods[idx[0]]
        fullpath = os.path.join(MODS_FOLDER, mod)
        info = f"Mod: {mod}\nStatus: {'ENABLED' if enabled else 'DISABLED'}\nPath: {fullpath}"
        try:
            if os.path.isdir(fullpath):
                size = self.get_dir_size(fullpath)
            elif os.path.isdir(fullpath + ".disabled"):
                size = self.get_dir_size(fullpath + ".disabled")
            elif os.path.exists(fullpath):
                size = os.path.getsize(fullpath)
            elif os.path.exists(fullpath + ".disabled"):
                size = os.path.getsize(fullpath + ".disabled")
            else:
                size = 0
            info += f"\nSize: {size} bytes"
        except:
            pass
        self.details_label.config(text=info)

    def get_dir_size(self, path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except Exception:
                    pass
        return total

    def setup_drag_and_drop(self):
        try:
            import tkinterdnd2 as tkdnd
            self.parent.drop_target_register(tkdnd.DND_FILES)
            self.parent.dnd_bind('<<Drop>>', self.on_drop)
        except ImportError:
            # If drag & drop isn't available, just leave it out.
            pass

    def on_drop(self, event):
        files = self.parent.tk.splitlist(event.data)
        for path in files:
            try:
                dest = os.path.join(MODS_FOLDER, os.path.basename(path))
                if os.path.isdir(path):
                    if os.path.exists(dest):
                        messagebox.showwarning("Already Exists", f"{os.path.basename(path)} already in mods.")
                        continue
                    shutil.copytree(path, dest)
                else:
                    shutil.copy2(path, dest)
            except Exception as e:
                messagebox.showerror("Drag & Drop", f"Failed to add mod:\n{e}")
        self.refresh_mod_list()
        messagebox.showinfo("Mod Added", "Mod(s) added successfully.")

ALLOWED_EXTS = {'.zip', '.png', '.jpg', '.jpeg', '.txt', '.ini', '.json'}

def add_mod(self):
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    if not is_safe_mod_file(file_path):
        messagebox.showerror("Error", f"File type not allowed: {file_path}")
        return