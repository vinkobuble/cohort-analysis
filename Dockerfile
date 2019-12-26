FROM python:3.7-alpine

COPY ./solution /solution
ADD ./data/ /data/
WORKDIR /solution
