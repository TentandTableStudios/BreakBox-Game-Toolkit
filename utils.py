import time

def log_to_file(message):
    with open("modding_tool.log", "a") as f:
        f.write(f"{time.ctime()}: {message}\n")
