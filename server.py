import socket
import nxbt
import time
import os
import pickle
import util

CONF = util.load_config()
PORT = CONF["system"]["port"]
PICKLE_FILENAME = CONF["system"]["pickle_filename"]

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
util.log("Init Controller")

# Read saved Switch MAC address
saved_switch_mac = None
if os.path.exists(PICKLE_FILENAME):
    try:
        with open(PICKLE_FILENAME, "rb") as f:
            saved_switch_mac = pickle.load(f)
        util.log(f"Found saved Switch MAC: {saved_switch_mac}")
    except:
        util.log("Saved info corrupted.", "WARNING")

# Make virtual controller and try to reconnect if MAC is available
controller = None
if saved_switch_mac:
    try:
        controller = nx.create_controller(
            nxbt.PRO_CONTROLLER,
            reconnect_address=saved_switch_mac
        )
    except Exception as e:
        util.log(f"Reconnect failed ({e}). Fallback to pairing.", "WARNING")
if controller is None:
    util.log("Starting Pairing Mode (Please open 'Change Grip/Order')...")
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

util.log("Waiting for Connection...")
nx.wait_for_connection(controller)
util.log("CONNECTED! Listening for commands...")

# Save the Switch MAC address for future reconnections
try:
    if not saved_switch_mac:
        switches = nx.get_switch_addresses()
        if switches and len(switches) > 0:
            target_mac = switches[0]
            with open(PICKLE_FILENAME, "wb") as f:
                pickle.dump(target_mac, f)
            util.log(f"Saved Switch MAC ({target_mac}) for next time.")
except Exception as e:
    util.log(f"Failed to save connection info: {e}", "ERROR")

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
        util.log(f"Error: {e}", "ERROR")
