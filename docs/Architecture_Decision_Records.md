# ADR 000: Arquitetura Orientada a Eventos (Producer-Consumer)

**Contexto**
O design inicial previa acoplamento direto entre serviços, onde um componente dependia da disponibilidade imediata de outro para completar a operação. Isso geraria gargalos em processos intensivos como OCR e importação de XML.

**Decisão**
Adotaremos uma arquitetura de serviços desacoplados por filas. Cada domínio (Upload, XML, OCR) será segregado. Para garantir o isolamento de recursos no Docker, cada serviço operará com duas especializações de instância:
* **Enfileirador (Producer):** Responsável por receber a requisição, validar e postar a tarefa na fila.
* **Consumidor (Worker):** Responsável pelo processamento pesado e execução da lógica de negócio.

**Alternativas**
* **Monolito ou Processamento Síncrono:** Executar todas as etapas na mesma instância. Rejeitado devido ao risco de um processo pesado (OCR) derrubar o recebimento de novos uploads.

**Consequências**
* **Escalabilidade Granular:** Possibilidade de escalar apenas os Workers de OCR sem aumentar a memória do serviço de Upload.
* **Resiliência:** Se o consumidor falhar, as tarefas permanecem seguras na fila para reprocessamento.


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
