import socket, nxbt, time, os

# --- 設定読み込み ---
CONFIG = {"PORT": 5005, "MAC": "B8:27:EB:00:53:01"}
try:
    with open("config.yaml", "r") as f:
        for line in f:
            if "port:" in line:
                CONFIG["PORT"] = int(line.split(":")[1].strip())
            if "mac_address:" in line:
                # バグ修正: splitの回数を指定してMACアドレスが切れないように変更
                CONFIG["MAC"] = line.split(":", 1)[1].strip().replace('"', '').replace("'", "")
except Exception as e:
    print(f"[Warning] Config load failed: {e}")

# --- マクロとボタン定義 ---
STICK_MACROS = {
    'L_UP': "L_STICK@000+100 0.1s",    'L_DOWN': "L_STICK@000-100 0.1s",
    'L_LEFT': "L_STICK@-100+000 0.1s", 'L_RIGHT': "L_STICK@100+000 0.1s",
    'R_UP': "R_STICK@000+100 0.1s",    'R_DOWN': "R_STICK@000-100 0.1s",
    'R_LEFT': "R_STICK@-100+000 0.1s", 'R_RIGHT': "R_STICK@100+000 0.1s",
    'L_PRESS': "L_STICK_PRESS 0.1s",   'R_PRESS': "R_STICK_PRESS 0.1s",
}

BUTTON_MAP = {
    'A': [nxbt.Buttons.A], 'B': [nxbt.Buttons.B], 'X': [nxbt.Buttons.X], 'Y': [nxbt.Buttons.Y],
    'L': [nxbt.Buttons.L], 'ZL': [nxbt.Buttons.ZL], 'R': [nxbt.Buttons.R], 'ZR': [nxbt.Buttons.ZR],
    'PLUS': [nxbt.Buttons.PLUS], 'MINUS': [nxbt.Buttons.MINUS],
    'HOME': [nxbt.Buttons.HOME], 'CAPTURE': [nxbt.Buttons.CAPTURE],
    'DPAD_UP': [nxbt.Buttons.DPAD_UP], 'DPAD_DOWN': [nxbt.Buttons.DPAD_DOWN],
    'DPAD_LEFT': [nxbt.Buttons.DPAD_LEFT], 'DPAD_RIGHT': [nxbt.Buttons.DPAD_RIGHT],
}

nx = nxbt.Nxbt()
print(f"[WSL] Init Controller (MAC: {CONFIG['MAC']})")

# 再接続を試みる
try:
    controller = nx.create_controller(
        nxbt.PRO_CONTROLLER,
        reconnect_address=nx.create_reconnect_address(CONFIG['MAC'])
    )
except:
    print("[WSL] Reconnect failed, creating new controller...")
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

print("[WSL] Waiting for Connection...")
nx.wait_for_connection(controller)
print("[WSL] CONNECTED! Listening for commands...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', CONFIG['PORT']))

while True:
    try:
        data, _ = sock.recvfrom(1024)
        cmd = data.decode()

        # ★デバッグ用: 信号が届いたら表示する
        print(f"[DEBUG] Received: {cmd}")

        if cmd in STICK_MACROS:
            nx.macro(controller, STICK_MACROS[cmd])
        elif cmd in BUTTON_MAP:
            nx.press_buttons(controller, BUTTON_MAP[cmd], down=0.1)
    except Exception as e:
        print(f"Error: {e}")
