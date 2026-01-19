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

# --- 保存されたSwitchのMACアドレスを読み込む ---
saved_switch_mac = None
if os.path.exists("switch_mac.pickle"):
    try:
        with open("switch_mac.pickle", "rb") as f:
            saved_switch_mac = pickle.load(f)
        print(f"[WSL] Found saved Switch MAC: {saved_switch_mac}")
    except:
        print("[WSL] Saved info corrupted.")

controller = None

# --- コントローラー作成 ---
if saved_switch_mac:
    try:
        # ★修正箇所: 変換などはせず、MACアドレスを「そのまま」渡すのが正解でした
        controller = nx.create_controller(
            nxbt.PRO_CONTROLLER,
            reconnect_address=saved_switch_mac
        )
    except Exception as e:
        print(f"[WSL] Reconnect failed ({e}). Fallback to pairing.")

if controller is None:
    print("[WSL] Starting Pairing Mode (Please open 'Change Grip/Order')...")
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

print("[WSL] Waiting for Connection...")
nx.wait_for_connection(controller)
print("[WSL] CONNECTED! Listening for commands...")

# --- SwitchのMACアドレスを保存 (初回のみ機能) ---
try:
    if not saved_switch_mac:
        switches = nx.get_switch_addresses()
        if switches and len(switches) > 0:
            target_mac = switches[0]
            with open("switch_mac.pickle", "wb") as f:
                pickle.dump(target_mac, f)
            print(f"[WSL] Saved Switch MAC ({target_mac}) for next time.")
except Exception as e:
    print(f"[WSL] Failed to save connection info: {e}")

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
