FROM python:3.12-alpine
LABEL authors="kevyn"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser -D apiuser
USER apiuser

EXPOSE 8000/tcp

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "Main:app"]