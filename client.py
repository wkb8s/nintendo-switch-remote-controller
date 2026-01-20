import socket
import keyboard
import time
import subprocess
import util

util.log("Client Started")

CONF = util.load_config()
PORT = CONF["system"]["port"]
KEY_MAP = CONF.get("key_mapping", {})
COOLDOWN = 0.15

# Auto-detect WSL IP
util.log("Detecting WSL IP...")
try:
    res = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True)
    wsl_ip = res.stdout.strip().split()[0]
    ADDR = (wsl_ip, PORT)
    util.log(f"-> Target: {wsl_ip}")
except:
    ADDR = ("127.0.0.1", PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Cooldown to prevent button spamming (seconds)
last_send_time = 0
def send(key_name, cmd):
    global last_send_time
    current_time = time.time()

    # Nothing is done during cooldown
    if current_time - last_send_time < COOLDOWN:
        return

    last_send_time = current_time
    util.log(f"Key [{key_name}] -> {cmd}")
    try:
        sock.sendto(cmd.encode(), ADDR)
    except: pass

util.log("Ready. Press [Ctrl+C] or [Q] to exit.")

running = True
def stop_program():
    global running
    running = False

# Exit keys (Q and Ctrl+C)
try:
    keyboard.add_hotkey('q', stop_program)
    keyboard.add_hotkey('ctrl+c', stop_program)
except: pass
for k, v in KEY_MAP.items():
    try:
        keyboard.on_press_key(str(k).lower(), lambda _, k=k, c=v: send(k, c))
    except: pass
while running:
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        break
