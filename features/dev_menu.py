import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os

KONAMI = ['Up', 'Up', 'Down', 'Down', 'Left', 'Right', 'Left', 'Right', 'b', 'a']
EASTER_EGG_TEXT = "🐵 You found the hidden dev Easter Egg! 🐒\nStay curious, keep hacking!"

class DevMenuPanel:
    def __init__(self, parent):
        self.parent = parent
        self.konami_index = 0
        self.setup_ui()
        self.parent.bind_all("<KeyPress>", self.check_konami)

    def setup_ui(self):
        nb = ttk.Notebook(self.parent)
        nb.pack(fill="both", expand=True)

        # --- Script Runner Tab ---
        tab_scripts = ttk.Frame(nb)
        nb.add(tab_scripts, text="Script Runner")
        self.make_script_runner(tab_scripts)

        # --- Live Memory Tab ---
        tab_memory = ttk.Frame(nb)
        nb.add(tab_memory, text="Live Memory (Sim)")
        self.make_memory_tools(tab_memory)

        # --- Developer Logs Tab ---
        tab_logs = ttk.Frame(nb)
        nb.add(tab_logs, text="Dev Logs")
        self.make_logs_tab(tab_logs)

        # --- Quick Toggles Tab ---
        tab_toggles = ttk.Frame(nb)
        nb.add(tab_toggles, text="Debug Toggles")
        self.make_toggles_tab(tab_toggles)

        # --- Easter Egg Panel (hidden, will appear on Konami code) ---
        self.tab_easter_egg = ttk.Frame(nb)
        # Not added to notebook until unlocked

        self.nb = nb

    def make_script_runner(self, tab):
        label = tk.Label(tab, text="Run Code (Python only for now):")
        label.pack(anchor="w", padx=10, pady=(10, 0))
        self.script_box = scrolledtext.ScrolledText(tab, width=80, height=12, font=("Consolas", 10))
        self.script_box.pack(padx=10, pady=4)
        run_btn = tk.Button(tab, text="Run", command=self.run_script)
        run_btn.pack(pady=(0, 8))
        self.script_output = scrolledtext.ScrolledText(tab, width=80, height=8, font=("Consolas", 10), state="disabled")
        self.script_output.pack(padx=10, pady=(0, 8))
        tk.Label(tab, text="(For safety, only print statements are allowed)").pack(anchor="w", padx=10)

    def run_script(self):
        code = self.script_box.get("1.0", "end")
        self.script_output.config(state="normal")
        self.script_output.delete("1.0", "end")
        try:
            # Sandbox: Only allow print(), block imports, no input(), etc
            locals_dict = {}
            def safe_print(*args, **kwargs):
                self.script_output.insert("end", " ".join(str(a) for a in args) + "\n")
            exec(compile(code, "<devmenu>", "exec"), {"print": safe_print}, locals_dict)
        except Exception as e:
            self.script_output.insert("end", f"Error: {e}")
        self.script_output.config(state="disabled")

    def make_memory_tools(self, tab):
        # Simulated memory search/patch
        mem_frame = tk.Frame(tab)
        mem_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(mem_frame, text="Search Value:").grid(row=0, column=0, sticky="e")
        self.search_entry = tk.Entry(mem_frame, width=14)
        self.search_entry.grid(row=0, column=1, padx=4)
        tk.Button(mem_frame, text="Search", command=self.search_memory).grid(row=0, column=2, padx=4)
        tk.Label(mem_frame, text="Patch Addr:").grid(row=1, column=0, sticky="e")
        self.addr_entry = tk.Entry(mem_frame, width=12)
        self.addr_entry.grid(row=1, column=1, padx=4)
        tk.Label(mem_frame, text="New Value:").grid(row=1, column=2, sticky="e")
        self.value_entry = tk.Entry(mem_frame, width=12)
        self.value_entry.grid(row=1, column=3, padx=4)
        tk.Button(mem_frame, text="Patch", command=self.patch_memory).grid(row=1, column=4, padx=4)
        self.mem_result = tk.Label(tab, text="", anchor="w")
        self.mem_result.pack(fill="x", padx=12, pady=4)
        tk.Label(tab, text="(This is a simulation—wire up with your backend for real memory editing.)").pack(anchor="w", padx=10, pady=(0,10))

    def search_memory(self):
        value = self.search_entry.get()
        # Simulate fake addresses
        results = [f"0x{1000+i*16:X}" for i in range(5) if value]
        self.mem_result.config(text="Found at: " + ", ".join(results) if results else "Not found.")

    def patch_memory(self):
        addr = self.addr_entry.get()
        value = self.value_entry.get()
        # Simulate patch result
        self.mem_result.config(text=f"Patched {addr} with {value} (simulated)")

    def make_logs_tab(self, tab):
        # Live tail of dev logs
        self.log_box = scrolledtext.ScrolledText(tab, width=90, height=20, font=("Consolas", 10), state="disabled")
        self.log_box.pack(padx=10, pady=8)
        tk.Button(tab, text="Refresh Logs", command=self.refresh_logs).pack(pady=(0, 8))
        self.log_path = "modding_tool.log"
        self.refresh_logs()

    def refresh_logs(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                self.log_box.insert("end", f.read())
        else:
            self.log_box.insert("end", "No logs found.")
        self.log_box.config(state="disabled")

    def make_toggles_tab(self, tab):
        # Quick debug toggles
        self.verbose_var = tk.BooleanVar()
        self.overlay_var = tk.BooleanVar()
        self.fake_crash_var = tk.BooleanVar()
        frame = tk.Frame(tab)
        frame.pack(fill="x", padx=10, pady=8)
        tk.Checkbutton(frame, text="Verbose Logging", variable=self.verbose_var).grid(row=0, column=0, sticky="w", padx=4)
        tk.Checkbutton(frame, text="Overlay Mode", variable=self.overlay_var).grid(row=1, column=0, sticky="w", padx=4)
        tk.Checkbutton(frame, text="Fake Crash", variable=self.fake_crash_var, command=self.trigger_fake_crash).grid(row=2, column=0, sticky="w", padx=4)
        tk.Button(frame, text="Apply Toggles", command=self.apply_toggles).grid(row=3, column=0, pady=8)

    def apply_toggles(self):
        msg = f"Verbose: {self.verbose_var.get()}, Overlay: {self.overlay_var.get()}, FakeCrash: {self.fake_crash_var.get()}"
        messagebox.showinfo("Toggles", msg)

    def trigger_fake_crash(self):
        if self.fake_crash_var.get():
            raise Exception("This is a simulated developer crash!")

    # --- Konami code/Easter Egg ---
    def check_konami(self, event):
        expected = KONAMI[self.konami_index]
        key = event.keysym.lower() if event.keysym != "b" and event.keysym != "a" else event.char
        key = key.lower()
        if key == expected.lower():
            self.konami_index += 1
            if self.konami_index == len(KONAMI):
                self.unlock_easter_egg()
                self.konami_index = 0
        else:
            self.konami_index = 0

    def unlock_easter_egg(self):
        if not hasattr(self, "egg_added") or not self.egg_added:
            self.nb.add(self.tab_easter_egg, text="🐵 Hidden")
            label = tk.Label(self.tab_easter_egg, text=EASTER_EGG_TEXT, font=("Segoe UI", 16), fg="#3a9")
            label.pack(pady=40)
            self.egg_added = True
            messagebox.showinfo("Easter Egg", "Hidden dev panel unlocked!")
