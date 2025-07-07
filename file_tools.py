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

def reset_save_file(file_path, template_path):
    try:
        shutil.copyfile(template_path, file_path)
        log_to_file(f"Save file reset using: {template_path}")
    except Exception as e:
        log_to_file(f"Error resetting file: {e}")
import os
import zipfile

def safe_extract_zip(zip_path, extract_to="."):
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            member_path = os.path.normpath(member)
            # Check for absolute paths or ".." components
            if os.path.isabs(member_path) or member_path.startswith("..") or ".." in member_path.split(os.sep):
                raise Exception(f"Unsafe ZIP member: {member_path}")
            dest_path = os.path.abspath(os.path.join(extract_to, member_path))
            if not dest_path.startswith(os.path.abspath(extract_to)):
                raise Exception(f"Illegal file extraction: {dest_path}")
        zf.extractall(extract_to)


