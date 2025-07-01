import ttkbootstrap as ttk
import tkinter as tk
import os
import importlib.util
import json
import sys
import webbrowser 
import subprocess
import platform
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
from ttkbootstrap.dialogs import Messagebox
from process_tools import detect_game_process
from file_tools import load_save_file, save_modified_file, backup_file
from utils import log_to_file
from features.intelligence import watch_memory_addresses
from PIL import Image, ImageTk 
from itertools import cycle
from features.game_control import (
    snapshot_state, recover_state, scan_memory, edit_memory, replace_assets,
    check_file_integrity, inject_resources, decrypt_save, encrypt_save,
    simulate_corruption, toggle_trainer_option, launch_game_with_tool, import_mod
)
from features.intelligence import (
    auto_backup, save_cheat_profile, load_cheat_profile, tweak_game_config, run_custom_script
)
from features.system_integration import (
    detect_steam_path, list_steam_games, optimize_performance,
    enable_clipboard_sync, toggle_overlay_mode, enable_discord_presence
)

#Image.open("assets/logo.png").save("assets/logo.ico", format="ICO", sizes=[(64, 64)])

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def check_github_updates():
    url = "https://github.com/TentandTableStudios/BreakBox-Game-Toolkit"
    try:
        if platform.system() == "Windows":
            subprocess.run(["cmd", "/c", "start", "", url], shell=True)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"Failed to open browser: {e}")

