FROM python:3.11

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY .env .env
COPY ./app /app
WORKDIR /app/app/
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
