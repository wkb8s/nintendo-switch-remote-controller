import socket, keyboard, yaml, time, subprocess, sys

print("--- Client (Ctrl+C or Q to Exit) ---")

try:
    with open("config.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
except:
    conf = {"system": {"port": 5005}, "key_mapping": {"l": "A"}}

PORT = conf["system"]["port"]
KEY_MAP = conf["key_mapping"]

# IP自動検出
try:
    res = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True)
    wsl_ip = res.stdout.strip().split()[0]
    ADDR = (wsl_ip, PORT)
except:
    ADDR = ("127.0.0.1", PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

last_send_time = 0
# 滑らか設定 (0.06秒) を維持
COOLDOWN = 0.06

def send(key_name, cmd):
    global last_send_time
    current_time = time.time()

    if current_time - last_send_time < COOLDOWN:
        return

    last_send_time = current_time
    try:
        sock.sendto(cmd.encode(), ADDR)
    except: pass

# --- 終了処理の仕組みを変更 ---
running = True
def stop_program():
    global running
    running = False

# Ctrl+C と Q の両方を終了キーとして登録
# (Remote Desktop環境でもどちらかは必ず効くはずです)
try:
    keyboard.add_hotkey('ctrl+c', stop_program)
    keyboard.add_hotkey('q', stop_program)
except: pass

print(f"Target: {ADDR}")
print("Ready. Press [Ctrl+C] or [Q] to exit.")

# キー登録
for k, v in KEY_MAP.items():
    try:
        keyboard.on_press_key(str(k).lower(), lambda _, k=k, c=v: send(k, c))
    except: pass

# メインループ
while running:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        # 万が一 Ctrl+C がOSの割り込みとして処理された場合も安全に終了
        stop_program()
