FROM python:3.12-alpine
LABEL authors="kevyn"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SMTP_SERVER="smtp.gmail.com"
ENV PORT_SMTP=465
ENV EHELO="localhost"
ENV MSG_PATH=/app/Assets

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser -D apiuser
USER apiuser

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "Main:app"]