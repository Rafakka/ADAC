@echo off
chcp 65001 > nul
echo 🚀 Iniciando Auto Discador para Windows
echo.

REM Verificar se Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instalando Python...
    pause
    start "" "https://www.python.org/downloads/"
    exit /b 1
)

REM Verificar se ADB está na pasta
if not exist "adb\adb.exe" (
    echo ❌ ADB não encontrado na pasta adb\
    echo 💡 Certifique-se de que os arquivos ADB estão na pasta adb\
    pause
    exit /b 1
)

REM Instalar drivers automaticamente
echo 📋 Verificando drivers ADB...
adb\adb.exe devices > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Drivers ADB podem ser necessários
    echo 💡 Execute install_drivers.bat como Administrador
)

echo 📱 Dispositivos detectados:
adb\adb.exe devices

echo.
echo 🚀 Executando auto discador...
python main.py contatos.csv

pause