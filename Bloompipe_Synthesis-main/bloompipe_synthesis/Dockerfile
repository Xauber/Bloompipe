# syntax=docker/dockerfile:1

# Env Setup
FROM python:3.8-slim-buster
WORKDIR /app

# Install Dependencies
COPY reqlist.txt reqlist.txt
RUN pip3 install -r reqlist.txt --no-cache-dir
RUN apt -y update && apt -y install ffmpeg libsndfile1

# Fix Oddities of Mega Package
RUN echo 'from .mega import Mega' >> /usr/local/lib/python3.8/site-packages/mega/__init__.py
RUN sed -i '54,62 s/^/#/' /usr/local/lib/python3.8/site-packages/mega/mega.py

# Start Container
COPY . .
CMD ["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0"]
