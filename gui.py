import ttkbootstrap as ttk
import tkinter as tk
import os
import importlib.util
import json
import getpass
import sys
import webbrowser
import ctypes
import xml.etree.ElementTree as ET
import platform
import psutil
import threading
import zipfile
import re
import shutil
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
from ttkbootstrap.dialogs import Messagebox
from PIL import Image, ImageTk
from itertools import cycle
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD

from features.game_control import (
    snapshot_state, recover_state, scan_memory, edit_memory, replace_assets,
    check_file_integrity, inject_resources, decrypt_save, encrypt_save,
    simulate_corruption, toggle_trainer_option, launch_game_with_tool, import_mod
)
from features.intelligence import (
    auto_backup, save_cheat_profile, load_cheat_profile, tweak_game_config, run_custom_script, watch_memory_addresses
)
from features.system_integration import (
    detect_steam_path, list_steam_games, optimize_performance,
    enable_clipboard_sync, toggle_overlay_mode, enable_discord_presence
)
from features.cheat_table_importer import import_cheat_table, load_cheat_table, save_cheat_table

from process_tools import detect_game_process
from file_tools import load_save_file, save_modified_file, backup_file
from utils import log_to_file

from features.hex_editor import HexEditorPanel
from features.mod_manager import ModManagerPanel
from features.scheduled_actions import ScheduledActionsPanel
from features.performance_meter import PerformanceMeterPanel
from features.undo_redo import UndoRedoPanel
from features.dev_menu import DevMenuPanel
from features.game_presets import GamePresetsPanel
from features.resource_previewer import ResourcePreviewerPanel
from file_tools import safe_extract_zip

def import_app_config():
    import_path = filedialog.askopenfilename(filetypes=[("Zip Files", "*.zip")])
    if not import_path:
        return
    try:
        safe_extract_zip(import_path, ".")  # Use import_path here, after defining it!
        Messagebox.show_info("Import Complete", "App configuration imported. Please restart BreakBox.")
    except Exception as e:
        Messagebox.show_error("Import Error", str(e))

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def check_github_updates():
    url = "https://github.com/TentandTableStudios/BreakBox-Game-Toolkit"
    try:
        if platform.system() == "Windows":
            os.startfile(url)
        else:
            webbrowser.open(url)
    except Exception as e:
        Messagebox.show_error(f"Failed to open browser: {e}", title="Error")

