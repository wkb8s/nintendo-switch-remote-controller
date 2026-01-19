@echo off
chcp 65001 >nul
cd /d %~dp0

:: --- Config ---
set BUSID=3-7

echo [INFO] Waking up WSL...
wsl -e ls >nul

echo [INFO] Attaching Bluetooth (BusID: %BUSID%)...
usbipd attach --wsl --busid %BUSID%

echo [INFO] Starting WSL Server...
start "" /B wsl -u root python3 server.py

timeout /t 5 >nul

echo [INFO] Starting Client...
python client.py

echo [INFO] Closing...
wsl -u root pkill -f "python3 server.py"
pause
