FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg docker.io && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install --no-cache-dir flask requests deemix spotdl
COPY patch_deezer.py /patch_deezer.py
RUN python3 /patch_deezer.py
COPY . /app
EXPOSE 4535
CMD ["python3", "app.py"]
