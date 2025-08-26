FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY app /app
COPY settings.ini /app/settings.ini

CMD ["bash", "-c", "bash /app/prestart.sh && uvicorn main:app --host 0.0.0.0 --port 8000"]
