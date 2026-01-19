import socket, nxbt, time, os

# 簡易Configパーサー (ライブラリ依存を減らすため手動解析)
CONFIG = {}
try:
    with open("config.yaml", "r") as f:
        for line in f:
            if "port:" in line: CONFIG["PORT"] = int(line.split(":")[1].strip())
            if "mac_address:" in line: CONFIG["MAC"] = line.split(":")[1].strip().replace('"', '')
except:
    print("Config Error")
    exit()

BUTTON_MAP = {
    'L_UP': [nxbt.Buttons.L_STICK_UP], 'L_DOWN': [nxbt.Buttons.L_STICK_DOWN],
    'L_LEFT': [nxbt.Buttons.L_STICK_LEFT], 'L_RIGHT': [nxbt.Buttons.L_STICK_RIGHT],
    'L_PRESS': [nxbt.Buttons.L_STICK_PRESS],
    'R_UP': [nxbt.Buttons.R_STICK_UP], 'R_DOWN': [nxbt.Buttons.R_STICK_DOWN],
    'R_LEFT': [nxbt.Buttons.R_STICK_LEFT], 'R_RIGHT': [nxbt.Buttons.R_STICK_RIGHT],
    'R_PRESS': [nxbt.Buttons.R_STICK_PRESS],
    'DPAD_UP': [nxbt.Buttons.DPAD_UP], 'DPAD_DOWN': [nxbt.Buttons.DPAD_DOWN],
    'DPAD_LEFT': [nxbt.Buttons.DPAD_LEFT], 'DPAD_RIGHT': [nxbt.Buttons.DPAD_RIGHT],
    'A': [nxbt.Buttons.A], 'B': [nxbt.Buttons.B], 'X': [nxbt.Buttons.X], 'Y': [nxbt.Buttons.Y],
    'L': [nxbt.Buttons.L], 'ZL': [nxbt.Buttons.ZL], 'R': [nxbt.Buttons.R], 'ZR': [nxbt.Buttons.ZR],
    'PLUS': [nxbt.Buttons.PLUS], 'MINUS': [nxbt.Buttons.MINUS],
    'HOME': [nxbt.Buttons.HOME], 'CAPTURE': [nxbt.Buttons.CAPTURE]
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
        if cmd in BUTTON_MAP: nx.press_buttons(controller, BUTTON_MAP[cmd], down=0.1)
    except: pass
