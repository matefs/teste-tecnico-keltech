# PROJECT ARCHITECTURE & RULES (MVP)

## 1. FILE HEADER PROTOCOL
# Arquivo: [caminho/completo/do/arquivo]
# Regra: Sem comentários inline.

## 2. DIRECTORY STRUCTURE (MODULAR MONOLITH)
/src
  /config          # Configurações globais (env, constants)
  /infrastructure  # Detalhes técnicos (Database, Libs, Mailer)
  /modules         # DOMÍNIOS DO NEGÓCIO (Screaming Architecture)
    /[module_name]
      module_router.py        # Definição de endpoints (FastAPI APIRouter)
      module_controller.py    # Orquestração de entrada (dependências, respostas HTTP)
      module_service.py       # Regras de Negócio (Core)
      module_repository.py    # Abstração de dados (SQL/ORM)
      module_schemas.py       # Modelos Pydantic (validação, serialização e tipos)
  /shared          # Utils, Middlewares globais, Erros padrão
/docs
  /rfcs            # Decisões arquiteturais e requisitos de módulos

## 3. CODING PRINCIPLES (MANDATORY)

### A. Clean Code & Naming
- **Nomes Extremamente Descritivos:** Variáveis, funções e classes devem dizer exatamente o que fazem.
  - Ruim: `d = datetime.now()` | Bom: `creation_date = datetime.now()`
  - Ruim: `def handle(u): ...` | Bom: `async def create_user_account(user_data: UserCreate): ...`
- **Funções Pequenas:** Uma função deve ter apenas uma responsabilidade (Single Responsibility Principle).
- **snake_case** para variáveis e funções; **PascalCase** para classes e schemas Pydantic.

### B. Design Patterns & Architecture
- **Dependency Injection:** Use `Depends()` do FastAPI para injetar repositórios e serviços nos endpoints.
- **Repository Pattern:** O Service não sabe qual banco de dados estamos usando. Ele conversa com a interface do Repository.
- **Fail Fast:** Valide inputs com Pydantic no início do fluxo. Lance `HTTPException` cedo com status codes corretos.
- **Early Returns:** Evite `if/else` aninhados. Use retornos antecipados para limpar o fluxo lógico.

### C. SQL & Persistence
- Relacional puro com SQLAlchemy (Core ou ORM) ou Query Builder equivalente.
- Todos os schemas de entrada e saída devem ser validados via Pydantic antes de atingir o banco.
- Migrations são obrigatórias para qualquer alteração de schema (Alembic).

### D. Tipagem
- Use type hints em todas as funções e métodos (parâmetros e retorno).
- Nunca use `Any` sem justificativa explícita.
- Modelos de request/response devem ser classes `BaseModel` do Pydantic.

## 4. IA INTERACTION RULES
- Antes de escrever código, leia o RFC correspondente em `/docs/rfcs`.
- Mantenha a separação de camadas: Router (HTTP) -> Controller (entrada) -> Service (negócio) -> Repository (dados).
- Use `async def` em endpoints e operações de I/O.

## 5. Contexto de Negócio
Uma empresa do setor de gestão documental precisa automatizar a entrada e classificação de documentos enviados por seus clientes. Hoje, esses documentos chegam em formato digitalizado (PDF ou imagem PNG) e precisam ser processados manualmente — uma pessoa abre o arquivo, identifica campos, digita as informações em uma planilha e cruza com um arquivo XML de referência enviado pelo cliente em momento posterior.
O objetivo do sistema é eliminar essa etapa manual. Os documentos devem ser carregados, processados automaticamente, enriquecidos com os dados do XML correspondente e disponibilizados para consulta e relatório quantitativo.

## 5.1. Personas
Operador: faz o upload dos documentos individualmente ou em lote, acompanha o status do processamento e corrige eventuais erros.
Gestor: consulta os relatórios consolidados, acompanha quantitativos por período, tipo de documento e cliente.
Administrador: gerencia usuários e tem acesso aos logs do sistema.
