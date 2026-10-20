FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask requests deemix yt-dlp
COPY patch_deezer.py /patch_deezer.py
RUN python3 /patch_deezer.py
COPY . /app
EXPOSE 4535
CMD ["python3", "app.py"]
