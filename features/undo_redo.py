import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import copy
import os

class UndoRedoPanel:
    def __init__(self, parent):
        self.parent = parent
        self.save_file = None
        self.data = None
        self.undo_stack = []
        self.redo_stack = []
        self.setup_ui()

    def setup_ui(self):
        top = tk.Frame(self.parent)
        top.pack(anchor="nw", fill="x", pady=6, padx=8)
        tk.Button(top, text="Open Save File", command=self.open_save).pack(side="left")
        tk.Button(top, text="Undo", command=self.undo).pack(side="left", padx=2)
        tk.Button(top, text="Redo", command=self.redo).pack(side="left", padx=2)
        tk.Button(top, text="Save", command=self.save).pack(side="left", padx=2)
        self.path_label = tk.Label(top, text="No file loaded")
        self.path_label.pack(side="left", padx=10)

        # Simple field editor
        fields_frame = tk.LabelFrame(self.parent, text="Player Fields", padx=10, pady=5)
        fields_frame.pack(fill="x", padx=8, pady=4)
        self.entries = {}
        for i, field in enumerate(["health", "resources", "level"]):
            tk.Label(fields_frame, text=f"{field.capitalize()}:").grid(row=i, column=0, sticky="e")
            ent = tk.Entry(fields_frame, width=12)
            ent.grid(row=i, column=1, sticky="w")
            self.entries[field] = ent
            ent.bind("<KeyRelease>", lambda e, f=field: self.on_edit(f))
        self.update_fields_state("disabled")

    def update_fields_state(self, state):
        for ent in self.entries.values():
            ent.config(state=state)

    def open_save(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.save_file = path
            self.data = copy.deepcopy(data)
            self.undo_stack = [copy.deepcopy(data)]
            self.redo_stack = []
            self.path_label.config(text=path)
            self.load_fields()
            self.update_fields_state("normal")
        except Exception as e:
            messagebox.showerror("Open Save", f"Failed to open save:\n{e}")

    def load_fields(self):
        if not self.data or "player" not in self.data:
            return
        player = self.data["player"]
        for field, ent in self.entries.items():
            value = player.get(field, "")
            ent.delete(0, "end")
            ent.insert(0, str(value))

    def on_edit(self, field):
        if not self.data or "player" not in self.data:
            return
        try:
            for f, ent in self.entries.items():
                self.data["player"][f] = type(self.undo_stack[0]["player"][f])(ent.get()) if ent.get() else 0
            self.undo_stack.append(copy.deepcopy(self.data))
            self.redo_stack.clear()
        except Exception:
            pass  # Ignore type errors for now

    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.data = copy.deepcopy(self.undo_stack[-1])
            self.load_fields()
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.redo_stack.pop()))
            self.data = copy.deepcopy(self.undo_stack[-1])
            self.load_fields()
        else:
            messagebox.showinfo("Redo", "Nothing to redo.")

    def save(self):
        if not self.save_file:
            messagebox.showwarning("No File", "No save file loaded.")
            return
        try:
            with open(self.save_file, "w") as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Saved", f"Save file written:\n{self.save_file}")
        except Exception as e:
            messagebox.showerror("Save", f"Failed to save:\n{e}")
