FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r /app/requirements.txt

COPY app/ /app/

EXPOSE 8000 1025

CMD ["python", "main.py"]
