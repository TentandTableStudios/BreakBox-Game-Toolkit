import ctypes
import struct
import time
import threading
from tkinter import filedialog, simpledialog, messagebox
from utils import log_to_file
from process_tools import detect_game_process
import shutil
import datetime
import json
import traceback

def run_custom_script():
    script_path = filedialog.askopenfilename(
        title="Select Python Script",
        filetypes=[("Python Scripts", "*.py")]
    )
    if not script_path:
        return

    try:
        with open(script_path, "r") as f:
            script_code = f.read()

        exec(script_code, globals())
        log_to_file(f"Executed script: {script_path}")
        messagebox.showinfo("Success", f"Custom script executed:\n{script_path}")
    except Exception as e:
        error_msg = f"Script execution failed:\n{traceback.format_exc()}"
        messagebox.showerror("Execution Error", error_msg)
        log_to_file(error_msg)

def tweak_game_config():
    config_path = filedialog.askopenfilename(
        title="Select Game Config File",
        filetypes=[("Config Files", "*.json *.ini *.cfg"), ("All Files", "*.*")]
    )
    if not config_path:
        return

    try:
        key = simpledialog.askstring("Config Key", "Enter the key/setting name (e.g., fullscreen, max_fps):")
        if not key:
            return

        new_value = simpledialog.askstring("New Value", f"Enter the new value for '{key}':")
        if new_value is None:
            return

        if config_path.endswith(".json"):
            with open(config_path, "r") as f:
                config = json.load(f)

            config[key] = new_value

            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)

        else:  # INI or CFG
            with open(config_path, "r") as f:
                lines = f.readlines()

            key_found = False
            for i, line in enumerate(lines):
                if re.match(rf"^\s*{re.escape(key)}\s*=", line):
                    lines[i] = f"{key} = {new_value}\n"
                    key_found = True
                    break

            if not key_found:
                lines.append(f"{key} = {new_value}\n")

            with open(config_path, "w") as f:
                f.writelines(lines)

        log_to_file(f"Updated config: {key} = {new_value} in {config_path}")
        messagebox.showinfo("Success", f"Updated '{key}' in config file.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

trainer_states = {}

def load_cheat_profile():
    file_path = filedialog.askopenfilename(
        title="Load Cheat Profile",
        filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "r") as f:
            profile = json.load(f)

        trainer_states.update(profile)
        log_to_file(f"Loaded cheat profile from: {file_path}")
        messagebox.showinfo("Profile Loaded", f"Loaded cheat profile:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Load Error", str(e))


trainer_states = {
    "GodMode": True,
    "InfiniteAmmo": False,
    "NoClip": True,
    "SpeedHack": False
}

def save_cheat_profile():
    file_path = filedialog.asksaveasfilename(
        title="Save Cheat Profile",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "w") as f:
            json.dump(trainer_states, f, indent=4)
        log_to_file(f"Cheat profile saved to: {file_path}")
        messagebox.showinfo("Profile Saved", f"Cheat profile saved:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Save Error", str(e))


def auto_backup():
    target_file = filedialog.askopenfilename(title="Select Game File to Back Up")
    if not target_file:
        return

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = target_file + f".backup_{timestamp}"
        shutil.copy2(target_file, backup_path)

        log_to_file(f"Backup created: {backup_path}")
        messagebox.showinfo("Backup Complete", f"Backup created:\n{backup_path}")
    except Exception as e:
        messagebox.showerror("Backup Failed", str(e))


watched_addresses = {}

def watch_memory_addresses():
    game_name = simpledialog.askstring("Watch Memory", "Enter game process name:")
    if not game_name:
        return

    pids = detect_game_process(game_name)
    if not pids:
        messagebox.showerror("Error", f"No process found for: {game_name}")
        return

    pid = pids[0]

    try:
        addr_input = simpledialog.askstring(
            "Memory Addresses",
            "Enter memory addresses (comma-separated, e.g., 0x12345678,0x123456AB):"
        )
        if not addr_input:
            return

        addresses = [int(a.strip(), 16) for a in addr_input.split(",")]

        PROCESS_ALL_ACCESS = 0x1F0FFF
        process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not process:
            raise Exception("Failed to open process.")

        def monitor():
            while True:
                for addr in addresses:
                    try:
                        buffer = ctypes.create_string_buffer(4)
                        bytes_read = ctypes.c_size_t(0)
                        success = ctypes.windll.kernel32.ReadProcessMemory(
                            process,
                            ctypes.c_void_p(addr),
                            buffer,
                            4,
                            ctypes.byref(bytes_read)
                        )
                        if success:
                            val = struct.unpack("i", buffer.raw)[0]
                            prev = watched_addresses.get(addr)
                            if prev != val:
                                watched_addresses[addr] = val
                                log_to_file(f"[{hex(addr)}] Value changed: {prev} -> {val}")
                    except Exception as e:
                        log_to_file(f"Error reading {hex(addr)}: {e}")
                time.sleep(1)

        threading.Thread(target=monitor, daemon=True).start()
        messagebox.showinfo("Watcher Running", f"Now watching {len(addresses)} memory addresses.")

    except Exception as e:
        messagebox.showerror("Memory Watch Error", str(e))
