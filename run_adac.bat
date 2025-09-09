@echo off
chcp 65001 > nul
echo Escolha o modo:
echo [1] CLI
echo [2] GUI
choice /c 12 /n /m "Selecione: "
if %errorlevel%==1 (
    python main.py
) else (
    python main.py --gui
)
pause
