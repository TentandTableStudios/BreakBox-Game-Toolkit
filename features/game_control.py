
import ctypes
import psutil
import struct
import json
import base64
import os
from tkinter import filedialog, messagebox, simpledialog
from process_tools import detect_game_process
from utils import log_to_file
import hashlib
import random
import subprocess
import shutil
import threading
import time

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
        addr_input = simpledialog.askstring("Memory Addresses", "Enter memory addresses (comma-separated, e.g., 0x12345678,0x123456AB):")
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

def import_mod():
    mod_file = filedialog.askopenfilename(
        title="Select Mod File",
        filetypes=[("Mod Files", "*.zip *.pak *.mod"), ("All Files", "*.*")]
    )
    if not mod_file:
        return

    game_mod_dir = filedialog.askdirectory(title="Select Game's Mod Folder")
    if not game_mod_dir:
        return

    try:
        target_path = os.path.join(game_mod_dir, os.path.basename(mod_file))
        shutil.copy(mod_file, target_path)

        log_to_file(f"Imported mod: {mod_file} -> {target_path}")
        messagebox.showinfo("Mod Imported", f"Mod successfully imported to:\n{target_path}")
    except Exception as e:
        messagebox.showerror("Import Error", str(e))

def launch_game_with_tool():
    exe_path = filedialog.askopenfilename(
        title="Select Game Executable",
        filetypes=[("Executable Files", "*.exe")]
    )
    if not exe_path:
        return

    try:
        subprocess.Popen([exe_path], shell=True)
        log_to_file(f"Launched game: {exe_path}")
        messagebox.showinfo("Game Launched", f"Game launched:\n{exe_path}")
    except Exception as e:
        messagebox.showerror("Launch Failed", str(e))

trainer_states = {} 

def toggle_trainer_option(option_name="GodMode"):
    current = trainer_states.get(option_name, False)
    new_state = not current
    trainer_states[option_name] = new_state

    try:
        if option_name == "GodMode":
            log_to_file(f"GodMode {'ENABLED' if new_state else 'DISABLED'}")
        elif option_name == "InfiniteAmmo":
            log_to_file(f"InfiniteAmmo {'ENABLED' if new_state else 'DISABLED'}")
        else:
            log_to_file(f"{option_name} toggled to {new_state}")

        messagebox.showinfo("Trainer Toggle", f"{option_name} {'ENABLED' if new_state else 'DISABLED'}")
    except Exception as e:
        messagebox.showerror("Trainer Toggle Failed", str(e))

