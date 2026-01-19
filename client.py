import socket, keyboard, yaml, time

print("--- Client Diagnostic Mode ---")

# 設定読み込み
try:
    with open("config.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    print("Config loaded.")
except:
    # 読み込み失敗時の保険
    conf = {"system": {"port": 5005}, "key_mapping": {"l": "A", "w": "L_UP"}}
    print("Config load failed. Using defaults.")

# ★重要: localhost だと不安定なことがあるので 127.0.0.1 を明示
ADDR = ("127.0.0.1", conf["system"]["port"])
KEY_MAP = conf["key_mapping"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(key_name, cmd):
    # 押されたことを画面に表示
    print(f"Key [{key_name}] -> Sending {cmd}...")
    try:
        sock.sendto(cmd.encode(), ADDR)
    except Exception as e:
        print(f"Send Error: {e}")

print(f"Target: {ADDR}")
print("Ready. Press [L] or [W] to test.")
print("Press [End] to exit.")

# キー登録
for k, v in KEY_MAP.items():
    try:
        # どのキーが押されたか分かるようにラップ
        keyboard.on_press_key(str(k).lower(), lambda _, k=k, c=v: send(k, c))
    except:
        pass

keyboard.wait("end")
