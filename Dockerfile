# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /source

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 3100

CMD ["uvicorn", "--app-dir=source", "main:app"]