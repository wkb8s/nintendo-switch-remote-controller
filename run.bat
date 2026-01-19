@echo off
chcp 65001 >nul
cd /d %~dp0

:: --- Config ---
:: Check your BusID with 'usbipd list'
set BUSID=3-7

echo [INFO] Attaching Bluetooth (BusID: %BUSID%)...
usbipd attach --wsl --busid %BUSID%

echo [INFO] Starting WSL Server...
start "" /B wsl -u root python3 server.py

:: Wait for server start
timeout /t 5 >nul

echo [INFO] Starting Client...
python client.py

echo [INFO] Closing...
wsl -u root pkill -f "python3 server.py"
pause
