import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json

PRESETS_FOLDER = "presets"

class GamePresetsPanel:
    def __init__(self, parent):
        self.parent = parent
        self.presets = {}
        self.selected_preset = None
        self.setup_ui()
        self.load_all_presets()

    def setup_ui(self):
        top = ttk.LabelFrame(self.parent, text="Presets Manager", padding=10)
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(top, text="Game Name:").grid(row=0, column=0, sticky="e")
        self.game_entry = ttk.Entry(top, width=20)
        self.game_entry.grid(row=0, column=1, padx=2)
        tk.Label(top, text="Preset Name:").grid(row=0, column=2, sticky="e")
        self.preset_entry = ttk.Entry(top, width=20)
        self.preset_entry.grid(row=0, column=3, padx=2)
        ttk.Button(top, text="Save Current", command=self.save_current).grid(row=0, column=4, padx=4)
        ttk.Button(top, text="Load Preset", command=self.load_selected).grid(row=0, column=5, padx=4)
        ttk.Button(top, text="Delete Preset", command=self.delete_selected).grid(row=0, column=6, padx=4)
        ttk.Button(top, text="Export...", command=self.export_preset).grid(row=0, column=7, padx=4)
        ttk.Button(top, text="Import...", command=self.import_preset).grid(row=0, column=8, padx=4)

        self.preset_listbox = tk.Listbox(self.parent, height=10)
        self.preset_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.preset_listbox.bind("<<ListboxSelect>>", self.on_select)

        self.details_label = tk.Label(self.parent, text="Preset details will appear here.", anchor="w", justify="left")
        self.details_label.pack(fill="x", padx=10, pady=(0,10))

    def load_all_presets(self):
        self.presets = {}
        self.preset_listbox.delete(0, "end")
        if not os.path.exists(PRESETS_FOLDER):
            os.makedirs(PRESETS_FOLDER)
        for fname in os.listdir(PRESETS_FOLDER):
            if fname.endswith(".json"):
                with open(os.path.join(PRESETS_FOLDER, fname), "r") as f:
                    try:
                        data = json.load(f)
                        key = f"{data.get('game', 'Unknown')} / {data.get('preset', fname[:-5])}"
                        self.presets[key] = data
                        self.preset_listbox.insert("end", key)
                    except Exception:
                        continue

    def save_current(self):
        game = self.game_entry.get().strip()
        preset = self.preset_entry.get().strip()
        if not game or not preset:
            messagebox.showwarning("Missing Info", "Enter both game name and preset name.")
            return
        # Simulate: save fields (in real use, gather actual config/cheat/mod info)
        data = {
            "game": game,
            "preset": preset,
            "fields": {
                "example_setting": "value",
                "mod_list": ["mod1", "mod2"]
            }
        }
        fname = os.path.join(PRESETS_FOLDER, f"{game}_{preset}.json")
        try:
            with open(fname, "w") as f:
                json.dump(data, f, indent=4)
            self.load_all_presets()
            messagebox.showinfo("Preset Saved", f"Preset for {game} saved.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_selected(self):
        idx = self.preset_listbox.curselection()
        if not idx:
            messagebox.showwarning("No Preset", "Select a preset.")
            return
        key = self.preset_listbox.get(idx[0])
        data = self.presets.get(key)
        if not data:
            return
        # Simulate: Apply preset to game (real tool would update config or cheats)
        messagebox.showinfo("Preset Loaded", f"Loaded preset for {data.get('game')}.\nFields: {data.get('fields')}")

    def delete_selected(self):
        idx = self.preset_listbox.curselection()
        if not idx:
            messagebox.showwarning("No Preset", "Select a preset to delete.")
            return
        key = self.preset_listbox.get(idx[0])
        data = self.presets.get(key)
        if not data:
            return
        fname = os.path.join(PRESETS_FOLDER, f"{data.get('game')}_{data.get('preset')}.json")
        try:
            os.remove(fname)
            self.load_all_presets()
            messagebox.showinfo("Deleted", "Preset deleted.")
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    def on_select(self, event=None):
        idx = self.preset_listbox.curselection()
        if not idx:
            self.details_label.config(text="Preset details will appear here.")
            return
        key = self.preset_listbox.get(idx[0])
        data = self.presets.get(key, {})
        self.details_label.config(text=json.dumps(data, indent=2))

    def export_preset(self):
        idx = self.preset_listbox.curselection()
        if not idx:
            messagebox.showwarning("No Preset", "Select a preset to export.")
            return
        key = self.preset_listbox.get(idx[0])
        data = self.presets.get(key)
        if not data:
            return
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Exported", "Preset exported.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def import_preset(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            game = data.get("game", "Imported")
            preset = data.get("preset", "Preset")
            fname = os.path.join(PRESETS_FOLDER, f"{game}_{preset}.json")
            with open(fname, "w") as f2:
                json.dump(data, f2, indent=4)
            self.load_all_presets()
            messagebox.showinfo("Imported", "Preset imported.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
