FROM python:3.13-slim
WORKDIR /app
COPY app.py .
RUN date > build-info.txt
CMD ["python", "app.py"]
