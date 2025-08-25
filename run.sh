#!/bin/bash
echo "🚀 Iniciando Auto Discador"
echo "💻 Sistema: $(uname -s)"
echo "📋 Dispositivos detectados:"

# Configurar ADB baseado no sistema
if [ "$(uname -s)" = "Linux" ]; then
    ADB_CMD="adb/Linux/adb"
    chmod +x adb/Linux/adb 2>/dev/null
else
    ADB_CMD="adb"
fi

# Verificar se ADB existe
if [ -f "$ADB_CMD" ]; then
    $ADB_CMD devices
else
    adb devices
fi

echo "🐍 Executando script Python..."
python3 main.py contatos.csv