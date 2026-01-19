import socket, keyboard, yaml, time

try:
    with open("config.yaml", encoding="utf-8") as f:
        conf = yaml.safe_load(f)
except Exception as e:
    print(f"Config Error: {e}")
    time.sleep(5)
    exit()

ADDR = ("localhost", conf["system"]["port"])
KEY_MAP = conf["key_mapping"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def send(cmd):
    try: sock.sendto(cmd.encode(), ADDR)
    except: pass

print(f"Client Ready. Port: {conf['system']['port']}")
print("Press [End] to exit.")

for k, v in KEY_MAP.items():
    try:
        keyboard.on_press_key(str(k).lower(), lambda _, c=v: send(c))
    except ValueError:
        print(f"Key mapping error: {k}")

keyboard.wait("end")
