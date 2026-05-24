FROM python:3.12-alpine
LABEL authors="kevyn"

# Defina variáveis de ambiente padrão (podem ser sobrescritas no compose)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SMTP_SERVER="smtp.gmail.com"
ENV PORT_SMTP=465
ENV EHELO="localhost"
# Removido MSG_PATH global para flexibilidade por serviço

WORKDIR /app

# Copie e instale dependências
COPY requirements.txt ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copie o código do projeto
COPY . .

# Crie usuário não-root para segurança
RUN adduser -D apiuser
USER apiuser

# Comando para iniciar a aplicação
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "Main:app"]