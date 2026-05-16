# Keltech — Sistema de Gestão Documental

API para automação de entrada, classificação e processamento de documentos digitalizados (PDF/PNG), com enriquecimento via XML e geração de relatórios quantitativos.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Stack](#stack)
- [Decisões Arquiteturais (ADRs)](#decisões-arquiteturais-adrs)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Rodando o Projeto](#rodando-o-projeto)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Fila: Documentos\_para\_OCR](#fila-documentos_para_ocr)

---

## Visão Geral

O sistema elimina o processamento manual de documentos. O fluxo principal é:

```
Upload (PDF/PNG)
      │
      ▼
  API REST  ──► publica na fila "Documentos_para_OCR"
                        │
                        ▼
               Consumer (aio-pika)
                        │
                        ▼
               OCR + extração de campos
                        │
                        ▼
             Persistência no PostgreSQL
                        │
                        ▼
         Enriquecimento com XML do cliente
                        │
                        ▼
          Disponível para consulta / relatório
```

---

## Stack

| Camada         | Tecnologia                        |
|----------------|-----------------------------------|
| API            | FastAPI 0.115 + Uvicorn 0.34      |
| Banco          | PostgreSQL 16 + SQLAlchemy 2 async|
| Migrations     | Alembic 1.15                      |
| Fila           | RabbitMQ 3.13 + aio-pika 9.5      |
| Validação      | Pydantic v2 + pydantic-settings   |
| Linting        | Ruff                              |
| Testes         | pytest + pytest-asyncio + httpx   |
| Gerenciador    | uv                                |
| Containers     | Docker + Docker Compose           |

---

## Decisões Arquiteturais (ADRs)

As decisões técnicas relevantes do projeto estão documentadas em [`docs/Architecture_Decision_Records.md`](docs/Architecture_Decision_Records.md).

| ADR | Decisão |
|-----|---------|
| 001 | Unificação da camada de persistência no PostgreSQL |
| 002 | Armazenamento de metadados variáveis via JSONB |
| 003 | Binários salvos no File System (Volume Docker), apenas path no banco |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) >= 24
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20
- [uv](https://docs.astral.sh/uv/getting-started/installation/) >= 0.5 (para desenvolvimento local sem Docker)
- Python 3.12+ (gerenciado automaticamente pelo uv)

---

## Instalação

### Com Docker (recomendado)

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd teste-tecnico-keltech

# 2. Copie e ajuste as variáveis de ambiente
cp .env.example .env
# edite .env conforme necessário

# 3. Suba todos os serviços
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.  
A documentação interativa (Swagger) estará em `http://localhost:8000/docs`.

### Sem Docker (desenvolvimento local)

```bash
# 1. Instale o uv (caso não tenha)
curl -LsSf https://astral.sh/uv/install.sh | sh   # Linux/Mac
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 2. Instale as dependências (cria .venv automaticamente)
uv sync

# 3. Copie e ajuste as variáveis de ambiente
cp .env.example .env
# Aponte DB_HOST=localhost e RABBITMQ_HOST=localhost

# 4. Suba apenas a infraestrutura
docker compose up db rabbitmq -d

# 5. Rode a aplicação
uv run uvicorn src.main:app --reload
```

#### Comandos úteis com uv

```bash
# Adicionar uma dependência
uv add <pacote>

# Adicionar dependência de desenvolvimento
uv add --dev <pacote>

# Atualizar todas as dependências
uv lock --upgrade

# Rodar qualquer comando no ambiente virtual
uv run <comando>

# Gerar requirements.txt a partir do lock file
uv export --no-dev -o requirements.txt
```

---

## Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha os valores.

| Variável            | Descrição                                       | Padrão       |
|---------------------|-------------------------------------------------|--------------|
| `APP_ENV`           | Ambiente (`development` / `production`)         | `development`|
| `APP_HOST`          | Host de bind da API                             | `0.0.0.0`    |
| `APP_PORT`          | Porta da API                                    | `8000`       |
| `SECRET_KEY`        | Chave para assinatura de tokens                 | —            |
| `DATABASE_URL`      | DSN completo do PostgreSQL (asyncpg)            | —            |
| `DB_USER`           | Usuário do banco                                | `keltech`    |
| `DB_PASSWORD`       | Senha do banco                                  | —            |
| `DB_NAME`           | Nome do banco                                   | `keltech`    |
| `DB_HOST`           | Host do banco                                   | `db`         |
| `DB_PORT`           | Porta do banco                                  | `5432`       |
| `RABBITMQ_URL`      | DSN completo do RabbitMQ (AMQP)                 | —            |
| `RABBITMQ_USER`     | Usuário do RabbitMQ                             | `keltech`    |
| `RABBITMQ_PASSWORD` | Senha do RabbitMQ                               | —            |
| `RABBITMQ_HOST`     | Host do RabbitMQ                                | `rabbitmq`   |
| `RABBITMQ_PORT`     | Porta AMQP                                      | `5672`       |

> Para gerar um `SECRET_KEY` seguro: `openssl rand -hex 32`

---

## Rodando o Projeto

```bash
# Subir tudo
docker compose up --build

# Subir em background
docker compose up --build -d

# Ver logs de um serviço específico
docker compose logs -f app
docker compose logs -f rabbitmq

# Derrubar tudo (mantém volumes)
docker compose down

# Derrubar tudo e apagar volumes (reseta banco e fila)
docker compose down -v
```

### Verificar saúde

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### RabbitMQ Management UI

Acesse `http://localhost:15672` com as credenciais definidas em `.env` (`keltech` / `keltech` por padrão).

---

## Estrutura de Pastas

```
src/
├── config/
│   └── settings.py              # Configurações via pydantic-settings
├── infrastructure/
│   └── rabbitmq/
│       ├── connection.py        # Conexão singleton com RabbitMQ (aio-pika)
│       ├── publisher.py         # Publica mensagens na fila
│       └── consumer.py          # Consome e processa mensagens
├── modules/                     # Domínios de negócio (Screaming Architecture)
│   └── [modulo]/
│       ├── module_router.py
│       ├── module_controller.py
│       ├── module_service.py
│       ├── module_repository.py
│       └── module_schemas.py
├── shared/                      # Utils, middlewares e erros padrão
└── main.py                      # Entry point — lifespan, health check e routers
docs/
├── Architecture_Decision_Records.md   # ADRs do projeto
├── Architecture_Decision_Records_DIAGRAM.png
├── diagrama_arquitetura.pdf
└── Desafio_Tecnico_Candidatos.docx
```

---

## Fila: Documentos\_para\_OCR

### Visão geral

A fila `Documentos_para_OCR` desacopla o upload do processamento OCR. Quando um documento é recebido pela API, uma mensagem é enfileirada imediatamente e a resposta HTTP retorna sem aguardar o processamento.

```
POST /documentos  ──►  publish_document_for_ocr()  ──►  [Documentos_para_OCR]
                                                                  │
                                                    start_ocr_consumer() (lifespan)
                                                                  │
                                                         _process_ocr_message()
```

### Configuração da fila

| Propriedade      | Valor                  |
|------------------|------------------------|
| Nome             | `Documentos_para_OCR`  |
| Durável          | Sim                    |
| Delivery mode    | Persistent             |
| Prefetch count   | 10                     |
| Requeue on error | Sim                    |

### Formato da mensagem

```json
{
  "document_id": "uuid-v4",
  "file_path": "uploads/2026/05/documento.pdf",
  "mime_type": "application/pdf"
}
```

### Publicando uma mensagem (publisher)

```python
from src.infrastructure.rabbitmq.publisher import publish_document_for_ocr

await publish_document_for_ocr(
    document_id=document.id,
    file_path="uploads/2026/05/documento.pdf",
    mime_type="application/pdf",
)
```

### Consumidor

O consumer é iniciado automaticamente no lifespan do FastAPI (`src/main.py`). Ele escuta a fila continuamente e chama `_process_ocr_message()` para cada mensagem.

- Se o processamento **suceder** → mensagem é removida da fila (ack via `message.process()`)
- Se o processamento **falhar** → mensagem é devolvida à fila (`requeue=True`)

Para integrar o OCR service, edite `src/infrastructure/rabbitmq/consumer.py` no bloco `TODO`:

```python
# consumer.py
await ocr_service.process(document_id, file_path, mime_type)
```
