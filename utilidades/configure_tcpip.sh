#!/bin/bash

# Configurar ADB via TCP/IP

# 1. Conectar via USB primeiro
adb devices

# 2. Configurar porta TCP
adb tcpip 5555

# 3. Obter IP do dispositivo
IP=$(adb shell ip addr show wlan0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)

echo "📱 IP do dispositivo: $IP"

# 4. Conectar via TCP
adb connect $IP:5555

echo "✅ Conectado via TCP/IP: $IP:5555"