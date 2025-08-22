#!/bin/bash

# Script para executar localmente (fora do Docker)

echo "🚀 Iniciando Auto Discador Localmente"

# Verificar se ADB está instalado
if ! command -v adb &> /dev/null; then
    echo "❌ ADB não encontrado. Instale:"
    echo "   Ubuntu/Debian: sudo apt-get install android-tools-adb"
    echo "   Fedora: sudo dnf install android-tools"
    echo "   Arch: sudo pacman -S android-tools"
    exit 1
fi

# Verificar se Python está instalado
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado. Instale:"
    echo "   Ubuntu/Debian: sudo apt-get install python3"
    echo "   Fedora: sudo dnf install python3"
    echo "   Arch: sudo pacman -S python"
    exit 1
fi

echo "✅ Usando: $PYTHON_CMD"

# Reiniciar servidor ADB
echo "🔄 Reiniciando servidor ADB..."
adb kill-server
adb start-server

sleep 2

echo "📋 Dispositivos detectados:"
adb devices -l

# Verificar se há dispositivos conectados
if adb devices | grep -q "device$"; then
    echo "✅ Dispositivo Android detectado!"
    echo "🚀 Iniciando auto discador..."
    
    # Executar o script Python
    $PYTHON_CMD main.py contatos.csv
else
    echo "❌ Nenhum dispositivo Android encontrado"
    echo "💡 Verifique:"
    echo "   - Cable USB conectado"
    echo "   - Depuração USB habilitada"
    echo "   - Autorização concedida no dispositivo"
    echo ""
    echo "📱 Tentando listar dispositivos USB..."
    lsusb || echo "lsusb não disponível"
    exit 1
fi