[![Integration and testing](https://github.com/Kevyn-Santos/E-mailSender/actions/workflows/CI.yml/badge.svg)](https://github.com/Kevyn-Santos/E-mailSender/actions/workflows/CI.yml)

# FastAPI E-mail Sender

Serviço REST modular desenvolvido em Python com FastAPI para envio de e-mails padronizados via SMTP-SSL. A arquitetura permite que a mesma imagem Docker seja executada como múltiplos contêineres independentes, cada um responsável por um tipo de comunicação diferente (boas-vindas, promoção, redefinição de senha, entre outros), sem qualquer alteração no código-fonte — toda a configuração é feita exclusivamente através de variáveis de ambiente.

---

## Tecnologias

| Categoria            | Tecnologia                                   |
|----------------------|----------------------------------------------|
| Linguagem            | Python 3.12                                  |
| Framework web        | FastAPI 0.124                                |
| Servidor ASGI        | Uvicorn 0.38                                 |
| Validação            | Pydantic 2.12 / Pydantic Settings 2.13       |
| Validação de e-mail  | email-validator 2.3.0                        |
| Envio de e-mail      | smtplib (stdlib) + email.mime (stdlib)       |
| Rate Limiting        | slowapi 0.1.9 (Sliding Window)               |
| Containerização      | Docker / Docker Compose                      |
| Testes               | pytest 9.0.3                                 |
| Templates            | Arquivos `.txt` com substituição de texto    |
| Formulários          | HTML + JavaScript (Fetch API)                |

---

## Estrutura de Diretórios

```
Email_Sender/
│
├── Main.py                  # Ponto de entrada: instancia o app FastAPI, aplica CORS, middlewares e registra os routers
├── conftest.py              # Configuração global do pytest (ajuste de sys.path)
├── Dockerfile
├── Sample.env               # Exemplo de variáveis de ambiente
├── requirements.txt
│
├── src/
│   ├── core/
│   │   ├── settings.py      # Carregamento e validação das variáveis de ambiente via Pydantic Settings
│   │   └── security.py      # Rate limiter e bloqueio de IP
│   │
│   ├── models/
│   │   └── emailModules.py  # Modelo de entrada da requisição (baseUser) com sanitização de nome
│   │
│   ├── routes/
│   │   ├── Sender.py        # Define o endpoint POST /sendMail
│   │   └── Health.py        # Define o endpoint GET /health
│   │
│   └── services/
│       └── sendMail.py      # Lógica de negócio: leitura do template, montagem e envio do e-mail
│
├── Assets/
│   └── mensagem.txt         # Template de e-mail
│
└── scripts/
    └── tests/               # Testes unitários e funcionais (pytest)
```

---

## Fluxo de Chamadas

```
Requisição HTTP POST /sendMail
        |
        v
   Main.py — Middleware block_banned_ips
        |  Verifica se o IP do cliente está na lista de bloqueados
        |  Retorna HTTP 429 com tempo restante caso bloqueado
        |
        v
   slowapi — Rate Limiter (Sliding Window)
        |  Verifica QTD_EMAILS requisições dentro de TMP_EMAILS segundos
        |  Se exceder: bloqueia o IP por TMP_BLOQ segundos → HTTP 429
        |
        v
   routes/Sender.py — email_sender()
        |  Valida o corpo da requisição com o modelo baseUser
        |  Agenda o envio como BackgroundTask
        |
        v
   services/sendMail.py — sendMail()
        |  Chama settings.path_validator() para verificar MSG_PATH
        |
        v
        +——> buildMail()
        |       Lê o arquivo de template
        |       Substitui {usuario} e {email}
        |       Monta o objeto MIMEMultipart
        |
        v
   smtplib.SMTP_SSL
        Autentica e envia a mensagem
```

---

## Variáveis de Ambiente

### Obrigatórias

| Variável   | Descrição                                                                                                  |
|------------|------------------------------------------------------------------------------------------------------------|
| `SENDER`   | Endereço de e-mail remetente                                                                               |
| `PASS`     | Senha de aplicativo do provedor de e-mail (não a senha da conta)                                           |
| `MSG_PATH` | Caminho completo para o arquivo de template dentro do contêiner (ex: `/app/Assets/mensagem.txt`)           |
| `SUBJECT`  | Assunto do e-mail                                                                                          |

### Opcionais

| Variável      | Padrão               | Descrição                                                           |
|---------------|----------------------|---------------------------------------------------------------------|
| `HOSTS`       | `http://localhost`   | Origens CORS adicionais separadas por vírgula. Necessário se o frontend estiver hospedado em um domínio externo. |
| `SMTP_SERVER` | `smtp.gmail.com`     | Hostname do servidor SMTP                                           |
| `PORT_SMTP`   | `465`                | Porta SMTP com SSL                                                  |
| `EHELO`       | `localhost`          | Hostname enviado no handshake EHELO com o servidor SMTP             |
| `QTD_EMAILS`  | `10`                 | Número máximo de requisições permitidas por janela de tempo         |
| `TMP_EMAILS`  | `60`                 | Duração da janela de rate limiting em segundos                      |
| `TMP_BLOQ`    | `30`                 | Tempo de bloqueio do IP após exceder o limite (segundos)            |

---

## Rate Limiting

O serviço implementa um rate limiter por IP com estratégia de **Sliding Window** via `slowapi`. O comportamento é configurável pelas variáveis `QTD_EMAILS`, `TMP_EMAILS` e `TMP_BLOQ`:

- Ao exceder o limite, o IP é bloqueado temporariamente e recebe `HTTP 429`.
- O desbloqueio ocorre automaticamente após `TMP_BLOQ` segundos.
- O middleware `block_banned_ips` em `Main.py` intercepta todas as requisições de IPs bloqueados antes mesmo de chegarem ao endpoint.

---

## Templates de E-mail

Os templates são arquivos `.txt` com dois placeholders disponíveis, substituídos em tempo de execução com os dados recebidos na requisição:

| Placeholder  | Substituído por                    |
|--------------|------------------------------------|
| `{usuario}`  | Nome do destinatário (`userName`)  |
| `{email}`    | E-mail do destinatário (`userMail`)|

**Exemplo de template:**

```
Olá, {usuario}.

Seu cadastro foi realizado com sucesso. O acesso está vinculado ao endereço {email}.

Atenciosamente,
Equipe de Suporte
```

Os templates ficam no diretório `Assets/` e são referenciados pela variável `MSG_PATH`. Por serem montados como volume, podem ser editados sem necessidade de reconstruir a imagem.

---

## API

### `GET /health`

Verifica se o serviço está em execução.

**Resposta de sucesso — HTTP 200:**

```json
{
  "Status": 200,
  "Description": "OK"
}
```

---

### `POST /sendMail`

Envia um e-mail ao destinatário informado utilizando o template configurado no contêiner.

**Corpo da requisição (JSON):**

```json
{
  "userMail": "destinatario@exemplo.com",
  "userName": "Ana Pereira"
}
```

**Resposta de sucesso — HTTP 200:**

```json
{
  "message": "E-mail enviado com sucesso"
}
```

**Resposta de erro — HTTP 429:** Limite de requisições excedido ou IP bloqueado.

**Resposta de erro — HTTP 500:** Caminho do template inválido ou erro no envio SMTP.

> O envio é processado em background (via `BackgroundTasks` do FastAPI), portanto a resposta HTTP é retornada imediatamente ao cliente.

A documentação interativa gerada automaticamente pelo FastAPI está disponível em `/docs` (Swagger UI) e `/redoc` (ReDoc) enquanto o serviço estiver em execução.

---

## Execução

### Desenvolvimento local

Crie um arquivo `.env` na raiz do projeto:

```env
SENDER=remetente@exemplo.com
PASS=senha_de_aplicativo
SMTP_SERVER=smtp.gmail.com
PORT_SMTP=465
MSG_PATH=Assets/mensagem.txt
SUBJECT=Bem-vindo ao serviço
HOSTS=http://meusite.com
```

Instale as dependências e inicie o servidor:

```bash
pip install -r requirements.txt
uvicorn Main:app --reload --host 0.0.0.0 --port 8000
```

---

### Docker CLI

**Construir a imagem:**

```bash
docker build -t kevynsantos/email_api:V4 .
```

**Executar um contêiner:**

```bash
docker run -d \
  --name servico-cadastro \
  -e SENDER=remetente@exemplo.com \
  -e PASS=senha_de_aplicativo \
  -e SMTP_SERVER=smtp.gmail.com \
  -e PORT_SMTP=465 \
  -e MSG_PATH=/app/Assets/mensagem.txt \
  -e SUBJECT="Cadastro realizado com sucesso" \
  -v ./Assets:/app/Assets \
  -p 8000:8000 \
  kevynsantos/email_api:V4
```

---

### Docker Compose

A configuração recomendada para produção executa múltiplos contêineres a partir da mesma imagem, cada um com seu próprio template e assunto:

```yaml
version: '3.8'

services:
  cadastro:
    build: .
    image: kevynsantos/email_api:V4
    container_name: email-cadastro
    env_file:
      - .env
    environment:
      MSG_PATH: /app/Assets/mensagem.txt
      SUBJECT: ${SUBJECT_CADASTRO}
    volumes:
      - ./Assets:/app/Assets
    ports:
      - "8000:8000"
    restart: unless-stopped

  promo:
    build: .
    image: kevynsantos/email_api:V4
    container_name: email-promo
    env_file:
      - .env
    environment:
      MSG_PATH: ${MSG_PATH_PROMO:-/app/Assets/mensagem.txt}
      SUBJECT: ${SUBJECT_PROMO}
    volumes:
      - ./Assets:/app/Assets
    ports:
      - "8001:8000"
    restart: unless-stopped

  reset:
    build: .
    image: kevynsantos/email_api:V4
    container_name: email-reset
    env_file:
      - .env
    environment:
      MSG_PATH: ${MSG_PATH_RESET:-/app/Assets/Reset.txt}
      SUBJECT: ${SUBJECT_RESET}
    volumes:
      - ./Assets:/app/Assets
    ports:
      - "8002:8000"
    restart: unless-stopped
```

---

### Operações

**Iniciar todos os serviços:**

```bash
docker-compose up -d
```

**Iniciar um serviço específico:**

```bash
docker-compose up cadastro
```

**Verificar status:**

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

**Encerrar todos os serviços:**

```bash
docker-compose down
```

---

## Licença

Este projeto está disponível sob a licença MIT.
