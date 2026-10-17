FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir redis flask

COPY app.py .

CMD ["python", "app.py"]
