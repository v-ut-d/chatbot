FROM python:3.7-bullseye as builder

WORKDIR /app

COPY requirements.lock /app
RUN pip3 install -r requirements.lock

FROM python:3.7-slim-bullseye as runner

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    libpq-dev \
 && apt-get -y clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages

COPY chatbot.py /app

CMD ["python", "-u", "/app/chatbot.py"]