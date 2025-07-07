import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta

class ScheduledActionsPanel:
    def __init__(self, parent):
        self.parent = parent
        self.actions = []
        self.scheduled_threads = []
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.LabelFrame(self.parent, text="Schedule New Action", padding=10)
        frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(frame, text="Action:").grid(row=0, column=0, sticky="e")
        self.action_var = tk.StringVar(value="None")
        self.action_menu = ttk.Combobox(frame, textvariable=self.action_var, values=["Enable Mod", "Disable Mod", "Run Script"], state="readonly", width=18)
        self.action_menu.grid(row=0, column=1, padx=4, pady=2)

        ttk.Label(frame, text="Target (mod/script):").grid(row=0, column=2, sticky="e")
        self.target_entry = ttk.Entry(frame, width=20)
        self.target_entry.grid(row=0, column=3, padx=4, pady=2)

        ttk.Label(frame, text="When (HH:MM:SS):").grid(row=1, column=0, sticky="e")
        self.time_entry = ttk.Entry(frame, width=10)
        self.time_entry.insert(0, (datetime.now() + timedelta(minutes=1)).strftime("%H:%M:%S"))
        self.time_entry.grid(row=1, column=1, padx=4, pady=2)

        ttk.Button(frame, text="Schedule", command=self.schedule_action).grid(row=1, column=3, padx=4, pady=2, sticky="e")

        # Scheduled actions list
        self.list_frame = ttk.LabelFrame(self.parent, text="Upcoming Scheduled Actions", padding=10)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.action_listbox = tk.Listbox(self.list_frame, height=6)
        self.action_listbox.pack(fill="both", expand=True, side="left")
        del_btn = ttk.Button(self.list_frame, text="Cancel Selected", command=self.cancel_selected)
        del_btn.pack(side="left", padx=8)

    def schedule_action(self):
        action = self.action_var.get()
        target = self.target_entry.get()
        when_str = self.time_entry.get()
        try:
            now = datetime.now()
            when = datetime.strptime(when_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
            if when < now:
                when += timedelta(days=1)
            delay = (when - now).total_seconds()
            # Save action to list
            action_info = (action, target, when.strftime("%H:%M:%S"))
            self.actions.append(action_info)
            self.action_listbox.insert("end", f"{action} {target} at {when.strftime('%H:%M:%S')}")
            # Start thread to run
            t = threading.Thread(target=self.run_action, args=(action, target, delay, len(self.actions)-1), daemon=True)
            t.start()
            self.scheduled_threads.append(t)
        except Exception as e:
            messagebox.showerror("Schedule Action", f"Failed to schedule:\n{e}")

    def run_action(self, action, target, delay, index):
        try:
            time.sleep(delay)
            # Simulate action (replace with real calls as needed)
            if action == "Enable Mod":
                result = f"Enabled mod: {target}"
            elif action == "Disable Mod":
                result = f"Disabled mod: {target}"
            elif action == "Run Script":
                result = f"Ran script: {target}"
            else:
                result = "Unknown action"
            # Mark action as done in listbox
            self.action_listbox.delete(index)
            self.action_listbox.insert(index, f"[DONE] {action} {target}")
            messagebox.showinfo("Scheduled Action Done", result)
        except Exception as e:
            messagebox.showerror("Scheduled Action Failed", str(e))

    def cancel_selected(self):
        idx = self.action_listbox.curselection()
        if not idx:
            messagebox.showwarning("Cancel", "No action selected.")
            return
        try:
            self.action_listbox.delete(idx[0])
            del self.actions[idx[0]]
            # No way to stop threads, but mark as cancelled in list (real tool would use a more advanced scheduler)
        except Exception as e:
            messagebox.showerror("Cancel Action", str(e))
