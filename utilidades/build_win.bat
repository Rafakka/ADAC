@echo off
chcp 65001 > nul
echo.
echo 🏗️  Criando executável para Windows...
echo.

REM Instalar PyInstaller se não existir
pip install pyinstaller

REM Criar executável
pyinstaller --onefile --name ADAC ^
  --add-data "contatos;contatos" ^
  --add-data "logs;logs" ^
  --add-data "config;config" ^
  --add-data "adb;adb" ^
  --hidden-import=logging ^
  --hidden-import=subprocess ^
  --hidden-import=os ^
  --hidden-import=sys ^
  --hidden-import=platform ^
  main.py

echo ✅ Executável criado em: dist\ADAC.exe
echo.
pause