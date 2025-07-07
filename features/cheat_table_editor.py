import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from ttkbootstrap import ttk
import json

def CheatTableEditorPanel(parent, load_cheat_table, save_cheat_table):
    frame = ttk.Frame(parent, padding=12)
    frame.pack(fill="both", expand=True)
    
    cheats = []
    current_path = tk.StringVar()

    top = ttk.Frame(frame)
    top.pack(fill="x", pady=4)
    ttk.Button(top, text="Open .CT", command=lambda: open_ct()).pack(side="left", padx=3)
    ttk.Button(top, text="Save .CT", command=lambda: save_ct()).pack(side="left", padx=3)
    ttk.Button(top, text="Export as JSON", command=lambda: export_json()).pack(side="left", padx=3)
    ttk.Button(top, text="Add Cheat", command=lambda: add_cheat()).pack(side="left", padx=3)
    ttk.Button(top, text="Delete Cheat", command=lambda: delete_cheat()).pack(side="left", padx=3)
    path_label = ttk.Label(top, textvariable=current_path)
    path_label.pack(side="left", padx=10)

    listbox = tk.Listbox(frame, height=12)
    listbox.pack(fill="both", expand=True, padx=5, pady=4)
    details_frame = ttk.Frame(frame)
    details_frame.pack(fill="x", pady=8)

    # Cheat editing entries
    fields = ["description", "address", "type", "value"]
    entries = {}
    for i, field in enumerate(fields):
        ttk.Label(details_frame, text=field.title()+":", width=14).grid(row=i, column=0, sticky="e")
        ent = ttk.Entry(details_frame, width=35)
        ent.grid(row=i, column=1, sticky="w")
        entries[field] = ent

    def update_list():
        listbox.delete(0, "end")
        for cheat in cheats:
            listbox.insert("end", f"{cheat['description']} | {cheat['address']} | {cheat['type']} | {cheat['value']}")

    def on_select(event=None):
        if not listbox.curselection():
            for field in fields:
                entries[field].delete(0, "end")
            return
        idx = listbox.curselection()[0]
        for field in fields:
            entries[field].delete(0, "end")
            entries[field].insert(0, cheats[idx].get(field, ""))

    def save_fields_to_cheat():
        if not listbox.curselection():
            return
        idx = listbox.curselection()[0]
        for field in fields:
            cheats[idx][field] = entries[field].get()
        update_list()

    def add_cheat():
        new_cheat = {field: "" for field in fields}
        cheats.append(new_cheat)
        update_list()
        listbox.select_set(len(cheats)-1)
        on_select()

    def delete_cheat():
        idx = listbox.curselection()
        if not idx:
            return
        idx = idx[0]
        if messagebox.askyesno("Delete", "Delete selected cheat?"):
            cheats.pop(idx)
            update_list()
            on_select()

    def open_ct():
        path = filedialog.askopenfilename(filetypes=[("Cheat Table", "*.ct")])
        if not path:
            return
        loaded = load_cheat_table(path)
        cheats.clear()
        cheats.extend(loaded)
        update_list()
        current_path.set(os.path.basename(path))
        listbox.select_clear(0, "end")
        on_select()

    def save_ct():
        if not cheats:
            messagebox.showwarning("Nothing to Save", "No cheats to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".ct", filetypes=[("Cheat Table", "*.ct")])
        if not path:
            return
        try:
            save_cheat_table(path, cheats)
            messagebox.showinfo("Saved", "Cheat table saved.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def export_json():
        if not cheats:
            messagebox.showwarning("Nothing to Export", "No cheats to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cheats, f, indent=4)
            messagebox.showinfo("Exported", "Cheats exported to JSON.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def on_entry_update(event=None):
        save_fields_to_cheat()

    for ent in entries.values():
        ent.bind("<FocusOut>", on_entry_update)

    listbox.bind("<<ListboxSelect>>", on_select)
    update_list()
    on_select()
