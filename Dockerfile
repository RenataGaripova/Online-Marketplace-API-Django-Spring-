FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gettext \
        redis-tools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/prod.txt /app/requirements/prod.txt
RUN pip install --no-cache-dir -r /app/requirements/prod.txt

COPY . /app/

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["sh", "/app/start.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]