def launch_gui():
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            theme = settings.get("theme", "superhero")
    except:
        theme = "superhero"

    root = TkinterDnD.Tk()
    from ttkbootstrap.style import Style
    style = Style(theme=theme)
    style.master = root
    root.title("BreakBox Game Toolkit (Alpha V1.0.1)")
    root.geometry("1280x820")
    root.minsize(1100, 700)
    root.configure(bg="#1c2330")
    status_var = tk.StringVar(value="Ready.")

    # --- Top Brand Bar ---
    top_bar = ttk.Frame(root, padding=(0, 16, 0, 16), style="primary.TFrame")
    top_bar.pack(side="top", fill="x")
    try:
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((72, 60), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(logo_img)
        logo_lbl = ttk.Label(top_bar, image=logo)
        logo_lbl.image = logo
        logo_lbl.pack(side="left", padx=(40, 16))
    except Exception:
        logo_lbl = ttk.Label(top_bar, text="🧰", font=("Segoe UI Emoji", 34))
        logo_lbl.pack(side="left", padx=(40, 16))
    title_lbl = ttk.Label(
        top_bar,
        text="BreakBox Game Toolkit",
        font=("Segoe UI", 32, "bold"),
        bootstyle="inverse-primary"
    )
    title_lbl.pack(side="left", padx=12)
    ver_lbl = ttk.Label(top_bar, text="ALPHA v1.0.1", font=("Segoe UI", 13, "bold"), bootstyle="info")
    ver_lbl.pack(side="left", padx=(14, 0))

    rainbow_colors = cycle([
        "#5DB3FF", "#4386FF", "#2a5fff", "#1272db",
        "#1482e6", "#47ccfd", "#59a6f4"
    ])
    update_label = tk.Label(
        master=top_bar,
        text="Check for Updates on GitHub",
        font=("Segoe UI", 12, "underline"),
        fg="#5DB3FF",
        bg=root.cget("background"),
        cursor="hand2"
    )
    update_label.pack(side="right", padx=36)
    update_label.bind("<Button-1>", lambda e: check_github_updates())
    def animate_label_color():
        color = next(rainbow_colors)
        update_label.configure(fg=color)
        root.after(140, animate_label_color)
    animate_label_color()

    notebook = ttk.Notebook(root, bootstyle="info")
    notebook.pack(fill='both', expand=True, padx=22, pady=20, ipadx=10, ipady=10)

    # --- Helper to Make a Section Card ---
    def section_card(tab, title, icon=None):
        frame = ttk.Frame(tab, padding=32, style="card.TFrame")
        frame.pack(fill="x", padx=44, pady=18)
        label = ttk.Label(
            frame,
            text=(f"{icon} {title}" if icon else title),
            font=("Segoe UI", 22, "bold"),
            bootstyle="inverse-secondary"
        )
        label.pack(anchor="w", pady=(0,16))
        return frame

    # ----- Game Detection Tab -----
    tab_game = ttk.Frame(notebook)
    notebook.add(tab_game, text='🎯 Game Detection')
    detect_card = section_card(tab_game, "Detect Game Process", icon="🔍")
    detect_frame = ttk.Frame(detect_card)
    detect_frame.pack(expand=True, fill="x")
    ttk.Label(detect_frame, text="Game Process Name:", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=14, pady=12, sticky="e")
    entry_game = ttk.Entry(detect_frame, width=50, bootstyle="dark")
    entry_game.grid(row=0, column=1, padx=14, pady=12)

    def detect():
        game = entry_game.get()
        try:
            pids = detect_game_process(game)
            if pids:
                Messagebox.show_info(title="Game Found", message=f"{game} running. PID(s): {pids}")
                log_to_file(f"Detected {game} at {pids}")
                status_var.set(f"Game found: {game} (PID {pids})")
            else:
                Messagebox.show_warning(title="Not Found", message=f"No process found for {game}")
                status_var.set(f"No game found for: {game}")
        except Exception as e:
            status_var.set(f"Error detecting game: {str(e)}")
    ttk.Button(detect_frame, text="Detect Game", bootstyle="info-outline", width=24, command=detect).grid(row=0, column=2, padx=14)

    # ----- Save Editor Tab -----
    tab_save = ttk.Frame(notebook)
    notebook.add(tab_save, text='📂 Save Editor')
    save_card = section_card(tab_save, "Save File Editor", icon="💾")
    save_frame = ttk.Frame(save_card)
    save_frame.pack(expand=True, fill="x")
    labels = ["Health", "Resources", "Level"]
    entries = {}
    for i, label in enumerate(labels):
        ttk.Label(save_frame, text=f"{label}:", font=("Segoe UI", 12, "bold")).grid(row=i, column=0, padx=12, pady=7, sticky="e")
        ent = ttk.Entry(save_frame, bootstyle="dark", font=("Segoe UI", 12), width=30)
        ent.grid(row=i, column=1, padx=10, pady=7)
        entries[label.lower()] = ent

    def reset_file():
        file = ttk.filedialog.askopenfilename(filetypes=[["JSON Files", "*.json"]])
        template = "template_save.json"
        if file:
            try:
                reset_save_file(file, template)
                Messagebox.show_info("Reset", "Save file has been reset.")
                status_var.set("Save file reset.")
            except Exception as e:
                Messagebox.show_error("Error", str(e))
                status_var.set(f"Error resetting save: {str(e)}")
    ttk.Button(save_frame, text="Reset Save File", command=reset_file, bootstyle="danger-outline", width=26).grid(row=4, column=1, pady=6)

    def modify():
        file = ttk.filedialog.askopenfilename(filetypes=[["JSON Files", "*.json"]])
        if file:
            try:
                backup_file(file)
                data = load_save_file(file)
                data['player']['health'] = int(entries['health'].get())
                data['player']['resources'] = int(entries['resources'].get())
                data['player']['level'] = int(entries['level'].get())
                save_modified_file(file, data)
                Messagebox.show_info("Saved", "Changes saved.")
                status_var.set("Save file modified successfully.")
            except Exception as e:
                Messagebox.show_error("Error", str(e))
                status_var.set(f"Error saving file: {str(e)}")
    ttk.Button(save_frame, text="Save Changes", bootstyle="success-outline", width=26, command=modify).grid(row=3, column=1, pady=12)

    UndoRedoPanel(save_card)
    HexEditorPanel(save_card)

    # --- System/Performance Tab ---
    tab_system = ttk.Frame(notebook)
    notebook.add(tab_system, text='📊 System/Performance')
    perf_card = section_card(tab_system, "Performance Meter", icon="🚦")
    PerformanceMeterPanel(perf_card)

    # --- Advanced Tools Tab ---
    tab_tools = ttk.Frame(notebook)
    notebook.add(tab_tools, text='🛠 Advanced Tools')
    advanced_card = section_card(tab_tools, "Advanced Tools", icon="🔧")
    canvas = tk.Canvas(advanced_card, bg="#1c2330", highlightthickness=0)
    scrollbar = ttk.Scrollbar(advanced_card, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)
    def create_dropdown_section(parent, title, tools):
        frame = ttk.Labelframe(parent, text=title, padding=12)
        frame.pack(fill="x", padx=26, pady=12)
        inner = ttk.Frame(frame)
        inner.pack(anchor="center")
        for text, func in tools.items():
            btn = ttk.Button(inner, text=text, command=lambda f=func: try_execute(f),
                             bootstyle="secondary-outline", width=32, padding=(4, 10))
            btn.pack(pady=7)
            btn.bind("<Enter>", lambda e, t=text: status_var.set(f"Hovering: {t}"))
            btn.bind("<Leave>", lambda e: status_var.set(""))
    def try_execute(func):
        try:
            func()
            status_var.set(f"Executed: {func.__name__}")
        except Exception as e:
            status_var.set(f"Error: {str(e)}")
    center_wrap = ttk.Frame(scrollable_frame)
    center_wrap.pack(anchor="center", pady=10)
    create_dropdown_section(center_wrap, "Memory Tools", {
        "Snapshot State": snapshot_state,
        "Recover State": recover_state,
        "Memory Scan": scan_memory,
        "Edit Memory": edit_memory,
        "Toggle Trainer Mode": lambda: toggle_trainer_option("god_mode"),
        "Watch Memory Addresses": watch_memory_addresses
    })
    create_dropdown_section(center_wrap, "File Tools", {
        "Replace Assets": replace_assets,
        "Check File Integrity": check_file_integrity,
        "Decrypt Save": decrypt_save,
        "Encrypt Save": encrypt_save,
        "Simulate Corruption": simulate_corruption,
        "Import Game Mod": lambda: import_mod("mod.zip"),
        "Import Cheat Table (.CT)": import_cheat_table
    })
    create_dropdown_section(center_wrap, "Game Tools", {
        "Inject Resources": inject_resources,
        "Launch Game with Tool": launch_game_with_tool,
        "Auto Backup": auto_backup,
        "Save Profile": save_cheat_profile,
        "Load Profile": load_cheat_profile,
        "Tweak Config": tweak_game_config,
        "Run Script": lambda: run_custom_script("print('Hello World')")
    })
    create_dropdown_section(center_wrap, "System Integration", {
        "Steam Path": detect_steam_path,
        "Steam Games": list_steam_games,
        "Optimize Performance": optimize_performance,
        "Clipboard Sync": enable_clipboard_sync,
        "Overlay Mode": toggle_overlay_mode,
        "Discord Presence": enable_discord_presence
    })

    # ----- Cheat Table Tab -----
    tab_cheat = ttk.Frame(notebook)
    notebook.add(tab_cheat, text='🧠 Cheat Tables')
    cheat_frame = section_card(tab_cheat, "Cheat Table Management", icon="🧩")
    cheat_path_var = tk.StringVar()
    search_var = tk.StringVar()
    selected_process = tk.StringVar()
    cheat_entries = []
    filtered_entries = []

    def get_user_processes():
        forbidden_names = {
            "wininit.exe", "lsass.exe", "csrss.exe", "svchost.exe",
            "winlogon.exe", "services.exe", "system", "idle", "explorer.exe"
        }
        procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                if (
                    name not in forbidden_names and
                    not name.startswith("system") and
                    not name.startswith("idle") and
                    proc.info['pid'] > 3
                ):
                    procs.append(f"{proc.info['name']} (PID {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sorted(procs)
    
    show_advanced = tk.BooleanVar(value=False)

    def update_process_list():
        if show_advanced.get():
            # Loosest possible filter, just skip pid 0/idle/system
            procs = [f"{p.info['name']} (PID {p.info['pid']})"
                for p in psutil.process_iter(['pid', 'name'])
                if p.info['pid'] > 3]
        else:
            procs = get_user_processes()
        process_dropdown["values"] = procs

    ttk.Checkbutton(root, text="Show Advanced (all processes)", variable=show_advanced,
                    command=update_process_list).pack()



    ttk.Label(cheat_frame, text="Target Process:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(12, 0))
    process_dropdown = ttk.Combobox(cheat_frame, textvariable=selected_process, bootstyle="info", font=("Segoe UI", 12), width=42)
    user_processes = get_user_processes()
    process_dropdown["values"] = user_processes if user_processes else ["No processes found"]
    process_dropdown.set(user_processes[0] if user_processes else "No processes found")
    process_dropdown.pack(pady=6, anchor="w")

    ttk.Label(cheat_frame, text="Selected Cheat Table:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8,0))
    ttk.Entry(cheat_frame, textvariable=cheat_path_var, width=92, bootstyle="dark", font=("Segoe UI", 11)).pack(pady=6, anchor="w")
    ttk.Button(cheat_frame, text="Browse .CT File", command=lambda: browse_ct(), bootstyle="secondary", width=28).pack(pady=6, anchor="w")

    ttk.Label(cheat_frame, text="Search Cheats:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8,0))
    ttk.Entry(cheat_frame, textvariable=search_var, width=40, bootstyle="info", font=("Segoe UI", 11)).pack(pady=5)

    cheat_listbox = tk.Listbox(
    cheat_frame,
    height=12,
    font=("Consolas", 9),
    bg="#1e1e1e",
    fg="#00ff00"
    )
    cheat_listbox.pack(fill="both", expand=True, pady=12, padx=2)

    btn_frame = ttk.Frame(cheat_frame)
    btn_frame.pack(pady=8)
    ttk.Button(btn_frame, text="Apply Selected", command=lambda: apply_selected_cheat(), bootstyle="success", width=22, padding=8).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Export to JSON", command=lambda: export_json(), bootstyle="secondary", width=22, padding=8).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Launch in Cheat Engine", command=lambda: launch_ct(), bootstyle="danger", width=22, padding=8).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Test Cheat", command=lambda: test_selected_cheat(), bootstyle="info", width=18, padding=8).pack(side="left", padx=5)

    def browse_ct():
        path = filedialog.askopenfilename(filetypes=[("Cheat Tables", "*.ct")])
        if path:
            cheat_path_var.set(path)
            refresh_cheat_entries(path)

    def refresh_cheat_entries(path):
        cheat_entries.clear()
        filtered_entries.clear()
        loaded = load_cheat_table(path)
        cheat_entries.extend(loaded)
        filtered_entries.extend(loaded)
        search_var.set("")
        update_listbox()
        if any("pointer" in str(cheat).lower() or "mono" in str(cheat).lower() or "il2cpp" in str(cheat).lower() for cheat in loaded):
            Messagebox.show_warning("Unsupported Cheat", "Pointer/Mono/IL2CPP cheats may not be fully supported yet.")

    def update_listbox():
        cheat_listbox.delete(0, "end")
        for cheat in filtered_entries:
            display = f"{cheat['description']} | {cheat['address']} | {cheat['type']} | {cheat['value']}"
            cheat_listbox.insert("end", display)

    def filter_cheats(*args):
        term = search_var.get().lower()
        filtered_entries.clear()
        filtered_entries.extend([c for c in cheat_entries if term in c['description'].lower()])
        update_listbox()
    search_var.trace_add("write", filter_cheats)

    def launch_ct():
        if not cheat_path_var.get():
            Messagebox.show_error("No File", "No .CT file loaded.")
            return
        try:
            launch_cheat_engine(cheat_path_var.get())
            Messagebox.show_info("Launched", "Cheat Engine launched with the loaded .CT file.")
        except Exception as e:
            Messagebox.show_error("Error", str(e))

    def export_json():
        if not cheat_entries:
            Messagebox.show_warning("No Data", "No cheat table loaded.")
            return
        path = "exported_cheats.json"
        with open(path, "w") as f:
            json.dump(cheat_entries, f, indent=4)
        Messagebox.show_info("Exported", f"Cheats exported to {path}")

    def apply_selected_cheat():
        selection = cheat_listbox.curselection()
        if not selection:
            Messagebox.show_warning("No Selection", "Select a cheat first.")
            return
        idx = selection[0]
        cheat = filtered_entries[idx]
        address = cheat['address']
        value = cheat['value']
        vartype = cheat.get('type', '4 Bytes')
        target_proc = selected_process.get()
        if not target_proc or "No processes found" in target_proc:
            Messagebox.show_error("No Target", "No process selected.")
            return
        try:
            edit_memory(target_proc, address, value, vartype)
            Messagebox.show_info("Cheat Applied", f"{cheat['description']} applied to {target_proc}")
        except Exception as e:
            Messagebox.show_error("Apply Failed", str(e))

    def test_selected_cheat():
        selection = cheat_listbox.curselection()
        if not selection:
            Messagebox.show_warning("No Selection", "Select a cheat first.")
            return
        idx = selection[0]
        cheat = filtered_entries[idx]
        address = cheat['address']
        value = cheat['value']
        vartype = cheat.get('type', '4 Bytes')
        target_proc = selected_process.get()
        if not target_proc or "No processes found" in target_proc:
            Messagebox.show_error("No Target", "No process selected.")
            return
        try:
            edit_memory(target_proc, address, value, vartype)
            Messagebox.show_info("Test Passed", f"Cheat {cheat['description']} can be applied to {target_proc}.")
        except Exception as e:
            Messagebox.show_error("Test Failed", f"Cheat failed: {str(e)}\nThis may be an unsupported pointer/mono/il2cpp cheat.")

    # ----- Cheat Table Editor Tab -----
    tab_cteditor = ttk.Frame(notebook)
    notebook.add(tab_cteditor, text="✏️ Cheat Table Editor")
    ctedit_card = section_card(tab_cteditor, "Cheat Table Editor", icon="📝")
    ctedit_path_var = tk.StringVar()
    ctedit_cheats = []
    ctedit_selected = tk.IntVar(value=-1)
    ctedit_top = ttk.Frame(ctedit_card)
    ctedit_top.pack(fill="x")
    def ctedit_load():
        path = filedialog.askopenfilename(filetypes=[("Cheat Tables", "*.ct")])
        if not path:
            return
        ctedit_path_var.set(path)
        cheats = load_cheat_table(path)
        ctedit_cheats.clear()
        ctedit_cheats.extend(cheats)
        ctedit_update_listbox()
        status_var.set("Loaded cheat table.")
    def ctedit_save():
        if not ctedit_path_var.get():
            Messagebox.show_error("No File", "No .CT file loaded.")
            return
        try:
            save_cheat_table(ctedit_path_var.get(), ctedit_cheats)
            status_var.set("Saved cheat table.")
            Messagebox.show_info("Saved", "Cheat Table saved successfully.")
        except Exception as e:
            Messagebox.show_error("Error", f"Failed to save CT: {e}")
    ttk.Entry(ctedit_top, textvariable=ctedit_path_var, width=68, bootstyle="dark", font=("Segoe UI", 11)).pack(side="left", padx=4)
    ttk.Button(ctedit_top, text="Browse", command=ctedit_load, bootstyle="info-outline", width=14).pack(side="left", padx=2)
    ttk.Button(ctedit_top, text="Save", command=ctedit_save, bootstyle="success-outline", width=14).pack(side="left", padx=2)
    ctedit_listbox = tk.Listbox(ctedit_card, height=14, font=("Consolas", 12), bg="#1f283b", fg="#5db3ff", borderwidth=2, relief="flat")
    ctedit_listbox.pack(fill="both", expand=True, padx=10, pady=(10,0))
    ctedit_listbox.bind("<<ListboxSelect>>", lambda e: ctedit_on_select())
    edit_frame = ttk.Frame(ctedit_card)
    edit_frame.pack(fill="x", pady=4, padx=12)
    fields = ["description", "address", "type", "value"]
    edit_vars = {f: tk.StringVar() for f in fields}
    for i, f in enumerate(fields):
        ttk.Label(edit_frame, text=f.capitalize()+":", width=12, font=("Segoe UI", 11, "bold")).grid(row=i, column=0, sticky="e", pady=2)
        ttk.Entry(edit_frame, textvariable=edit_vars[f], width=55, font=("Segoe UI", 11)).grid(row=i, column=1, sticky="w", pady=2)
    def ctedit_update_listbox():
        ctedit_listbox.delete(0, "end")
        for idx, c in enumerate(ctedit_cheats):
            ctedit_listbox.insert("end", f"{idx+1}. {c.get('description','')[:36]} | {c.get('address','')} | {c.get('type','')} | {c.get('value','')}")
    def ctedit_on_select():
        sel = ctedit_listbox.curselection()
        if not sel:
            for v in edit_vars.values():
                v.set("")
            ctedit_selected.set(-1)
            return
        idx = sel[0]
        cheat = ctedit_cheats[idx]
        for f in fields:
            edit_vars[f].set(str(cheat.get(f,"")))
        ctedit_selected.set(idx)
    def ctedit_apply():
        idx = ctedit_selected.get()
        if idx < 0 or idx >= len(ctedit_cheats):
            Messagebox.show_warning("No Selection", "Select a cheat to edit.")
            return
        for f in fields:
            ctedit_cheats[idx][f] = edit_vars[f].get()
        ctedit_update_listbox()
        status_var.set("Cheat edited.")
    def ctedit_add():
        cheat = {f:edit_vars[f].get() for f in fields}
        ctedit_cheats.append(cheat)
        ctedit_update_listbox()
        status_var.set("Cheat added.")
    def ctedit_remove():
        idx = ctedit_selected.get()
        if idx < 0 or idx >= len(ctedit_cheats):
            Messagebox.show_warning("No Selection", "Select a cheat to remove.")
            return
        del ctedit_cheats[idx]
        ctedit_update_listbox()
        for v in edit_vars.values():
            v.set("")
        ctedit_selected.set(-1)
        status_var.set("Cheat removed.")
    btns = ttk.Frame(ctedit_card)
    btns.pack(fill="x", pady=(8,6))
    ttk.Button(btns, text="Apply Edit", command=ctedit_apply, bootstyle="primary", width=16).pack(side="left", padx=2)
    ttk.Button(btns, text="Add New Cheat", command=ctedit_add, bootstyle="success", width=18).pack(side="left", padx=2)
    ttk.Button(btns, text="Remove Cheat", command=ctedit_remove, bootstyle="danger", width=16).pack(side="left", padx=2)

    # ----- Modding Tools Tab -----
    tab_modding = ttk.Frame(notebook)
    notebook.add(tab_modding, text='🛠 Modding Tools')
    ModManagerPanel(tab_modding)
    ScheduledActionsPanel(tab_modding)
    GamePresetsPanel(tab_modding)

    # --- Developer Tab ---
    tab_dev = ttk.Frame(notebook)
    notebook.add(tab_dev, text='👾 Dev Menu')
    DevMenuPanel(tab_dev)

    # ----- Settings Tab -----
    tab_settings = ttk.Frame(notebook)
    notebook.add(tab_settings, text='⚙️ Settings')
    settings_card = section_card(tab_settings, "Application Settings", icon="🛠️")
    ttk.Label(settings_card, text="Theme Changer", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=8)
    theme_choice = ttk.Combobox(settings_card, values=["superhero", "vapor", "darkly", "litera"], font=("Segoe UI", 12))
    theme_choice.set(theme)
    theme_choice.pack(anchor="w", padx=6, pady=10)
    def apply_theme():
        selected = theme_choice.get()
        with open("settings.json", "w") as f:
            json.dump({"theme": selected}, f)
        root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)
    ttk.Button(settings_card, text="Apply Theme", command=apply_theme, bootstyle="primary-outline", width=18).pack(anchor="w", pady=14)
    def export_app_config():
        export_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip Files", "*.zip")])
        if not export_path:
            return
        try:
            with zipfile.ZipFile(export_path, "w") as zf:
                for fname in ["settings.json", "profile.json"]:
                    if os.path.exists(fname):
                        zf.write(fname)
                if os.path.exists("mods"):
                    for rootdir, dirs, files in os.walk("mods"):
                        for file in files:
                            full_path = os.path.join(rootdir, file)
                            rel_path = os.path.relpath(full_path, ".")
                            zf.write(full_path, arcname=rel_path)
            Messagebox.show_info("Export Complete", f"Config exported to {export_path}")
        except Exception as e:
            Messagebox.show_error("Export Error", str(e))
    def import_app_config():
        import_path = filedialog.askopenfilename(filetypes=[("Zip Files", "*.zip")])
        if not import_path:
            return
        try:
            with zipfile.ZipFile(import_path, "r") as zf:
                zf.extractall(".")
            Messagebox.show_info("Import Complete", "App configuration imported. Please restart BreakBox.")
        except Exception as e:
            Messagebox.show_error("Import Error", str(e))
    def reset_app_config():
        try:
            for fname in ["settings.json", "profile.json"]:
                if os.path.exists(fname):
                    os.remove(fname)
            if os.path.exists("mods"):
                shutil.rmtree("mods")
            os.makedirs("mods", exist_ok=True)
            Messagebox.show_info("Reset Complete", "Settings and mods have been reset. Please restart BreakBox.")
        except Exception as e:
            Messagebox.show_error("Reset Error", str(e))
    backup_frame = ttk.Frame(settings_card)
    backup_frame.pack(fill="x", pady=18)
    ttk.Label(backup_frame, text="Backup & Restore", font=("Segoe UI", 14, "bold")).pack(anchor="w")
    ttk.Button(backup_frame, text="Export App Config", command=export_app_config, bootstyle="info", width=20).pack(side="left", padx=2)
    ttk.Button(backup_frame, text="Import App Config", command=import_app_config, bootstyle="secondary", width=20).pack(side="left", padx=2)
    ttk.Button(backup_frame, text="Reset All", command=reset_app_config, bootstyle="danger", width=20).pack(side="left", padx=2)
    ttk.Label(settings_card, text="Log Verbosity", font=("Segoe UI", 12)).pack(anchor="w", pady=(12,0))
    verbosity = tk.StringVar(value="Normal")
    ttk.Combobox(settings_card, textvariable=verbosity, values=["Low", "Normal", "High"], font=("Segoe UI", 11)).pack(anchor="w", padx=6)
    auto_update_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(settings_card, text="Auto check for updates", variable=auto_update_var, bootstyle="success").pack(anchor="w", pady=(10,0))
    ttk.Label(settings_card, text="Default Game Path (placeholder)", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=12)
    ttk.Entry(settings_card, bootstyle="dark", font=("Segoe UI", 11)).pack(anchor="w", pady=7)
    ttk.Label(settings_card, text="(Not yet implemented)", font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=4)

    # ----- Logs Tab -----
    tab_logs = ttk.Frame(notebook)
    notebook.add(tab_logs, text='📜 Logs')
    logs_card = section_card(tab_logs, "Log Viewer", icon="📖")
    controls_frame = ttk.Frame(logs_card)
    controls_frame.pack(fill='x', padx=4, pady=4)
    filter_var = tk.StringVar(value="All")
    search_var = tk.StringVar()
    log_box = tk.Text(logs_card, bg="#1f283b", fg="#5db3ff", insertbackground="#5db3ff",
                    font=("Consolas", 12), height=18, wrap="none", borderwidth=2, relief="flat")
    log_box.pack(fill='both', expand=True, padx=8, pady=6)
    def load_log():
        if not os.path.exists("modding_tool.log"):
            return []
        with open("modding_tool.log", "r") as f:
            return f.readlines()
    def filter_log_lines(lines, level, keyword):
        out = []
        for line in lines:
            if level != "All":
                if not re.search(rf"\[{level.upper()}\]", line):
                    continue
            if keyword and keyword.lower() not in line.lower():
                continue
            out.append(line)
        return out
    def update_log_display(*_):
        log_box.delete('1.0', 'end')
        lines = load_log()
        filtered = filter_log_lines(
            lines, filter_var.get(), search_var.get())
        for line in filtered:
            log_box.insert("end", line)
    filter_label = ttk.Label(controls_frame, text="Filter:", font=("Segoe UI", 11, "bold"))
    filter_label.pack(side="left", padx=(0, 4))
    filter_menu = ttk.Combobox(controls_frame, textvariable=filter_var,
                            values=["All", "INFO", "WARNING", "ERROR"], width=9, state="readonly", font=("Segoe UI", 11))
    filter_menu.pack(side="left")
    filter_menu.bind("<<ComboboxSelected>>", update_log_display)
    search_label = ttk.Label(controls_frame, text="Search:", font=("Segoe UI", 11, "bold"))
    search_label.pack(side="left", padx=(10, 4))
    search_entry = ttk.Entry(controls_frame, textvariable=search_var, width=22, font=("Segoe UI", 11))
    search_entry.pack(side="left")
    search_var.trace_add("write", lambda *_: update_log_display())
    def copy_log():
        log = log_box.get("1.0", "end").strip()
        if log:
            root.clipboard_clear()
            root.clipboard_append(log)
            Messagebox.show_info("Copied", "Log copied to clipboard.")
    def clear_log():
        log_box.delete('1.0', 'end')
        with open("modding_tool.log", "w") as f:
            f.write("")
    copy_btn = ttk.Button(controls_frame, text="Copy", command=copy_log, bootstyle="info-outline", width=14)
    copy_btn.pack(side="right", padx=(4, 0))
    clear_btn = ttk.Button(controls_frame, text="Clear Log", command=clear_log, bootstyle="danger-outline", width=14)
    clear_btn.pack(side="right", padx=2)
    update_log_display()

    # ----- Resource Previewer Tab -----
    tab_preview = ttk.Frame(notebook)
    notebook.add(tab_preview, text='🖼️ Resource Previewer')
    ResourcePreviewerPanel(tab_preview)

    # ----- About Tab -----
    tab_about = ttk.Frame(notebook)
    notebook.add(tab_about, text='ℹ️ About')
    about_card = section_card(tab_about, "About", icon="💡")
    about_text = (
        "🔹 BreakBox Game Toolkit\n"
        "Version: Alpha 1.0.1\n\n"
        "A modular, feature-rich game editing and analysis tool.\n"
        "Designed for educational, debugging, and offline single player game enhancement uses.\n\n"
        "Developed by: Tent and Table Studios\n"
        "Interface: ttkbootstrap + Tkinter\n"
        "Made with ❤️ and Python"
    )
    credits_text = (
        "🔹 Credits:\n"
        "- ttkbootstrap (GUI theming)\n"
        "- Pillow (image/logo handling)\n"
        "- Python 3.x\n"
        "- The Open Source community\n"
        "🔸 Special thanks to testers and contributors.\n"
    )
    verse_text = (
        "📖 Proverbs 18:15 (NIV)\n"
        "“The heart of the discerning acquires knowledge, for the ears of the wise seek it out.”"
    )
    about_lbl = ttk.Label(about_card, text=about_text, justify="left", font=("Segoe UI", 14))
    about_lbl.pack(anchor="w", pady=10)
    credits_lbl = ttk.Label(about_card, text=credits_text, justify="left", font=("Segoe UI", 12))
    credits_lbl.pack(anchor="w", pady=8)
    verse_lbl = ttk.Label(about_card, text=verse_text, justify="left", font=("Segoe UI", 11, "italic"))
    verse_lbl.pack(anchor="w", pady=8)

    # ----- Status Bar -----
    status_bar = ttk.Label(
        root, textvariable=status_var, anchor="w", relief="ridge",
        bootstyle="inverse-secondary", font=("Segoe UI", 13), padding=8
    )
    status_bar.pack(fill="x", side="bottom")
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
