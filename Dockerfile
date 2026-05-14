FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

COPY requirements /app/requirements/
RUN pip install -r /app/requirements/prod.txt

COPY . /app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]