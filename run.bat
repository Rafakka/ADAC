@echo off
chcp 65001 > nul
echo.
echo ========================================
echo    ADAC - Auto Discador para Windows
echo ========================================
echo.

REM Verificar se Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 💡 Instale Python em:
    echo    https://www.python.org/downloads/
    echo.
    echo 📋 Durante a instalação, MARQUE a opção:
    echo    "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Verificar se ADB está disponível
if exist "adb\Win\adb.exe" (
    set ADB_CMD=adb\Win\adb.exe
    echo ✅ Usando ADB do projeto
) else (
    set ADB_CMD=adb
    echo ⚠️  Usando ADB do sistema
)

REM Verificar se dispositivo está conectado
echo.
echo 📱 Verificando dispositivos...
%ADB_CMD% devices > nul 2>&1
if errorlevel 1 (
    echo ❌ Problema com o ADB
    echo.
    echo 💡 Soluções:
    echo   1. Conecte o celular via USB
    echo   2. Ative Depuração USB
    echo   3. Autorize o computador no popup do celular
    echo   4. Execute install_drivers.bat como Administrador
    echo.
    pause
    exit /b 1
)

echo.
echo 📋 Dispositivos detectados:
%ADB_CMD% devices

echo.
echo 🚀 Iniciando Auto Discador...
echo.
python main.py

echo.
pause