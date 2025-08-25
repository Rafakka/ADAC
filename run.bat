@echo off
chcp 65001 > nul
echo 🚀 Iniciando Auto Discador para Windows
echo.

REM Verificar se Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado.
    echo 💡 Instale Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Usar ADB da pasta Win
if exist "adb\Win\adb.exe" (
    set ADB_CMD=adb\Win\adb.exe
    echo ✅ Usando ADB do projeto
) else (
    set ADB_CMD=adb
    echo ⚠️  Usando ADB do sistema
)

echo 📋 Dispositivos detectados:
%ADB_CMD% devices

echo.
echo 🚀 Executando auto discador...
python main.py contatos.csv

pause