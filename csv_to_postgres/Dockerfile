FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash etl

COPY ./csv_to_postgres/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./csv_to_postgres/ ./csv_to_postgres
COPY ./etl ./etl

RUN chown -R etl:etl /app
USER etl

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app/csv_to_postgres

CMD ["python", "migration-script.py"]