FROM python:3.12-slim

WORKDIR /app

COPY src ./src
COPY adb ./adb
COPY dados ./dados

RUN pip install --no-cache-dir -r src/requirements.txt || true

RUN chmod +x ;/adb/adb

CMD [ "python","src/adac.py" ]
