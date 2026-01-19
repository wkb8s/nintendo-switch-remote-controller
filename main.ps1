# -----------------------------------------------------------------------------
# [概要] Switch Remote Controller (Config-Driven)
# [必須] pip install pyyaml
# -----------------------------------------------------------------------------

Write-Host "=== Switch Remote Controller (YAML Config) ===" -ForegroundColor Cyan

# 1. Load Config (YAML -> JSON -> PowerShell Object)
#    PowerShell単体でYAMLを読むのは大変なので、Python経由でオブジェクト化します
$configPath = "config.yaml"
if (-not (Test-Path $configPath)) {
    Write-Error "Config file '$configPath' not found."
    exit
}

try {
    # YAMLを読み込んでJSON経由でPSオブジェクトに変換
    $conf = python -c "import yaml, json; print(json.dumps(yaml.safe_load(open('$configPath', encoding='utf-8'))))" | ConvertFrom-Json
} catch {
    Write-Error "Failed to parse config.yaml. Please ensure 'pip install pyyaml' is run."
    exit
}

# 変数展開
$BUS_ID = $conf.system.bus_id
$MAC    = $conf.system.mac_address
$PORT   = $conf.system.port

Write-Host "Loaded Config:"
Write-Host " - BusID: $BUS_ID"
Write-Host " - MAC:   $MAC"
Write-Host " - Port:  $PORT"

# 2. Attach Bluetooth (Auto)
Write-Host "Checking Bluetooth Adapter..."
try { usbipd attach --wsl --busid $BUS_ID } catch { Write-Warning "Attach skipped (Device might be busy or already attached)." }

# =============================================================================
# 3. WSL Server (Settings injected from YAML)
# =============================================================================
# WSL側にはYAMLファイルを渡さず、読み込んだ値を直接コードに埋め込みます
$wslScript = @"
import socket, nxbt, time

# --- Hardcoded Button Map (Internal Logic) ---
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
print(f'[WSL] Init Controller (MAC: $MAC)')

try:
    controller = nx.create_controller(
        nxbt.PRO_CONTROLLER,
        reconnect_address=nx.create_reconnect_address('$MAC')
    )
except:
    controller = nx.create_controller(nxbt.PRO_CONTROLLER)

print('[WSL] Waiting for Connection...')
nx.wait_for_connection(controller)
print('[WSL] CONNECTED!')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', $PORT))

while True:
    try:
        data, _ = sock.recvfrom(1024)
        cmd = data.decode()
        if cmd in BUTTON_MAP:
            nx.press_buttons(controller, BUTTON_MAP[cmd], down=0.1)
    except Exception as e:
        print(e)
"@

$job = Start-Job -ScriptBlock {
    param($script)
    wsl -u root python3 -c $script
} -ArgumentList $wslScript

# =============================================================================
# 4. Windows Client (Reads YAML directly)
# =============================================================================
Start-Sleep -Seconds 3

Write-Host "------------------------------------------------"
Write-Host " Remote Controller Active"
Write-Host " Mapping loaded from $configPath"
Write-Host " Press [End] to Quit." -ForegroundColor Yellow
Write-Host "------------------------------------------------"

try {
    # Windows側のPythonはファイルを直接読みに行きます
    python -c @"
import socket, keyboard, yaml

with open('$configPath', encoding='utf-8') as f:
    conf = yaml.safe_load(f)

ADDR = ('localhost', conf['system']['port'])
KEY_MAP = conf['key_mapping']

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(cmd):
    try: sock.sendto(cmd.encode(), ADDR)
    except: pass

# Register Keys
for key, cmd in KEY_MAP.items():
    # Convert string key to lowercase just in case
    keyboard.on_press_key(str(key).lower(), lambda _, c=cmd: send(c))

keyboard.wait('end')
"@
}
finally {
    Write-Host "Stopping..."
    Stop-Job $job
    Remove-Job $job
    wsl -u root pkill -f "python3 -c"
    Write-Host "Done."
}
