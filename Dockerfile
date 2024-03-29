# syntax=docker/dockerfile:1

FROM python:3.8-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src/ .
COPY config.yaml .
CMD ["python3", "run.py" ]