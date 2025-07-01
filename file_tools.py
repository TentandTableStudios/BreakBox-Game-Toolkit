import json
import shutil
from utils import log_to_file

def load_save_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_to_file(f"Error loading file: {e}")
        return None

def save_modified_file(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        log_to_file(f"Modified file saved to: {file_path}")
    except Exception as e:
        log_to_file(f"Error saving file: {e}")

def backup_file(file_path):
    try:
        backup_path = file_path + ".bak"
        shutil.copyfile(file_path, backup_path)
        log_to_file(f"Backup created at: {backup_path}")
    except Exception as e:
        log_to_file(f"Error creating backup: {e}")
