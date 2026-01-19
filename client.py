import socket, keyboard, yaml, time, subprocess

print("--- Client Diagnostic Mode (Auto-IP) ---")

# 設定読み込み
try:
    with open("config.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
except:
    conf = {"system": {"port": 5005}, "key_mapping": {"l": "A"}}

PORT = conf["system"]["port"]
KEY_MAP = conf["key_mapping"]

# ★修正ポイント: WSLの正しいIPアドレスを自動取得する
print("Detecting WSL IP Address...")
try:
    # wslコマンドを使ってIPを調べる
    result = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True)
    wsl_ip = result.stdout.strip().split()[0]
    print(f"-> Found WSL IP: {wsl_ip}")
    ADDR = (wsl_ip, PORT)
except Exception as e:
    print(f"-> Failed to detect IP ({e}). Fallback to localhost.")
    ADDR = ("127.0.0.1", PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(key_name, cmd):
    print(f"Key [{key_name}] -> Sending {cmd} to {ADDR}...")
    try:
        sock.sendto(cmd.encode(), ADDR)
    except Exception as e:
        print(f"Send Error: {e}")

print("Ready. Press [End] to exit.")

# キー登録
for k, v in KEY_MAP.items():
    try:
        keyboard.on_press_key(str(k).lower(), lambda _, k=k, c=v: send(k, c))
    except: pass

keyboard.wait("end")