def launch_gui():
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            theme = settings.get("theme", "vapor")
    except:
        theme = "vapor"

    root = ttk.Window(themename=theme)

    rainbow_colors = cycle([
        "#FF0000", "#FF7F00", "#FFFF00", "#00FF00", 
        "#0000FF", "#4B0082", "#8F00FF"
    ])

    top_frame = ttk.Frame(root)
    top_frame.pack(fill="x", pady=(5, 0))

    update_label = tk.Label(
            master=root,
            text="Check for Updates on GitHub",
            font=("Segoe UI", 12, "underline"),
            fg="blue",
            bg=root.cget("background"),
            cursor="hand2"
    )
    update_label.pack(side="top", padx=10)
    update_label.bind("<Button-1>", lambda e: check_github_updates())

    def animate_label_color():
        color = next(rainbow_colors)
        update_label.configure(foreground=color)
        root.after(150, animate_label_color)


    animate_label_color()
    root.title("BreakBox Game Toolkit (Alpha V1.0.0)")
    root.geometry("1000x900")

    status_var = tk.StringVar()

    style = ttk.Style()
    style.configure("Bold.TButton", font=("Segoe UI", 10, "bold"))
    style.configure("Bold.TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    try:
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((220, 182), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(logo_img)
        logo_frame = ttk.Frame(root)
        logo_frame.pack(pady=(10, 0))
        logo_label = ttk.Label(logo_frame, image=logo)
        logo_label.image = logo
        logo_label.pack()
    except Exception as e:
        print(f"Logo not loaded: {e}")

    notebook = ttk.Notebook(root, bootstyle="info")
    notebook.pack(fill='both', expand=True, padx=10, pady=10) 

 
    tab_game = ttk.Frame(notebook)
    notebook.add(tab_game, text='🎯 Game Detection')
    detect_frame = ttk.Frame(tab_game)
    detect_frame.pack(expand=True)

    ttk.Label(detect_frame, text="Game Process Name:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_game = ttk.Entry(detect_frame, width=40, bootstyle="dark")
    entry_game.grid(row=0, column=1, padx=10, pady=10)

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

    ttk.Button(detect_frame, text="Detect Game", bootstyle="info-outline", command=detect, style="Bold.TButton").grid(row=0, column=2, padx=10)

    tab_save = ttk.Frame(notebook)
    notebook.add(tab_save, text='📂 Save Editor')

    save_frame = ttk.Frame(tab_save)
    save_frame.pack(expand=True)

    labels = ["Health", "Resources", "Level"]
    entries = {}
    for i, label in enumerate(labels):
        ttk.Label(save_frame, text=f"{label}:", font=("Segoe UI", 10, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        ent = ttk.Entry(save_frame, bootstyle="dark")
        ent.grid(row=i, column=1, padx=10, pady=5)
        entries[label.lower()] = ent

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

    ttk.Button(save_frame, text="Save Changes", bootstyle="success-outline", command=modify, style="Bold.TButton").grid(row=3, column=1, pady=10)

    tab_tools = ttk.Frame(notebook)
    notebook.add(tab_tools, text='🛠 Advanced Tools')

    canvas = tk.Canvas(tab_tools)
    scrollbar = ttk.Scrollbar(tab_tools, orient="vertical", command=canvas.yview)
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
        frame = ttk.Labelframe(parent, text=title, padding=10, style="Bold.TLabelframe")
        frame.pack(fill="x", padx=20, pady=10)
        inner = ttk.Frame(frame)
        inner.pack(anchor="center")
        for text, func in tools.items():
            btn = ttk.Button(inner, text=text, command=lambda f=func: try_execute(f), bootstyle="secondary-outline", width=30, style="Bold.TButton")
            btn.pack(pady=5)
            btn.bind("<Enter>", lambda e, t=text: status_var.set(f"Hovering: {t}"))
            btn.bind("<Leave>", lambda e: status_var.set(""))

    def try_execute(func):
        try:
            func()
            status_var.set(f"Executed: {func.__name__}")
        except Exception as e:
            status_var.set(f"Error: {str(e)}")

    center_wrap = ttk.Frame(scrollable_frame)
    center_wrap.pack(anchor="center")

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
        "Import Game Mod": lambda: import_mod("mod.zip")
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

    tab_settings = ttk.Frame(notebook)
    notebook.add(tab_settings, text='⚙️ Settings')

    ttk.Label(tab_settings, text="Theme Changer", font=("Segoe UI", 10, "bold")).pack(pady=5)
    theme_choice = ttk.Combobox(tab_settings, values=["vapor", "darkly", "litera", "superhero"])
    theme_choice.set(theme)
    theme_choice.pack()

    def apply_theme():
        selected = theme_choice.get()
        with open("settings.json", "w") as f:
            json.dump({"theme": selected}, f)
        root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    ttk.Button(tab_settings, text="Apply Theme", command=apply_theme).pack(pady=10)

    ttk.Label(tab_settings, text="Default Game Path (placeholder)", font=("Segoe UI", 10, "bold")).pack(pady=10)
    ttk.Entry(tab_settings, bootstyle="dark").pack(pady=5)
    ttk.Label(tab_settings, text="(Not yet implemented)").pack(pady=2)

    tab_logs = ttk.Frame(notebook)
    notebook.add(tab_logs, text='📜 Logs')

    log_box = tk.Text(tab_logs, bg="#1e1e1e", fg="#00ff00", insertbackground="#00ff00", font=("Consolas", 10))
    log_box.pack(fill='both', expand=True)
    try:
        with open("modding_tool.log", "r") as f:
            log_box.insert("end", f.read())
    except:
        log_box.insert("end", ">> Log file missing.\n")

    status_bar = ttk.Label(root, textvariable=status_var, anchor="w", relief="sunken")
    status_bar.pack(fill="x", side="bottom")

    tab_about = ttk.Frame(notebook)
    notebook.add(tab_about, text='ℹ️ About')

    about_text = (
        "🔹 BreakBox Game Toolkit\n"
        "Version: Alpha 1.0.0\n"
        "\n"
        "A modular, feature-rich game editing and analysis tool.\n"
        "Designed for educational, debugging, and offline single player game enhancement uses.\n"
        "\n"
        "Developed by: Tent and Table Studios\n"
        "Interface: ttkbootstrap + Tkinter\n"
        "Made with ❤️and Python"
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
        "📖 Proverbs 18:15 (NIV) “The heart of the discerning acquires knowledge, for the ears of the wise seek it out.”\n"
    )

    

    frame_about = ttk.Frame(tab_about)
    frame_about.pack(fill='both', expand=True, padx=20, pady=20)

    about_label = ttk.Label(frame_about, text=about_text, justify="left", font=("Segoe UI", 10))
    about_label.pack(anchor="w", pady=10)

    credits_label = ttk.Label(frame_about, text=credits_text, justify="left", font=("Segoe UI", 10))
    credits_label.pack(anchor="w")

    verse_label = ttk.Label(frame_about, text=verse_text, justify="left", font=("Segoe UI", 10))
    verse_label.pack(anchor="w")

    tools_frame = ttk.Frame(notebook)
    notebook.add(tools_frame, text="🧪 Updates")

    ttk.Label(tools_frame, text="Coming Soon Tools", font=("Segoe UI", 12, "bold")).pack(pady=10)
    ttk.Label(tools_frame, text="These features are currently in development.", font=("Segoe UI", 10, "bold")).pack(pady=5)

    ttk.Label(tools_frame, text="- Cheat Table Importer\n- Mod Manager Panel\n- Scheduled Actions\n- Performance Meter\n- Undo/Redo Save Editing\n- Hex Editor\n- Dev Menu\n- Game Presets", justify="left").pack(pady=5)


    
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
