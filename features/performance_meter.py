import tkinter as tk
from tkinter import ttk
import psutil

class PerformanceMeterPanel:
    def __init__(self, parent, process_name_var=None):
        self.parent = parent
        self.process_name_var = process_name_var
        self.cpu_var = tk.DoubleVar()
        self.ram_var = tk.DoubleVar()
        self.proc_cpu_var = tk.DoubleVar()
        self.proc_ram_var = tk.DoubleVar()
        self.setup_ui()
        self.refresh_stats()

    def setup_ui(self):
        frame = ttk.LabelFrame(self.parent, text="System Performance", padding=10)
        frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(frame, text="CPU Usage:").grid(row=0, column=0, sticky="e")
        self.cpu_bar = ttk.Progressbar(frame, variable=self.cpu_var, maximum=100, length=200)
        self.cpu_bar.grid(row=0, column=1, padx=4, pady=2, sticky="w")
        self.cpu_label = ttk.Label(frame, text="0%")
        self.cpu_label.grid(row=0, column=2, sticky="w")

        ttk.Label(frame, text="RAM Usage:").grid(row=1, column=0, sticky="e")
        self.ram_bar = ttk.Progressbar(frame, variable=self.ram_var, maximum=100, length=200)
        self.ram_bar.grid(row=1, column=1, padx=4, pady=2, sticky="w")
        self.ram_label = ttk.Label(frame, text="0%")
        self.ram_label.grid(row=1, column=2, sticky="w")

        self.proc_group = ttk.LabelFrame(self.parent, text="Game Process Performance", padding=10)
        self.proc_group.pack(fill="x", padx=10, pady=8)

        ttk.Label(self.proc_group, text="Proc CPU:").grid(row=0, column=0, sticky="e")
        self.proc_cpu_bar = ttk.Progressbar(self.proc_group, variable=self.proc_cpu_var, maximum=100, length=200)
        self.proc_cpu_bar.grid(row=0, column=1, padx=4, pady=2, sticky="w")
        self.proc_cpu_label = ttk.Label(self.proc_group, text="0%")
        self.proc_cpu_label.grid(row=0, column=2, sticky="w")

        ttk.Label(self.proc_group, text="Proc RAM MB:").grid(row=1, column=0, sticky="e")
        self.proc_ram_label = ttk.Label(self.proc_group, text="0")
        self.proc_ram_label.grid(row=1, column=1, padx=4, pady=2, sticky="w")

    def refresh_stats(self):
        # System CPU/RAM
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        self.cpu_var.set(cpu)
        self.ram_var.set(ram)
        self.cpu_label.config(text=f"{cpu:.1f}%")
        self.ram_label.config(text=f"{ram:.1f}%")

        # Process stats
        proc_cpu = 0
        proc_ram = 0
        proc = None
        pname = None
        if self.process_name_var:
            pname = self.process_name_var.get()
        if pname and pname.lower() != "no processes found":
            for p in psutil.process_iter(['name']):
                try:
                    if pname.lower() in p.info['name'].lower():
                        proc = p
                        break
                except Exception:
                    continue
            if proc:
                try:
                    proc_cpu = proc.cpu_percent(interval=0.1)
                    proc_ram = proc.memory_info().rss / (1024 * 1024)
                except Exception:
                    proc_cpu, proc_ram = 0, 0
        self.proc_cpu_var.set(proc_cpu)
        self.proc_ram_var.set(proc_ram)
        self.proc_cpu_label.config(text=f"{proc_cpu:.1f}%")
        self.proc_ram_label.config(text=f"{proc_ram:.1f} MB")

        # Schedule next update
        self.parent.after(1000, self.refresh_stats)
