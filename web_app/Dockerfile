FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask requests yt-dlp mutagen
COPY . /app
EXPOSE 4535
CMD ["python3", "app.py"]
