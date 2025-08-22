FROM python:3.9-slim

# Instalar ADB e dependências
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    android-tools-adbd \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Criar diretório para contatos
RUN mkdir -p /app/contatos

# Expor porta para ADB (opcional)
EXPOSE 5037

CMD ["python", "main.py"]