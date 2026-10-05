# 🔬 Projeto de Mineração de APIs Científicas

[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/tvlemes/projeto-data-engineer-articles/blob/main/LICENSE)
![S3](https://img.shields.io/badge/AWS-S3-blue?logo=s3)
![LocalStack](https://img.shields.io/badge/LocalStack-Running-green?logo=docker)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker)
![Airflow](https://img.shields.io/badge/Airflow-blue?logo=airflow)
[![Status](https://img.shields.io/badge/Status-Concluído-green.svg)]()


Pipeline de Engenharia de Dados desenvolvido para **coleta, normalização, armazenamento, transformação e análise de artigos científicos** provenientes de diferentes APIs acadêmicas.

O projeto utiliza uma arquitetura baseada em **Data Lake + Data Warehouse**, organizada nas camadas:

```text
                         ┌──────────────────────┐
                         │   APIs Científicas   │
                         │                      │
                         │ OpenAlex             │
                         │ CORE                 │
                         │ Crossref             │
                         │ Europe PMC           │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FASTAPI        │
                         │                      │
                         │ Pesquisa             │
                         │ Normalização         │
                         │ Validação            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       BRONZE         │
                         │                      │
                         │ LocalStack S3        │
                         │ Dados brutos         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       AIRFLOW        │
                         │                      │
                         │ Orquestração ETL     │
                         │ Agendamento          │
                         │ Controle             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       SILVER         │
                         │                      │
                         │ PostgreSQL           │
                         │ Dados normalizados   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │        GOLD          │
                         │                      │
                         │ PostgreSQL           │
                         │ Dados analíticos     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  GOLD SOURCE SUMMARY │
                         │                      │
                         │ Indicadores por      │
                         │ fonte científica     │
                         └──────────────────────┘
```

---

# 📚 Objetivo do Projeto

O objetivo é construir uma plataforma de Engenharia de Dados capaz de:

* Consultar diferentes APIs científicas.
* Normalizar dados provenientes de fontes diferentes.
* Armazenar os dados brutos em um Data Lake.
* Processar os dados utilizando ETL.
* Armazenar dados normalizados no PostgreSQL.
* Criar uma camada analítica Gold.
* Controlar as execuções dos pipelines.
* Evitar duplicidade de artigos.
* Criar estatísticas sobre os artigos coletados.
* Permitir futuras análises de dados e aplicações de Machine Learning/IA.

---

# 🏗️ Arquitetura do Projeto

A arquitetura segue o conceito:

```text
API
 │
 ▼
FASTAPI
 │
 ▼
BRONZE
 │
 │ LocalStack / S3
 ▼
AIRFLOW
 │
 ▼
SILVER
 │
 │ PostgreSQL
 ▼
GOLD
 │
 ▼
GOLD SOURCE SUMMARY
```

## Camadas

### 🥉 Bronze

A camada Bronze contém os dados **brutos**, preservando o máximo possível da resposta original das APIs.

Tecnologia:

* LocalStack
* Amazon S3 API

Exemplo de organização:

```text
scientific-articles/
│
├── bronze/
│   ├── openalex/
│   │   └── works/
│   │
│   ├── core/
│   │
│   ├── crossref/
│   │
│   └── europepmc/
```

---

### 🥈 Silver

A Silver contém os dados:

* normalizados;
* padronizados;
* tratados;
* estruturados;
* prontos para utilização analítica.

Tecnologia:

```text
PostgreSQL
```

Tabela principal:

```text
silver_articles
```

---

### 🥇 Gold

A camada Gold contém dados preparados para:

* análise;
* indicadores;
* BI;
* dashboards;
* relatórios;
* Machine Learning;
* aplicações de IA.

Tabela principal:

```text
gold_articles
```

---

# 🧩 Tecnologias Utilizadas

| Tecnologia     | Função                           |
| -------------- | -------------------------------- |
| Python         | Linguagem principal              |
| FastAPI        | API REST                         |
| Pydantic       | Validação e normalização         |
| PostgreSQL     | Banco de dados                   |
| LocalStack     | Simulação de AWS/S3              |
| S3             | Data Lake                        |
| Apache Airflow | Orquestração                     |
| Docker         | Containers                       |
| Docker Compose | Orquestração local               |
| pgAdmin        | Administração PostgreSQL         |
| SQL            | Transformação e consulta         |
| OpenAlex       | Artigos científicos              |
| CORE           | Artigos e documentos científicos |
| Crossref       | DOI e metadados                  |
| Europe PMC     | Artigos biomédicos               |

---

# 🌐 APIs Científicas

O projeto foi projetado para trabalhar com múltiplas fontes.

```text
/api/v1/articles
        │
        ├── OpenAlex
        │
        ├── Crossref
        │
        ├── CORE
        │
        └── Europe PMC
```

---

# 🔵 OpenAlex

O OpenAlex é uma das principais fontes utilizadas pelo projeto.

Ele fornece informações como:

* título;
* autores;
* resumo;
* DOI;
* ano de publicação;
* fonte;
* Open Access;
* URL do PDF;
* referências;
* citações.

## Endpoint oficial

Pesquisa por título:

```text
https://api.openalex.org/works?filter=title.search:{nome_título}
```

Pesquisa utilizando busca:

```text
https://api.openalex.org/works?search={nome_título}&per-page=20
```

Pesquisa por ano:

```text
https://api.openalex.org/works?search={nome_título}&filter=publication_year:{ano}
```

Pesquisa por DOI:

```text
https://api.openalex.org/works/https://doi.org/10.xxxx/xxxxx
```

---

# 🔵 Campos da OpenAlex

| Campo da aplicação | Campo OpenAlex                         |
| ------------------ | -------------------------------------- |
| `id`               | `id`                                   |
| `title`            | `title`                                |
| `authors`          | `authorships[].author.display_name`    |
| `abstract`         | `abstract_inverted_index`              |
| `publication_year` | `publication_year`                     |
| `doi`              | `doi`                                  |
| `source`           | `primary_location.source.display_name` |
| `pdf_url`          | `primary_location.pdf_url`             |
| `open_access`      | `open_access.is_oa`                    |

---

# 🧠 Normalização do Abstract

A OpenAlex pode retornar o resumo no formato:

```json
{
    "This": [0],
    "paper": [1],
    "presents": [2],
    "data": [3]
}
```

O projeto transforma esse formato em:

```text
This paper presents data
```

A função responsável por isso é:

```python
extract_abstract()
```

---

# 🔑 API Key OpenAlex

Quando utilizada no projeto, a chave da OpenAlex deve ser configurada através das variáveis de ambiente.

A chave pode ser obtida nas configurações da OpenAlex:

https://openalex.org/settings/api-key

> A validade e as regras de utilização da chave devem ser verificadas diretamente na documentação/configuração atual da OpenAlex.

Não coloque a chave diretamente no código-fonte.

Recomendação:

```env
OPENALEX_API_KEY=xxxxxxxxxxxxxxxx
```

E adicionar o `.env` ao `.gitignore`.

---

# 🚀 API Local — OpenAlex

A aplicação FastAPI disponibiliza os recursos de consulta e importação.

Exemplo:

```http
GET /api/v1/articles/
```

Fluxo:

```text
GET /api/v1/articles/
        │
        ▼
     OpenAlex
        │
        ▼
    Normalização
        │
        ▼
     Pydantic
        │
        ▼
      JSON
```

A consulta não deve ser confundida com a persistência.

---

# 💾 Importação dos artigos

Para o processo de ingestão/persistência:

```http
POST /api/v1/articles/import
```

Fluxo:

```text
POST /api/v1/articles/import
        │
        ▼
     OpenAlex
        │
        ▼
    Normalização
        │
        ▼
      Bronze
        │
        ▼
      Airflow
        │
        ▼
      Silver
        │
        ▼
       Gold
```

A persistência definitiva do pipeline deve ocorrer através do processo ETL, evitando que uma simples consulta à API gere registros duplicados no PostgreSQL.

---

# 🟣 CORE API

A CORE é utilizada para pesquisa de trabalhos científicos e documentos.

API:

```text
https://api.core.ac.uk/v3
```

## Pesquisa por título

```text
https://api.core.ac.uk/v3/search/works?q={nome_título}
```

## Limitar resultados

```text
https://api.core.ac.uk/v3/search/works?q={nome_título}&limit=20
```

## Paginação

```text
https://api.core.ac.uk/v3/search/works?q={nome_título}&limit=20&offset=20
```

## Pesquisa por frases

Exemplo:

```text
https://api.core.ac.uk/v3/search/works?q="data mining"
```

Outro exemplo:

```text
https://api.core.ac.uk/v3/search/works?q=mining AND "machine learning"
```

## API local

Pesquisa:

```text
GET /api/v1/core/works?q={nome_artigo}
```

Pesquisa por ID:

```text
GET /api/v1/core/works/{id}
```

Pesquisa de outputs:

```text
GET /api/v1/core/outputs?q={nome_artigo}
```

Download de output:

```text
GET /api/v1/core/outputs/{id}/download
```

Limite:

```text
GET /api/v1/core/works?q={nome_artigo}&limit={numero_artigos}
```

Limite + paginação:

```text
GET /api/v1/core/works?q={nome_artigo}&limit={numero_artigos}&offset={numero_da_pagina}
```

---

# 🟢 Crossref

A Crossref é especialmente importante para:

* DOI;
* metadados;
* títulos;
* autores;
* periódicos;
* publicação.

## Pesquisa geral

```text
https://api.crossref.org/works?query=mining
```

## Limitar resultados

```text
https://api.crossref.org/works?query=mining&rows=20
```

## Pesquisa por título

```text
https://api.crossref.org/works?query.title=mining
```

## Pesquisa por autor

```text
https://api.crossref.org/works?query.author=Smith
```

## Pesquisa por DOI

```text
https://api.crossref.org/works/10.xxxx/xxxxx
```

---

# 🗄️ PostgreSQL

Banco:

```text
scientific_articles
```

Usuário:

```text
articles_user
```

Porta do host:

```text
5434
```

Dentro do Docker:

```text
5432
```

---

# 🥈 Tabela Silver

A tabela principal da camada Silver é:

```text
silver_articles
```

Estrutura conceitual:

```text
silver_articles
│
├── id
├── source_api
├── external_id
├── doi
├── title
├── authors
├── abstract
├── publication_year
├── container_title
├── publisher
├── language
├── field_of_study
├── document_type
├── url
├── fulltext_urls
├── pdf_url
├── open_access
├── reference_count
├── is_referenced_by_count
├── created_at
└── updated_at
```

---

# 🔑 Identificação do artigo

A identificação lógica do artigo é baseada em:

```text
source_api
+
external_id
```

Exemplo:

```text
source_api = openalex
external_id = W123456789
```

Isso permite armazenar artigos provenientes de diferentes APIs sem depender exclusivamente do ID de uma única fonte.

---

# 🥇 Tabela Gold

A camada Gold possui os dados preparados para análise.

Conceitualmente:

```text
gold_articles
│
├── source
├── source_id
├── title
├── authors
├── abstract
├── publication_year
├── doi
├── source_name
├── pdf_url
├── open_access
├── author_count
├── abstract_length
├── has_doi
├── has_pdf
├── publication_decade
├── created_at
└── updated_at
```

> A Gold utiliza `source` e `source_id` como identificação da origem, enquanto a Silver utiliza `source_api` e `external_id`.

---

# 📊 Gold Source Summary

O projeto possui uma tabela derivada:

```text
gold_source_summary
```

Ela é alimentada **exclusivamente a partir da tabela `gold_articles`**.

O objetivo é gerar indicadores por fonte científica.

Exemplos de indicadores:

```text
total_articles
articles_with_doi
articles_with_pdf
articles_with_abstract
open_access_articles
total_authors
avg_author_count
avg_abstract_length
first_publication_year
last_publication_year
total_publication_decades
```

Fluxo:

```text
gold_articles
      │
      ▼
gold_source_summary
      │
      ├── quantidade de artigos
      ├── artigos com DOI
      ├── artigos com PDF
      ├── artigos Open Access
      ├── quantidade de autores
      ├── média de autores
      ├── tamanho médio dos abstracts
      └── período de publicação
```

---

# ⚙️ Airflow

O Apache Airflow é responsável pela orquestração dos processos ETL.

Principais DAGs:

```text
bronze_to_silver
        │
        ▼
silver_to_gold
        │
        ▼
gold_source_summary
```

---

# 🥉 Bronze → Silver

DAG:

```text
bronze_to_silver
```

Agendamento atual:

```text
*/5 * * * *
```

Ou seja:

```text
a cada 5 minutos
```

Fluxo:

```text
LocalStack S3
      │
      ▼
Bronze
      │
      ▼
service_etl.py
      │
      ▼
Normalização
      │
      ▼
silver_articles
```

---

# 🥈 Silver → Gold

DAG:

```text
silver_to_gold
```

Fluxo:

```text
silver_articles
      │
      ▼
service_gold_etl.py
      │
      ▼
Transformações
      │
      ▼
gold_articles
```

A transformação utiliza:

```text
source_api → source
external_id → source_id
```

---

# 📊 Gold Source Summary

DAG:

```text
gold_source_summary
```

Fluxo:

```text
gold_articles
      │
      ▼
service_gold_summary.py
      │
      ▼
gold_source_summary
```

---

# 📝 Controle dos ETLs

O projeto possui tabelas de controle para acompanhar as execuções dos pipelines.

---

## Bronze ETL Control

Tabela:

```text
bronze_etl_control
```

Pode ser utilizada para acompanhar a ingestão da camada Bronze.

---

## Silver ETL Control

Tabela:

```text
silver_etl_control
```

Estrutura:

```sql
CREATE TABLE IF NOT EXISTS silver_etl_control (
    id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    execution_id TEXT,
    status TEXT NOT NULL,
    source_api TEXT,
    records_read INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Gold ETL Control

Tabela:

```text
gold_etl_control
```

Estrutura:

```sql
CREATE TABLE IF NOT EXISTS gold_etl_control (
    id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    execution_id TEXT,
    status TEXT NOT NULL,
    source TEXT,
    records_read INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 🔄 Service de Controle ETL

Arquivo:

```text
app/services/service_etl_control.py
```

Responsabilidades:

```text
Criar execução
      │
      ▼
RUNNING
      │
      ▼
Executar ETL
      │
      ├── SUCCESS
      │
      └── FAILED
```

Informações controladas:

```text
execution_id
pipeline_name
status
source
records_read
records_inserted
records_updated
records_processed
records_failed
error_message
started_at
finished_at
```

---

# 📁 Estrutura do Projeto

Uma estrutura conceitual do projeto:

```text
projeto-data-engineer-articles-v2/
│
├── app/
│   │
│   ├── api/
│   │   └── routers/
│   │
│   ├── database/
│   │   ├── init_db.py
│   │   ├── create_silver.py
│   │   └── ...
│   │
│   ├── models/
│   │
│   ├── services/
│   │   ├── service_etl.py
│   │   ├── service_gold_etl.py
│   │   ├── service_gold_summary.py
│   │   └── service_etl_control.py
│   │
│   └── main.py
│
├── airflow/
|      └── dags/
|           ├── dag_bronze_silver.py
|           ├── dag_silver_gold.py
|           └── gold_source_summary.py
│
│
├── s3-explorer/
│
├── sql/
│
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# 🐳 Docker Compose

O projeto utiliza Docker Compose para executar toda a infraestrutura.

Principais serviços:

```text
scientific-articles-api
scientific-articles-localstack
scientific-articles-postgres
scientific-articles-airflow-webserver
scientific-articles-airflow-scheduler
scientific-articles-pgadmin
scientific-articles-s3-explorer
```

---

# 🌐 URLs e Portas

| Serviço     | URL                   |
| ----------- | --------------------- |
| FastAPI     | http://localhost:8000 |
| LocalStack  | http://localhost:4566 |
| pgAdmin     | http://localhost:5050 |
| Airflow     | http://localhost:8088 |
| S3 Explorer | http://localhost:8090 |
| PostgreSQL  | localhost:5434        |

---

# 🔎 FastAPI

A API pode ser acessada através de:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# 🪣 LocalStack

O LocalStack fornece uma implementação local das APIs da AWS.

Neste projeto é utilizado principalmente para:

```text
S3
```

Porta:

```text
4566
```

Arquitetura:

```text
FastAPI
   │
   ▼
LocalStack
   │
   ▼
S3
   │
   ▼
Bronze
```

---

# 🖥️ S3 Explorer

Interface web desenvolvida para visualizar o armazenamento S3.

Porta:

```text
8090
```

A interface permite trabalhar com:

* buckets;
* arquivos;
* JSON;
* Parquet;
* Excel;
* upload;
* download;
* visualização;
* atualização;
* exclusão.

A aplicação se conecta ao LocalStack através de:

```text
http://localstack:4566
```

---

# 🛠️ Comandos Úteis

## 1. Adicionar `source_api` e `external_id` na Silver

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "ALTER TABLE silver_articles ADD COLUMN IF NOT EXISTS source_api TEXT; ALTER TABLE silver_articles ADD COLUMN IF NOT EXISTS external_id TEXT;"
```

Adiciona as colunas:

```text
source_api
external_id
```

caso elas ainda não existam.

---

## 2. Preencher as novas colunas da Silver

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "UPDATE silver_articles SET source_api = 'openalex', external_id = openalex_id WHERE source_api IS NULL;"
```

Migra registros antigos que possuem:

```text
openalex_id
```

para:

```text
source_api = openalex
external_id = openalex_id
```

> Esse comando é apropriado para registros antigos originados da OpenAlex.

---

## 3. Verificar os dados da Silver

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "SELECT id, openalex_id, source_api, external_id, title FROM silver_articles LIMIT 10;"
```

Permite verificar se a migração dos campos foi realizada corretamente.

---

## 4. Criar chave única

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "ALTER TABLE silver_articles ADD CONSTRAINT uq_silver_source_external UNIQUE (source_api, external_id);"
```

Cria uma restrição de unicidade para:

```text
source_api + external_id
```

Isso ajuda a impedir artigos duplicados da mesma fonte.

> Se a tabela já possuir essa constraint, o comando apresentará erro. Nesse caso, verifique as constraints existentes antes de executar novamente.

---

# 🏗️ Criar as tabelas pelo Python

```powershell
docker compose exec api python -c "from app.database.init_db import create_tables; create_tables()"
```

Executa a função:

```python
create_tables()
```

dentro do container da API.

A função é responsável pela inicialização das estruturas de banco definidas pelo projeto.

---

# 🥈 Criar a tabela Silver

```powershell
docker compose exec api python -c "from app.database.create_silver import create_silver_table; create_silver_table()"
```

Executa especificamente a criação/inicialização da tabela:

```text
silver_articles
```

---

# 📋 Listar todas as tabelas

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\dt"
```

Lista as tabelas existentes no banco:

```text
scientific_articles
```

---

# 🔍 Ver estrutura da Bronze Control

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d bronze_etl_control"
```

Mostra:

* colunas;
* tipos;
* constraints;
* índices;
* estrutura da tabela.

---

# 🔍 Ver estrutura da Silver Control

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d silver_etl_control"
```

---

# 🔍 Ver estrutura da Gold Control

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d gold_etl_control"
```

---

# 🔍 Ver estrutura da Silver

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d silver_articles"
```

---

# 🔍 Ver estrutura da Gold

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d gold_articles"
```

---

# 🔍 Ver estrutura do Gold Summary

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d gold_source_summary"
```

---

# 🧪 Validar banco através do Python

```powershell
docker compose exec api python -m app.database.init_db
```

Executa o módulo:

```text
app.database.init_db
```

---

# 🧪 Testar a DAG manualmente

Para executar uma DAG diretamente pelo scheduler:

```powershell
docker compose exec airflow-scheduler airflow dags test gold_source_summary 2026-10-05
```

Esse comando executa a DAG:

```text
gold_source_summary
```

para a data:

```text
2026-10-05
```

É especialmente útil para testar uma DAG sem esperar o agendamento automático do Airflow.

---

# 🧪 Testar outras DAGs

Bronze → Silver:

```powershell
docker compose exec airflow-scheduler airflow dags test bronze_to_silver 2026-10-05
```

Silver → Gold:

```powershell
docker compose exec airflow-scheduler airflow dags test silver_to_gold 2026-10-05
```

Gold Source Summary:

```powershell
docker compose exec airflow-scheduler airflow dags test gold_source_summary 2026-10-05
```

---

# 🗃️ SQL — Índices

Índice para ano de publicação:

```sql
CREATE INDEX IF NOT EXISTS idx_silver_articles_year
ON silver_articles(publication_year);
```

Índice para DOI:

```sql
CREATE INDEX IF NOT EXISTS idx_silver_articles_doi
ON silver_articles(doi);
```

Índice para origem da API:

```sql
CREATE INDEX IF NOT EXISTS idx_silver_articles_source_api
ON silver_articles(source_api);
```

> Na Silver atual, utilize `source_api`. O campo `source` pertence à modelagem da Gold e não deve ser utilizado para criar um índice na `silver_articles` atual.

---

# 🧱 SQL — Migração da Silver

Adicionar `source_api`:

```sql
ALTER TABLE silver_articles
ADD COLUMN IF NOT EXISTS source_api TEXT;
```

Adicionar `external_id`:

```sql
ALTER TABLE silver_articles
ADD COLUMN IF NOT EXISTS external_id TEXT;
```

Migrar registros antigos da OpenAlex:

```sql
UPDATE silver_articles
SET
    source_api = 'openalex',
    external_id = openalex_id
WHERE source_api IS NULL;
```

Criar unicidade:

```sql
ALTER TABLE silver_articles
ADD CONSTRAINT uq_silver_source_external
UNIQUE (source_api, external_id);
```

---

# 📊 Consultas úteis

## Ver artigos da Silver

```sql
SELECT
    id,
    source_api,
    external_id,
    title,
    publication_year,
    doi
FROM silver_articles
LIMIT 20;
```

## Ver artigos da Gold

```sql
SELECT
    source,
    source_id,
    title,
    publication_year,
    doi,
    open_access
FROM gold_articles
LIMIT 20;
```

## Quantidade de artigos por fonte

```sql
SELECT
    source,
    COUNT(*) AS total_articles
FROM gold_articles
GROUP BY source
ORDER BY total_articles DESC;
```

## Ver resumo por fonte

```sql
SELECT *
FROM gold_source_summary
ORDER BY total_articles DESC;
```

---

# 🔐 Variáveis de Ambiente

Exemplo:

```env
POSTGRES_DB=scientific_articles
POSTGRES_USER=articles_user
POSTGRES_PASSWORD=********

OPENALEX_API_KEY=********

S3_ENDPOINT_URL=http://localstack:4566
S3_BUCKET=scientific-articles
```

Nunca versionar:

```text
.env
```

Adicionar ao:

```text
.gitignore
```

Exemplo:

```gitignore
.env
__pycache__/
*.pyc
.venv/
.vscode/
.idea/
```

---

# 🔄 Fluxo Completo do Pipeline

O fluxo completo do projeto é:

```text
                    APIs
                     │
        ┌────────────┼─────────────┐
        │            │             │
     OpenAlex       CORE        Crossref
        │            │             │
        └────────────┼─────────────┘
                     │
                     ▼
                  FastAPI
                     │
                     ▼
                Normalização
                     │
                     ▼
                  BRONZE
                     │
                     ▼
              LocalStack / S3
                     │
                     ▼
                  Airflow
                     │
                     ▼
              bronze_to_silver
                     │
                     ▼
                  SILVER
                     │
                     ▼
             PostgreSQL
                     │
                     ▼
               silver_to_gold
                     │
                     ▼
                   GOLD
                     │
                     ▼
             gold_source_summary
                     │
                     ▼
             Indicadores / BI
```

---

# 🔁 Estratégia de ETL

## Extract

Coleta os dados das APIs:

```text
OpenAlex
CORE
Crossref
Europe PMC
```

---

## Load — Bronze

Os dados brutos são armazenados no S3 através do LocalStack.

```text
API
 ↓
JSON bruto
 ↓
S3
```

---

## Transform — Silver

O Airflow lê os dados Bronze e executa:

```text
Leitura
   ↓
Validação
   ↓
Normalização
   ↓
Padronização
   ↓
Deduplicação
   ↓
PostgreSQL
```

---

## Transform — Gold

A Silver é transformada em dados analíticos:

```text
Silver
  ↓
Cálculos
  ↓
Indicadores
  ↓
Gold
```

Exemplos:

```text
author_count
abstract_length
has_doi
has_pdf
publication_decade
```

---

# 🧭 Controle de Execução

Cada etapa pode registrar:

```text
RUNNING
   │
   ├── SUCCESS
   │
   └── FAILED
```

Informações registradas:

```text
pipeline_name
execution_id
status
records_read
records_inserted
records_updated
records_processed
records_failed
error_message
started_at
finished_at
```

Isso permite acompanhar a execução dos pipelines e facilitar o diagnóstico de problemas.

---

# 🛡️ Deduplicação

A deduplicação utiliza a combinação:

```text
source_api
+
external_id
```

Exemplo:

```text
openalex + W123456789
```

Outro artigo:

```text
crossref + 10.1234/example
```

Dessa maneira, diferentes APIs podem possuir identificadores diferentes sem que o modelo dependa exclusivamente da OpenAlex.

---

# 📈 Possibilidades Futuras

O projeto pode evoluir para:

* Dashboard Power BI;
* Grafana;
* Apache Superset;
* análise de citações;
* análise de autores;
* análise de periódicos;
* recomendação de artigos;
* classificação automática;
* embeddings;
* busca semântica;
* RAG;
* LLM;
* Vector Database;
* Elasticsearch/OpenSearch;
* Spark;
* Databricks;
* processamento distribuído;
* Kubernetes;
* deploy em AWS/GCP/Azure.

---

# 🧠 Possível arquitetura futura com IA

```text
                 Artigos Científicos
                         │
                         ▼
                    PostgreSQL
                         │
                         ▼
                    Embeddings
                         │
                         ▼
                  Vector Database
                         │
                         ▼
                       RAG
                         │
                         ▼
                       LLM
                         │
                         ▼
                Assistente Científico
```

---

# 🚀 Inicialização do Projeto

Subir os containers:

```powershell
docker compose up -d
```

Verificar os containers:

```powershell
docker compose ps
```

Ver logs:

```powershell
docker compose logs -f
```

Logs da API:

```powershell
docker compose logs -f api
```

Logs do PostgreSQL:

```powershell
docker compose logs -f postgres
```

Logs do Airflow:

```powershell
docker compose logs -f airflow-scheduler
```

---

# 🛑 Parar o Projeto

```powershell
docker compose down
```

---

# 🔄 Recriar os Containers

```powershell
docker compose down
docker compose up -d --build
```

---

# 🧹 Recriar Containers

```powershell
docker compose down
docker compose build --no-cache
docker compose up -d
```

> Utilize `--no-cache` quando for necessário garantir que a imagem seja reconstruída sem utilizar as camadas de cache anteriores.

---

# 📋 Verificar os Containers

```powershell
docker compose ps
```

Exemplo esperado:

```text
scientific-articles-api
scientific-articles-localstack
scientific-articles-postgres
scientific-articles-airflow-webserver
airflow-scheduler
scientific-articles-pgadmin
scientific-articles-s3-explorer
```

---

# 🔍 Verificar as Tabelas do PostgreSQL

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\dt"
```

Principais tabelas esperadas:

```text
silver_articles
gold_articles
gold_source_summary
bronze_etl_control
silver_etl_control
gold_etl_control
```

---

# 🧪 Checklist de Diagnóstico

Quando ocorrer algum erro no ETL, verificar nesta ordem:

```text
1. Containers
       ↓
2. PostgreSQL
       ↓
3. Tabelas
       ↓
4. Estrutura das tabelas
       ↓
5. Dados Silver
       ↓
6. Dados Gold
       ↓
7. Airflow DAG
       ↓
8. Logs
```

Primeiro:

```powershell
docker compose ps
```

Depois:

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\dt"
```

Ver Silver:

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d silver_articles"
```

Ver Gold:

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d gold_articles"
```

Ver controles:

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d silver_etl_control"
```

```powershell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d gold_etl_control"
```

---

# 📌 Resumo da Arquitetura

```text
┌─────────────────────────────────────────────────────────┐
│                  APIs CIENTÍFICAS                       │
│                                                         │
│ OpenAlex │ CORE │ Crossref │ Europe PMC                │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                       FASTAPI                           │
│                                                         │
│ Consulta │ Normalização │ Validação │ Importação       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                     BRONZE                              │
│                                                         │
│              LocalStack / S3                            │
│                 Dados brutos                            │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    APACHE AIRFLOW                       │
│                                                         │
│            Orquestração dos ETLs                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                     SILVER                              │
│                                                         │
│                 PostgreSQL                              │
│             Dados normalizados                          │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      GOLD                               │
│                                                         │
│                 PostgreSQL                              │
│              Dados analíticos                           │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│               GOLD SOURCE SUMMARY                       │
│                                                         │
│       Indicadores e estatísticas por fonte              │
└─────────────────────────────────────────────────────────┘
```

---

# 👨‍💻 Autor

**Thiago Vilarinho Lemes**
👤 Autor: Thiago Vilarinho Lemes <br>
💻 Engenheiro e Analista de Dados.\
🏠 Home: https://thiagolemes.netlify.app/ \
🔗 LinkedIn: <a href="https://www.linkedin.com/in/thiago-v-lemes-b1232727" target="_blank">Thiago Lemes</a><br>
✉️ e-mail:contatothiagolemes@gmail.com | lemes_vilarinho@yahoo.com.br


Principais áreas:

```text
Data Engineering
Docker
Kafka
Python
SQL
Apache Airflow
Docker
PostgreSQL
Data Lake
ETL
APIs
Cloud
IoT
Machine Learning
Generative AI
```

---

# 📜 Licença

Este projeto é destinado a estudos, experimentação e desenvolvimento de soluções de Engenharia de Dados utilizando APIs científicas e tecnologias open source.

<a href="LICENSE">LICENSE MIT</a>
