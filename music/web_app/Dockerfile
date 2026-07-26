FROM python:3.11-slim
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir flask requests
COPY . /app
EXPOSE 4535
CMD ["python3", "app.py"]
