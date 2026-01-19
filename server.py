import socket, nxbt, time, os, pickle

# --- Bluetoothを叩き起こす ---
os.system("service bluetooth start")
time.sleep(1)

# --- 設定読み込み ---
CONFIG = {"PORT": 5005}
try:
    with open("config.yaml", "r") as f:
        for line in f:
            if "port:" in line:
                CONFIG["PORT"] = int(line.split(":")[1].strip())
except: pass

# --- スティック/ボタン定義 ---
STICK_MACROS = {
    'DPAD_UP':    "L_STICK@+000+100 0.1s",
    'DPAD_DOWN':  "L_STICK@+000-100 0.1s",
    'DPAD_LEFT':  "L_STICK@-100+000 0.1s",
    'DPAD_RIGHT': "L_STICK@+100+000 0.1s",
    'R_UP':       "R_STICK@+000+100 0.1s",
    'R_DOWN':     "R_STICK@+000-100 0.1s",
    'R_LEFT':     "R_STICK@-100+000 0.1s",
    'R_RIGHT':    "R_STICK@+100+000 0.1s",
    'L_PRESS':    "L_STICK_PRESS 0.1s",
    'R_PRESS':    "R_STICK_PRESS 0.1s",
}

BUTTON_MAP = {
    'L_UP': [nxbt.Buttons.DPAD_UP],     'L_DOWN': [nxbt.Buttons.DPAD_DOWN],
    'L_LEFT': [nxbt.Buttons.DPAD_LEFT], 'L_RIGHT': [nxbt.Buttons.DPAD_RIGHT],
    'A': [nxbt.Buttons.A], 'B': [nxbt.Buttons.B], 'X': [nxbt.Buttons.X], 'Y': [nxbt.Buttons.Y],
    'L': [nxbt.Buttons.L], 'ZL': [nxbt.Buttons.ZL], 'R': [nxbt.Buttons.R], 'ZR': [nxbt.Buttons.ZR],
    'PLUS': [nxbt.Buttons.PLUS], 'MINUS': [nxbt.Buttons.MINUS],
    'HOME': [nxbt.Buttons.HOME], 'CAPTURE': [nxbt.Buttons.CAPTURE],
}

nx = nxbt.Nxbt()
print(f"[WSL] Init Controller")

# --- ★重要: 前回の接続情報(鍵)があれば読み込む ---
reconnect_addr = None
if os.path.exists("reconnect_info.pickle"):
    try:
        with open("reconnect_info.pickle", "rb") as f:
            reconnect_addr = pickle.load(f)
        print("[WSL] Found saved connection info!")
    except:
        print("[WSL] Saved info corrupted.")

controller = None

# --- コントローラー作成 (再接続 または 新規ペアリング) ---
if reconnect_addr:
    try:
        # 鍵を使って再接続を試みる
        controller = nx.create_controller(nxbt.PRO_CONTROLLER, reconnect_address=reconnect_addr)
    except Exception as e:
        print(f"[WSL] Reconnect failed ({e}). Fallback to pairing.")

if controller is None:
    # 鍵がない、または失敗した場合は新規ペアリングモード
    print("[WSL] Starting Pairing Mode (Please open 'Change Grip/Order')...")
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

print("[WSL] Waiting for Connection...")
nx.wait_for_connection(controller)
print("[WSL] CONNECTED! Listening for commands...")

# --- ★重要: 次回のために接続情報(鍵)を保存する ---
try:
    new_addr = nx.get_reconnect_address(controller)
    with open("reconnect_info.pickle", "wb") as f:
        pickle.dump(new_addr, f)
    print("[WSL] Connection info SAVED for next time.")
except:
    print("[WSL] Failed to save connection info.")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', CONFIG['PORT']))

while True:
    try:
        data, _ = sock.recvfrom(1024)
        cmd = data.decode()
        if cmd in STICK_MACROS:
            nx.macro(controller, STICK_MACROS[cmd])
        elif cmd in BUTTON_MAP:
            nx.press_buttons(controller, BUTTON_MAP[cmd], down=0.1)
    except Exception as e:
        print(f"Error: {e}")
