import socket, nxbt, time

# 簡易Config読み込み
CONFIG = {"PORT": 5005, "MAC": "B8:27:EB:00:53:01"} # デフォルト
try:
    with open("config.yaml", "r") as f:
        for line in f:
            if "port:" in line: CONFIG["PORT"] = int(line.split(":")[1].strip())
            if "mac_address:" in line: CONFIG["MAC"] = line.split(":")[1].strip().replace('"', '')
except: pass

# --- ここを修正: スティックはマクロで定義 ---
STICK_MACROS = {
    'L_UP': "L_STICK@000+100 0.1s",    'L_DOWN': "L_STICK@000-100 0.1s",
    'L_LEFT': "L_STICK@-100+000 0.1s", 'L_RIGHT': "L_STICK@100+000 0.1s",
    'R_UP': "R_STICK@000+100 0.1s",    'R_DOWN': "R_STICK@000-100 0.1s",
    'R_LEFT': "R_STICK@-100+000 0.1s", 'R_RIGHT': "R_STICK@100+000 0.1s",
}

# --- 通常のボタン ---
BUTTON_MAP = {
    'A': [nxbt.Buttons.A], 'B': [nxbt.Buttons.B], 'X': [nxbt.Buttons.X], 'Y': [nxbt.Buttons.Y],
    'L': [nxbt.Buttons.L], 'ZL': [nxbt.Buttons.ZL], 'R': [nxbt.Buttons.R], 'ZR': [nxbt.Buttons.ZR],
    'PLUS': [nxbt.Buttons.PLUS], 'MINUS': [nxbt.Buttons.MINUS],
    'HOME': [nxbt.Buttons.HOME], 'CAPTURE': [nxbt.Buttons.CAPTURE],
    'DPAD_UP': [nxbt.Buttons.DPAD_UP], 'DPAD_DOWN': [nxbt.Buttons.DPAD_DOWN],
    'DPAD_LEFT': [nxbt.Buttons.DPAD_LEFT], 'DPAD_RIGHT': [nxbt.Buttons.DPAD_RIGHT],
    'L_PRESS': [nxbt.Buttons.L_STICK_PRESS], 'R_PRESS': [nxbt.Buttons.R_STICK_PRESS],
}

nx = nxbt.Nxbt()
print(f"[WSL] Init Controller (MAC: {CONFIG['MAC']})")
try:
    controller = nx.create_controller(nxbt.PRO_CONTROLLER, reconnect_address=nx.create_reconnect_address(CONFIG['MAC']))
except:
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

nx.wait_for_connection(controller)
print("[WSL] CONNECTED!")

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
    except: pass
