# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /source

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "main.py"]