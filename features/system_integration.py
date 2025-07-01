import os
import winreg
from tkinter import simpledialog, messagebox
import re
import json
from pathlib import Path
import psutil
import ctypes
import pyperclip
import tkinter as tk
from pypresence import Presence
import time
import threading

discord_client = None

def enable_discord_presence():
    global discord_client

    client_id = simpledialog.askstring("Discord Client ID", "Enter your Discord App Client ID:")
    if not client_id:
        return

    try:
        discord_client = Presence(client_id)
        discord_client.connect()

        start_time = int(time.time())

        def update_presence():
            try:
                discord_client.update(
                    state="Modding & Memory Tools Active",
                    details="Game Exploit Toolset",
                    start=start_time,
                    large_image="default",
                    large_text="BreakBox Tools"
                )
                log_to_file("Discord Rich Presence enabled.")
            except Exception as e:
                log_to_file(f"Discord Presence update failed: {e}")

        threading.Thread(target=update_presence, daemon=True).start()
        messagebox.showinfo("Discord", "Rich Presence connected.")
    except Exception as e:
        messagebox.showerror("Discord Error", str(e))

overlay_window = None

def toggle_overlay_mode():
    global overlay_window

    if overlay_window and overlay_window.winfo_exists():
        overlay_window.destroy()
        overlay_window = None
        log_to_file("Overlay mode disabled.")
        return

    
    overlay_window = tk.Toplevel()
    overlay_window.title("Overlay")
    overlay_window.geometry("300x100+100+100")
    overlay_window.attributes("-topmost", True)
    overlay_window.overrideredirect(True) 

    
    try:
        overlay_window.attributes("-alpha", 0.85)
    except Exception:
        pass

    label = tk.Label(overlay_window, text="Overlay Mode Active", font=("Segoe UI", 12), bg="black", fg="lime")
    label.pack(expand=True, fill="both")

    log_to_file("Overlay mode enabled.")

def enable_clipboard_sync():
    value = simpledialog.askstring("Clipboard Sync", "Enter value to copy to clipboard:")
    if not value:
        return

    try:
        pyperclip.copy(value)
        messagebox.showinfo("Copied", "Value copied to clipboard.")
        log_to_file(f"Clipboard synced: {value}")
    except Exception as e:
        messagebox.showerror("Clipboard Error", str(e))

def optimize_performance():
    try:
        game_name = simpledialog.askstring("Game Process", "Enter the game's process name (e.g., game.exe):")
        if not game_name:
            return

        
        target_proc = None
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == game_name.lower():
                target_proc = proc
                break

        if not target_proc:
            messagebox.showwarning("Not Found", f"Process '{game_name}' not found.")
            return

        
        target_proc.nice(psutil.HIGH_PRIORITY_CLASS)

        # Disable Windows Game DVR via registry (optional, may require admin)
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\GameBar", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 0)
        except Exception:
            pass  # Not critical

        messagebox.showinfo("Optimized", f"Performance tweaks applied to: {game_name}")
        log_to_file(f"Set high priority for: {game_name}")

    except Exception as e:
        messagebox.showerror("Optimization Failed", str(e))

def list_steam_games(steam_path=None):
    if not steam_path:
        from features.system_integration import detect_steam_path
        steam_path = detect_steam_path()
        if not steam_path:
            return []

    library_paths = [os.path.join(steam_path, "steamapps")]

    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if os.path.exists(vdf_path):
        try:
            with open(vdf_path, "r", encoding="utf-8") as f:
                text = f.read()

            folder_matches = re.findall(r'"\d+"\s+"([^"]+)"', text)
            for path in folder_matches:
                library_paths.append(os.path.join(path.replace("\\\\", "\\"), "steamapps"))
        except Exception:
            pass

    games = []

    for lib in library_paths:
        try:
            manifests = Path(lib).glob("appmanifest_*.acf")
            for manifest in manifests:
                with open(manifest, "r", encoding="utf-8") as f:
                    data = f.read()
                name_match = re.search(r'"name"\s+"([^"]+)"', data)
                if name_match:
                    games.append(name_match.group(1))
        except Exception:
            continue

    if games:
        messagebox.showinfo("Steam Games Found", f"Found {len(games)} games:\n" + "\n".join(games[:15]))
    else:
        messagebox.showwarning("No Games", "No installed Steam games could be detected.")

    return games

def detect_steam_path():
    steam_path = None

    try:
        # Try registry first
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path, _ = winreg.QueryValueEx(key, "SteamPath")

        if steam_path and os.path.exists(steam_path):
            messagebox.showinfo("Steam Path Detected", f"Steam installation found at:\n{steam_path}")
            return steam_path

    except Exception:
        pass

    common_paths = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam"
    ]

    for path in common_paths:
        if os.path.exists(path):
            messagebox.showinfo("Steam Path Found", f"Found Steam at default path:\n{path}")
            return path

    messagebox.showwarning("Steam Not Found", "Steam installation path could not be detected.")
    return None
