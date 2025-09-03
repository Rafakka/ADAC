@echo off
chcp 65001 > nul
echo.
echo 🖥️  ADAC - Auto Discador
echo.
echo [1] Modo Texto (padrão)
echo [2] Interface Gráfica (Recomendado)
echo.
choice /c 12 /n /m "Escolha o modo: "
if %errorlevel% equ 1 (
    python main.py
) else (
    python main.py --gui
)
pause
