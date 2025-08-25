#!/bin/bash
echo "🔧 Preparando build do AutoDiscador..."

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar PyInstaller
echo "📥 Instalando PyInstaller..."
pip install pyinstaller

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p dist/autodiscador/adb
mkdir -p dist/autodiscador/adb/Win
mkdir -p dist/autodiscador/adb/Linux

# Copiar arquivos
echo "📋 Copiando arquivos..."
cp -r adb/Win/* dist/autodiscador/adb/Win/ 2>/dev/null || echo "⚠️  Pasta adb/Win/ não encontrada"
cp -r adb/Linux/* dist/autodiscador/adb/Linux/ 2>/dev/null || echo "⚠️  Pasta adb/Linux/ não encontrada"
cp *.py dist/autodiscador/ 2>/dev/null
cp *.csv dist/autodiscador/ 2>/dev/null
cp *.bat dist/autodiscador/ 2>/dev/null
cp *.sh dist/autodiscador/ 2>/dev/null

# Entrar na pasta de distribuição
cd dist/autodiscador

# Dar permissão ao ADB do Linux
if [ -f "adb/Linux/adb" ]; then
    chmod +x adb/Linux/adb
fi

# Fazer build com PyInstaller
echo "🏗️  Criando executável..."
pyinstaller --onefile --name autodiscador \
  --add-data "adb:adb" \
  --add-data "contatos.csv:." \
  --hidden-import=logging \
  --hidden-import=subprocess \
  --hidden-import=os \
  --hidden-import=sys \
  --hidden-import=platform \
  ../main.py

echo "✅ Build concluído!"
echo "📦 Executável em: dist/autodiscador/dist/autodiscador"