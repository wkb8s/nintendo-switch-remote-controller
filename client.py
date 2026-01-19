import socket, keyboard, yaml, time, subprocess

print("--- Client (Ctrl+C or Q to Exit) ---")

try:
    with open("config.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
except:
    conf = {"system": {"port": 5005}, "key_mapping": {"l": "A"}}

PORT = conf["system"]["port"]
KEY_MAP = conf["key_mapping"]

# IP自動検出
print("Detecting WSL IP...")
try:
    res = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True)
    wsl_ip = res.stdout.strip().split()[0]
    ADDR = (wsl_ip, PORT)
    print(f"-> Target: {wsl_ip}")
except:
    ADDR = ("127.0.0.1", PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 連打防止用クールダウン (秒) - 元のまま
last_send_time = 0
COOLDOWN = 0.15

def send(key_name, cmd):
    global last_send_time
    current_time = time.time()

    # クールダウン中なら何もしない
    if current_time - last_send_time < COOLDOWN:
        return

    last_send_time = current_time
    # print(f"Key [{key_name}] -> {cmd}")
    try:
        sock.sendto(cmd.encode(), ADDR)
    except: pass

# --- ★変更点1: 終了制御用のフラグと関数を追加 ---
print("Ready. Press [Ctrl+C] or [Q] to exit.")

running = True
def stop_program():
    global running
    running = False

# 終了キーを登録 (Q と Ctrl+C)
try:
    keyboard.add_hotkey('q', stop_program)
    keyboard.add_hotkey('ctrl+c', stop_program)
except: pass

# キー登録
for k, v in KEY_MAP.items():
    try:
        keyboard.on_press_key(str(k).lower(), lambda _, k=k, c=v: send(k, c))
    except: pass

# --- ★変更点2: waitの代わりにループ待機に変更 ---
while running:
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        break
