@echo off
chcp 65001 > nul
echo 🔧 Instalador de Drivers ADB para Windows
echo.
echo ⚠️  Execute como Administrador (botão direito -> Executar como Administrador)
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Execute como Administrador!
    pause
    exit /b 1
)

echo 📥 Instalando drivers ADB...
echo.

REM Instalar drivers usando dpinst
if exist "drivers\dpinst.exe" (
    echo 🔧 Executando DPInst...
    drivers\dpinst.exe /LM /SW
) else (
    echo 💡 Baixe os drivers da plataforma Android SDK
    echo 🔗 https://developer.android.com/studio/releases/platform-tools
    pause
)

echo.
echo ✅ Drivers instalados. Reconecte o dispositivo USB.
pause