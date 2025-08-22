FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    android-tools-adb \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/contatos

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 5037

ENTRYPOINT ["docker-entrypoint.sh"]