import socket, nxbt, time, os

# --- 設定読み込み ---
CONFIG = {"PORT": 5005, "MAC": "B8:27:EB:00:53:01"}
try:
    with open("config.yaml", "r") as f:
        for line in f:
            if "port:" in line:
                CONFIG["PORT"] = int(line.split(":")[1].strip())
            if "mac_address:" in line:
                CONFIG["MAC"] = line.split(":", 1)[1].strip().replace('"', '').replace("'", "")
except: pass

# --- ★修正1: スティック操作の時間も短縮 (0.1s -> 0.05s) ---
STICK_MACROS = {
    'DPAD_UP':    "L_STICK@+000+100 0.05s",
    'DPAD_DOWN':  "L_STICK@+000-100 0.05s",
    'DPAD_LEFT':  "L_STICK@-100+000 0.05s",
    'DPAD_RIGHT': "L_STICK@+100+000 0.05s",
    'R_UP':       "R_STICK@+000+100 0.05s",
    'R_DOWN':     "R_STICK@+000-100 0.05s",
    'R_LEFT':     "R_STICK@-100+000 0.05s",
    'R_RIGHT':    "R_STICK@+100+000 0.05s",
    'L_PRESS':    "L_STICK_PRESS 0.05s",
    'R_PRESS':    "R_STICK_PRESS 0.05s",
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
print(f"[WSL] Init Controller (MAC: {CONFIG['MAC']})")

try:
    controller = nx.create_controller(nxbt.PRO_CONTROLLER, reconnect_address=nx.create_reconnect_address(CONFIG['MAC']))
except:
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

nx.wait_for_connection(controller)
print("[WSL] CONNECTED! Listening...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', CONFIG['PORT']))

while True:
    try:
        data, _ = sock.recvfrom(1024)
        cmd = data.decode()

        if cmd in STICK_MACROS:
            nx.macro(controller, STICK_MACROS[cmd])
        elif cmd in BUTTON_MAP:
            # --- ★修正2: ボタンを押す時間を 0.1 -> 0.05 に短縮 ---
            nx.press_buttons(controller, BUTTON_MAP[cmd], down=0.05)
    except: pass
