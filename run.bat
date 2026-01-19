@echo off
cd /d %~dp0

echo === Starting Switch Remote Controller ===

:: 1. Bluetooth接続 (ConfigからBusIDを読み取る荒技)
for /f "tokens=2 delims=:" %%a in ('findstr "bus_id" config.yaml') do set BUSID=%%a
set BUSID=%BUSID:"=%
set BUSID=%BUSID: =%
echo Attaching Bluetooth (BusID: %BUSID%)...
usbipd attach --wsl --busid %BUSID%

:: 2. WSLサーバーをバックグラウンドで起動
echo Starting WSL Server...
start "" /B wsl -u root python3 server.py

:: 3. Windowsクライアントを起動 (少し待ってから)
timeout /t 4 >nul
echo Starting Client...
python client.py

:: 終了処理
echo Closing...
wsl -u root pkill -f "python3 server.py"
pause