def simulate_corruption():
    file_path = filedialog.askopenfilename(title="Select File to Corrupt")
    if not file_path:
        return

    try:
        with open(file_path, "rb") as f:
            data = bytearray(f.read())

        if len(data) < 16:
            raise Exception("File too small to safely corrupt.")

        # Randomly corrupt ~1% of the file
        corruption_count = max(1, len(data) // 100)
        for _ in range(corruption_count):
            index = random.randint(0, len(data) - 1)
            data[index] = random.randint(0, 255)

        corrupted_path = file_path + ".corrupt"
        with open(corrupted_path, "wb") as f:
            f.write(data)

        messagebox.showinfo("Corruption Complete", f"Corrupted file saved as:\n{corrupted_path}")
        log_to_file(f"Corrupted {file_path} -> {corrupted_path} with {corruption_count} changes")
    except Exception as e:
        messagebox.showerror("Corruption Failed", str(e))

def decrypt_save():
    enc_path = filedialog.askopenfilename(filetypes=[("Encrypted Save", "*.enc")])
    if not enc_path:
        return

    try:
        with open(enc_path, "r") as f:
            encoded = f.read()
        decoded = base64.b64decode(encoded).decode()

        decrypted_path = enc_path.replace(".enc", ".decrypted.json")
        with open(decrypted_path, "w") as f:
            f.write(decoded)

        messagebox.showinfo("Decrypted", f"Decrypted save created:\n{decrypted_path}")
        log_to_file(f"Decrypted save: {decrypted_path}")
    except Exception as e:
        messagebox.showerror("Decryption Error", str(e))


def inject_resources():
    game_dir = filedialog.askdirectory(title="Select Game Directory")
    resource_file = filedialog.askopenfilename(title="Select Resource to Inject")
    if not game_dir or not resource_file:
        return

    try:
        target_path = os.path.join(game_dir, os.path.basename(resource_file))
        with open(resource_file, "rb") as src:
            data = src.read()
        with open(target_path, "wb") as dst:
            dst.write(data)

        messagebox.showinfo("Resource Injected", f"Injected resource into: {target_path}")
        log_to_file(f"Injected resource from {resource_file} to {target_path}")
    except Exception as e:
        messagebox.showerror("Injection Error", str(e))


def check_file_integrity():
    file_path = filedialog.askopenfilename(title="Select file to check integrity")
    if not file_path:
        return

    try:
        with open(file_path, "rb") as f:
            contents = f.read()
            sha256_hash = hashlib.sha256(contents).hexdigest()

        messagebox.showinfo("File Integrity", f"SHA256:\n{sha256_hash}")
        log_to_file(f"Checked integrity for {file_path}: {sha256_hash}")
    except Exception as e:
        messagebox.showerror("Integrity Check Error", str(e))


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def snapshot_state():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Save", "*.json")])
    if not file_path:
        return
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        snap_path = file_path + ".snapshot.json"
        with open(snap_path, "w") as f:
            json.dump(data, f, indent=4)
        log_to_file(f"Snapshot created: {snap_path}")
        messagebox.showinfo("Snapshot", f"Snapshot saved:\n{snap_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def recover_state():
    snap_path = filedialog.askopenfilename(filetypes=[("Snapshot", "*.snapshot.json")])
    if not snap_path:
        return
    original_path = snap_path.replace(".snapshot.json", ".json")
    try:
        with open(snap_path, "r") as f:
            data = json.load(f)
        with open(original_path, "w") as f:
            json.dump(data, f, indent=4)
        log_to_file(f"Recovered state to: {original_path}")
        messagebox.showinfo("Recovered", f"Recovered state:\n{original_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def encrypt_save():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Save", "*.json")])
    if not file_path:
        return
    try:
        with open(file_path, "r") as f:
            content = f.read()
        encoded = base64.b64encode(content.encode()).decode()
        encrypted_path = file_path.replace(".json", ".enc")
        with open(encrypted_path, "w") as f:
            f.write(encoded)
        log_to_file(f"Encrypted save to: {encrypted_path}")
        messagebox.showinfo("Encrypted", f"Encrypted save created:\n{encrypted_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def scan_memory():
    if not is_admin():
        messagebox.showwarning("Permission Denied", "Memory scanning requires admin privileges.\nPlease run the tool as Administrator.")
        return
    _real_scan_memory()

def _real_scan_memory():
    game_name = simpledialog.askstring("Memory Scan", "Enter game process name:")
    if not game_name:
        return

    pids = detect_game_process(game_name)
    if not pids:
        messagebox.showerror("Error", f"No process found for: {game_name}")
        return

    pid = pids[0]
    try:
        PROCESS_ALL_ACCESS = (0x1F0FFF)
        process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not process:
            raise Exception("Could not open process.")

        value = simpledialog.askinteger("Scan Value", "Enter integer value to scan for:")
        if value is None:
            return

        matches = []
        mbi = ctypes.create_string_buffer(48)
        addr = 0
        while addr < 0x7FFFFFFF:
            if ctypes.windll.kernel32.VirtualQueryEx(process, ctypes.c_void_p(addr), mbi, ctypes.sizeof(mbi)):
                baseAddr = struct.unpack("L", mbi.raw[0:4])[0]
                regionSize = struct.unpack("L", mbi.raw[4:8])[0]
                state = struct.unpack("L", mbi.raw[8:12])[0]

                if state == 0x1000:
                    data = ctypes.create_string_buffer(regionSize)
                    bytesRead = ctypes.c_size_t(0)
                    if ctypes.windll.kernel32.ReadProcessMemory(process, ctypes.c_void_p(addr), data, regionSize, ctypes.byref(bytesRead)):
                        for i in range(0, regionSize - 4):
                            if struct.unpack("i", data[i:i+4])[0] == value:
                                matches.append(hex(addr + i))
            addr += 0x1000

        ctypes.windll.kernel32.CloseHandle(process)
        if matches:
            messagebox.showinfo("Matches Found", "Found value at addresses:\n" + "\n".join(matches[:10]))
        else:
            messagebox.showinfo("No Match", "No matches found.")
    except Exception as e:
        messagebox.showerror("Scan Error", str(e))

def edit_memory():
    if not is_admin():
        messagebox.showwarning("Permission Denied", "Memory editing requires admin privileges.\nPlease run the tool as Administrator.")
        return
    _real_edit_memory()

def _real_edit_memory():
    game_name = simpledialog.askstring("Edit Memory", "Enter game process name:")
    if not game_name:
        return

    pids = detect_game_process(game_name)
    if not pids:
        messagebox.showerror("Error", f"No process found for: {game_name}")
        return

    pid = pids[0]
    try:
        addr_str = simpledialog.askstring("Memory Address", "Enter memory address (e.g., 0x12345678):")
        if not addr_str:
            return
        address = int(addr_str, 16)

        new_value = simpledialog.askinteger("New Value", "Enter new integer value to write:")
        if new_value is None:
            return

        PROCESS_ALL_ACCESS = (0x1F0FFF)
        process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not process:
            raise Exception("Could not open process.")

        data = struct.pack("i", new_value)
        bytes_written = ctypes.c_size_t(0)
        success = ctypes.windll.kernel32.WriteProcessMemory(process, ctypes.c_void_p(address), data, len(data), ctypes.byref(bytes_written))
        ctypes.windll.kernel32.CloseHandle(process)

        if success:
            messagebox.showinfo("Success", f"Wrote value {new_value} to address {addr_str}")
        else:
            raise Exception("Write failed.")
    except Exception as e:
        messagebox.showerror("Write Error", str(e))

def modify_and_save_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    try:
        with open(file_path, "r") as f:
            data = f.read()
        modified = data.replace("100", "999")  
        with open(file_path, "w") as f:
            f.write(modified)
        messagebox.showinfo("Success", f"File modified and saved: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def replace_assets():
    source = filedialog.askopenfilename(title="Select replacement file")
    target = filedialog.askopenfilename(title="Select target game file")
    if not source or not target:
        return
    try:
        with open(source, "rb") as fsrc:
            content = fsrc.read()
        with open(target, "wb") as ftgt:
            ftgt.write(content)
        messagebox.showinfo("Replaced", "Asset replaced successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
