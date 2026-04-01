# FastAPI E-mail Sender

Serviço REST modular desenvolvido em Python com FastAPI para envio de e-mails padronizados via SMTP-SSL. A arquitetura permite que a mesma imagem Docker seja executada como múltiplos contêineres independentes, cada um responsável por um tipo de comunicação diferente (boas-vindas, promoção, redefinição de senha, entre outros), sem qualquer alteração no código-fonte — toda a configuração é feita exclusivamente através de variáveis de ambiente.

---

## Tecnologias

| Categoria         | Tecnologia                                  |
|-------------------|---------------------------------------------|
| Linguagem         | Python 3.12                                 |
| Framework web     | FastAPI 0.124                               |
| Servidor ASGI     | Uvicorn 0.38                                |
| Validação         | Pydantic 2.12 / Pydantic Settings 2.13      |
| Envio de e-mail   | smtplib (stdlib) + email.mime (stdlib)      |
| Containerização   | Docker / Docker Compose                     |
| Templates         | Arquivos `.txt` com substituição de texto   |
| Formulários       | HTML + JavaScript (Fetch API)               |

---

## Estrutura de Diretórios

```
Email_Sender/
│
├── Main.py                  # Ponto de entrada: instancia o app FastAPI, aplica CORS e registra o router
│
├── core/
│   └── settings.py          # Carregamento e validação das variáveis de ambiente via Pydantic Settings
│
├── routes/
│   └── Sender.py            # Define o endpoint POST /sendMail
│
├── models/
│   └── emailModules.py      # Modelo de entrada da requisição (baseUser) com sanitização de nome
│
├── services/
│   └── sendMail.py          # Lógica de negócio: leitura do template, montagem e envio do e-mail
│
├── Assets/
│   ├── mensagem.txt         # Template de e-mail
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                     # Variáveis de ambiente locais (não versionado)
```

---

## Fluxo de Chamadas

```
Requisição HTTP POST /sendMail
        |
        v
   Main.py (FastAPI app)
        |
        |
        v
        |
        +——> buildMail()
        |       Lê o arquivo de template
        |       Substitui {usuario} e {email}
        |       Monta o objeto MIMEMultipart
        |
        |
   services/sendMail.py — sendMail()
        |  Chama settings.path_validator() para verificar MSG_PATH
        |
        v
   routes/Sender.py — email_sender()
        |  Valida o corpo da requisição com o modelo baseUser
        |  Agenda o envio como BackgroundTask
        |
        v
   smtplib.SMTP_SSL
        Autentica e envia a mensagem
```

---

## Variáveis de Ambiente

### Obrigatórias

| Variável   | Descrição                                                                 |
|------------|---------------------------------------------------------------------------|
| `SENDER`   | Endereço de e-mail remetente                                              |
| `PASS`     | Senha de aplicativo do provedor de e-mail (não a senha da conta)          |
| `MSG_PATH` | Caminho completo para o arquivo de template dentro do contêiner           |
| `SUBJECT`  | Assunto do e-mail                                                         |
| `HOSTS`    | Origens CORS adicionais separadas por vírgula. Variantes de localhost são sempre permitidas por padrão. |

### Opcionais

| Variável      | Padrão           | Descrição                                                    |
|---------------|------------------|--------------------------------------------------------------|
| `SMTP_SERVER` | `smtp.gmail.com` | Hostname do servidor SMTP                                    |
| `PORT_SMTP`   | `465`            | Porta SMTP com SSL                                           |
| `EHELO`       | `localhost`      | Hostname enviado no handshake EHELO com o servidor SMTP      |



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

**Resposta de erro — HTTP 500:**


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
docker build -t email-sender:v1 .
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
  email-sender:v1
```

---

### Docker Compose

A configuração recomendada para produção executa múltiplos contêineres a partir da mesma imagem, cada um com seu próprio template e assunto:

```yaml
version: '3.8'

services:
  cadastro:
    build: .
    image: email-sender:v1
    env_file:
      - .env                               # Contém SENDER e PASS
    environment:
      MSG_PATH: /app/Assets/mensagem.txt
      SUBJECT: "Cadastro realizado com sucesso"
    volumes:
      - ./Assets:/app/Assets
    ports:
      - "8000:8000"
    restart: unless-stopped

  promo:
    build: .
    image: email-sender:v1
    env_file:
      - .env
    environment:
      MSG_PATH: ${MSG_PATH_PROMO:-/app/Assets/mensagem.txt} # Personalizavel com Interpolação
      SUBJECT: ${SUBJECT_PROMO}
    volumes:
      - ./Assets:/app/Assets
    ports:
      - "8001:8000"
    restart: unless-stopped

  reset:
    build: .
    image: email-sender:v1
    environment:
      SENDER: remetente@exemplo.com
      PASS: senha_de_aplicativo
      SMTP_SERVER: smtp.gmail.com
      PORT_SMTP: 465
      MSG_PATH: /app/Assets/Reset.txt
      SUBJECT: "Redefinicao de senha"
    volumes:
      - ./Assets:/app/Assets
    ports:
      - "8002:8000"
    restart: unless-stopped
```

**Iniciar todos os serviços:**

```bash
docker compose up --build
```

**Iniciar um serviço especifico:**

```bash
docker compose up cadastro
```

**Encerrar todos os serviços:**

```bash
docker compose down
```

---

## Licenca

Este projeto esta disponivel sob a licenca MIT.
