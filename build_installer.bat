@echo off
setlocal

REM 1) Rebuild the EXE (PyInstaller)
pyinstaller --noconfirm --clean StockmarketSim.spec
if errorlevel 1 exit /b 1

REM 2) Rebuild the installer (Inno Setup)
set "ISCC=C:\PROGRA~2\INNOSE~1\ISCC.exe"
"%ISCC%" "installer.iss"
if errorlevel 1 exit /b 1

echo Done.
endlocal
