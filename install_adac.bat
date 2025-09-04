@echo off
chcp 65001 > nul
setlocal

REM ---------------------------
REM Configurações de caminho
REM ---------------------------
set ROOT_DIR=%~dp0
set PYTHON_PATH=%ROOT_DIR%python\python.exe
set PIP_PATH=%ROOT_DIR%python\Scripts\pip.exe
set ADB_PATH=%ROOT_DIR%adb\Win\adb.exe
set REQ_FILE=%ROOT_DIR%requirements.txt

echo.
echo ADAC - Instalador e Inicializador
echo ================================

REM ---------------------------
REM Verifica Python embutido
REM ---------------------------
if exist "%PYTHON_PATH%" (
    echo Python encontrado: %PYTHON_PATH%
) else (
    echo Python nao encontrado em python\python.exe
    echo Instale a versão full dentro da pasta python\
    pause
    exit /b 1
)

REM ---------------------------
REM Checa pip, setuptools e wheel
REM ---------------------------
"%PYTHON_PATH%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Pip nao encontrado, instalando via get-pip.py...
    if exist "%ROOT_DIR%get-pip.py" (
        "%PYTHON_PATH%" "%ROOT_DIR%get-pip.py"
    ) else (
        echo Arquivo get-pip.py nao encontrado no root
        pause
        exit /b 1
    )
)

"%PYTHON_PATH%" -m pip install --upgrade pip setuptools wheel

REM ---------------------------
REM Instala dependencias
REM ---------------------------
echo Instalando dependencias do requirements.txt...
"%PYTHON_PATH%" -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo Falha ao instalar dependencias via pip. Tentando instalar pygame via .whl local...
    if exist "%ROOT_DIR%python\whl\pygame*.whl" (
        "%PYTHON_PATH%" -m pip install "%ROOT_DIR%python\whl\pygame*.whl"
    ) else (
        echo Arquivo .whl do pygame nao encontrado.
        pause
        exit /b 1
    )
)

REM ---------------------------
REM Checa ADB
REM ---------------------------
if exist "%ADB_PATH%" (
    echo ADB encontrado: %ADB_PATH%
    echo Testando conexao ADB...
    "%ADB_PATH%" devices
) else (
    echo ADB nao encontrado em adb\Win\adb.exe
    echo Baixe o Platform Tools e coloque em adb\Win
    pause
    exit /b 1
)

REM ---------------------------
REM Criar pastas default se nao existirem
REM ---------------------------
if not exist "%ROOT_DIR%contatos" mkdir "%ROOT_DIR%contatos"
if not exist "%ROOT_DIR%logs" mkdir "%ROOT_DIR%logs"
if not exist "%ROOT_DIR%config" mkdir "%ROOT_DIR%config"

REM Arquivos default
if not exist "%ROOT_DIR%contatos\contatos.csv" (
    echo numero,nome,data_nascimento,status,data_processamento,tentativas> "%ROOT_DIR%contatos\contatos.csv"
    echo 11999999999,Exemplo Silva,01/01/1990,PENDENTE,,0>> "%ROOT_DIR%contatos\contatos.csv"
)
if not exist "%ROOT_DIR%config\config.txt" (
    echo numero_redirecionamento=11999999999> "%ROOT_DIR%config\config.txt"
    echo tempo_discagem=8>> "%ROOT_DIR%config\config.txt"
    echo tempo_transferencia=12>> "%ROOT_DIR%config\config.txt"
)

REM ---------------------------
REM Tudo instalado
REM ---------------------------
echo.

pause
endlocal
