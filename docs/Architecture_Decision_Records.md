
# ADR 001: Unificação da Camada de Persistência (PostgreSQL)
Contexto: O diagrama original propunha múltiplos bancos de dados para separar metadados, registros de usuários e logs. A volumetria estimada é de 5.000 documentos/dia com arquivos de até 25MB.

Decisão: Utilizaremos exclusivamente o PostgreSQL como banco de dados relacional e documental.

Alternativas: MongoDB para metadados (rejeitado por redundância) e Redis para filas (rejeitado para simplificar a stack inicial).

Consequências: Simplificação drástica do ambiente Docker, garantia de transações ACID em todo o fluxo de processamento e redução do consumo de memória RAM.

# ADR 002: Armazenamento de Metadados via JSONB
Contexto: Documentos processados possuem campos variáveis extraídos pelo OCR e enriquecidos pelo XML.

Decisão: Usar o tipo de dado JSONB do PostgreSQL para armazenar os campos identificados e os dados do XML.

Alternativas: Criar tabelas altamente normalizadas para cada tipo de documento (rejeitado por falta de flexibilidade no MVP).

Consequências: Flexibilidade de esquema (NoSQL-like) dentro de um ambiente SQL robusto, permitindo consultas complexas sem migrações constantes de schema.

# ADR 003: Estratégia de Armazenamento de Binários (FileSystem vs Blob)
Contexto: Arquivos de até 25MB precisam ser retidos.

Decisão: O banco de dados armazenará apenas os metadados e o path do arquivo. O binário bruto será salvo no File System (Volume Docker).

Alternativas: Salvar como BYTEA no Postgres (rejeitado: inflaria o backup e degradaria performance).

Consequências: Alta performance de I/O e facilidade de backup dos metadados.
