# 🛠 PROJECT ARCHITECTURE & RULES (MVP)

## 1. FILE HEADER PROTOCOL
// Arquivo: [caminho/completo/do/arquivo]
// Regra: Sem comentários inline. Apenas este comentário no topo.

## 2. DIRECTORY STRUCTURE (MODULAR MONOLITH)
/src
  /config          # Configurações globais (env, constants)
  /infrastructure  # Detalhes técnicos (Database, Libs, Mailer)
  /modules         # DOMÍNIOS DO NEGÓCIO (Screaming Architecture)
    /[module-name]
      [module].controller.ts  # Orquestração de entrada
      [module].service.ts     # Regras de Negócio (Core)
      [module].routes.ts      # Definição de endpoints
      [module].repository.ts  # Abstração de dados (SQL/ORM)
      [module].schema.ts      # Validações (Zod/Joi) e Tipos
  /shared          # Utils, Middlewares globais, Erros padrão
/docs
  /rfcs            # Decisões arquiteturais e requisitos de módulos

## 3. CODING PRINCIPLES (MANDATORY)

### A. Clean Code & Naming
- **Nomes Extremamente Descritivos:** Variáveis, funções e classes devem dizer exatamente o que fazem.
  - Ruim: `const d = new Date();` | Bom: `const creationDate = new Date();`
  - Ruim: `function handle(u) {}` | Bom: `async function createUserAccount(userData) {}`
- **Funções Pequenas:** Uma função deve ter apenas uma responsabilidade (Single Responsibility Principle).

### B. Design Patterns & Architecture
- **Dependency Injection:** Services não devem instanciar suas dependências. Receba-as via construtor ou parâmetros.
- **Repository Pattern:** O Service não sabe qual banco de dados estamos usando. Ele conversa com a interface do Repository.
- **Fail Fast:** Valide inputs no início da função. Lance erros cedo (Error Handling robusto).
- **Early Returns:** Evite `if/else` aninhados. Use retornos antecipados para limpar o fluxo lógico.

### C. SQL & Persistence
- Relacional puro ou Query Builder (Knex/Drizzle/Prisma).
- Esquemas devem ser validados antes de atingir o banco.
- Migrations são obrigatórias para qualquer alteração de schema.

## 4. IA INTERACTION RULES
- Antes de escrever código, leia o RFC correspondente em `/docs/rfcs`.
- Siga estritamente a tipagem do TypeScript. Não use `any`.
- Mantenha a separação de camadas: Controller (HTTP) -> Service (Business) -> Repository (Data).

## 2. Contexto de Negócio
Uma empresa do setor de gestão documental precisa automatizar a entrada e classificação de documentos enviados por seus clientes. Hoje, esses documentos chegam em formato digitalizado (PDF ou imagem PNG) e precisam ser processados manualmente — uma pessoa abre o arquivo, identifica campos, digita as informações em uma planilha e cruza com um arquivo XML de referência enviado pelo cliente em momento posterior.
O objetivo do sistema é eliminar essa etapa manual. Os documentos devem ser carregados, processados automaticamente, enriquecidos com os dados do XML correspondente e disponibilizados para consulta e relatório quantitativo.

## 2.1. Personas
Operador: faz o upload dos documentos individualmente ou em lote, acompanha o status do processamento e corrige eventuais erros.
Gestor: consulta os relatórios consolidados, acompanha quantitativos por período, tipo de documento e cliente.
Administrador: gerencia usuários e tem acesso aos logs do sistema.
