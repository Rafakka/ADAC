@echo off
chcp 65001 > nul
echo.
echo 🎯 ADAC - Instalador para Windows
echo =================================
echo.

REM Verificar e instalar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado
    echo 📥 Baixando instalador do Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe' -OutFile 'python_installer.exe'"
    echo 🛠️  Instalando Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo ✅ Python instalado!
)

REM Criar pastas
if not exist "contatos" mkdir contatos
if not exist "logs" mkdir logs
if not exist "config" mkdir config

REM Criar arquivos padrão
if not exist "contatos\contatos.csv" (
    echo numero,nome,data_nascimento,status,data_processamento,tentativas > contatos\contatos.csv
    echo 11999999999,Exemplo Silva,01/01/1990,PENDENTE,,0 >> contatos\contatos.csv
)

if not exist "config\config.txt" (
    echo numero_redirecionamento=11999999999 > config\config.txt
    echo tempo_discagem=8 >> config\config.txt
    echo tempo_transferencia=12 >> config\config.txt
)

echo ✅ Instalação concluída!
echo 🚀 Execute run.bat para iniciar
echo.
pause