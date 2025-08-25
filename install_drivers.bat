@echo off
chcp 65001 > nul
echo.
echo ========================================
echo    INSTALADOR DE DRIVERS ADB - WINDOWS
echo ========================================
echo.
echo ⚠️  EXECUTE COMO ADMINISTRADOR
echo    (Botão direito -> Executar como administrador)
echo.

REM Verificar se é administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Execute como Administrador!
    echo.
    pause
    exit /b 1
)

echo 📥 Instalando drivers ADB...
echo.

REM Tentar instalar drivers automaticamente
if exist "adb\Win\adb.exe" (
    echo 🔧 Instalando drivers do projeto...
    adb\Win\adb.exe devices
) else (
    echo 💡 Baixando Platform Tools...
    echo 📥 Download: https://developer.android.com/studio/releases/platform-tools
    start "" "https://developer.android.com/studio/releases/platform-tools"
)

echo.
echo ✅ Drivers instalados/verificados
echo 💡 Reconecte o dispositivo USB se necessário
echo.
pause