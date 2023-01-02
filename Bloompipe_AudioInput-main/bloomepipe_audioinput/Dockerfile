# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY reqlist.txt reqlist.txt

RUN pip3 install -r reqlist.txt

RUN apt -y update && apt -y install ffmpeg

COPY . .

CMD ["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0"]
