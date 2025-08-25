@echo off
chcp 65001 > nul
echo.
echo 🛠️  Configuração do ADAC para Windows
echo.

REM Criar pastas necessárias
if not exist "contatos" mkdir contatos
if not exist "logs" mkdir logs
if not exist "config" mkdir config

REM Verificar se CSV existe
if not exist "contatos\contatos.csv" (
    echo 📋 Criando arquivo CSV modelo...
    echo numero,nome,data_nascimento,status,data_processamento,tentativas > contatos\contatos.csv
    echo 11999999999,Exemplo Silva,01/01/1990,PENDENTE,,0 >> contatos\contatos.csv
)

REM Verificar se config existe
if not exist "config\config.txt" (
    echo ⚙️  Criando arquivo de configuração...
    echo # Configurações do ADAC > config\config.txt
    echo numero_redirecionamento=11999999999 >> config\config.txt
    echo tempo_discagem=8 >> config\config.txt
    echo tempo_transferencia=12 >> config\config.txt
)

echo ✅ Configuração concluída!
echo 💡 Agora execute run.bat
echo.
pause