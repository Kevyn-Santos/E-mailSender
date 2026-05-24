# Etapa 1: instalação de dependências em ambiente isolado
FROM python:3.12-alpine AS dependencias

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Etapa 2: imagem de runtime enxuta
FROM python:3.12-alpine AS runtime

LABEL authors="kevyn"

# Variáveis de reserva — sobrescritas pelo env_file ou environment do compose
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SMTP_SERVER="smtp.gmail.com" \
    PORT_SMTP=465 \
    EHELO="localhost"

WORKDIR /app

# Usuário não-root criado antes de qualquer cópia de arquivos
RUN adduser -D apiuser

# Dependências vindas da etapa anterior — sem ferramentas de build na imagem final
COPY --from=dependencias /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Código copiado com ownership do usuário não-root
COPY --chown=apiuser:apiuser . .

# Diretório de dados com permissão de escrita para o apiuser
RUN mkdir /app/data && chown apiuser:apiuser /app/data

USER apiuser

EXPOSE 8000

CMD ["uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8000"]