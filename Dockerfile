FROM python:3.12-slim

RUN apt-get update && apt-get install -y adb && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r src/requirements.txt
COPY adac.py .

CMD [ "python","src/adac.py" ]
