import psutil

def detect_game_process(game_name):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if game_name.lower() in proc.info['name'].lower():
            pids.append(proc.info['pid'])
    return pids
