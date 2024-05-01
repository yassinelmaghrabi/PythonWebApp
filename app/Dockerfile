FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder
WORKDIR /code
RUN pip install Flask mysql-connector-python
COPY . .
ENV FLASK_APP run.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 8000
ENV FLASK_RUN_HOST 0.0.0.0
EXPOSE 8000

CMD python -m flask run
