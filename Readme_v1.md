# Projeto de Mineração de API´s

## API´s utilizadas:
Modelo da estrutura da API:
```
/api/v1/articles
        │
        ├── OpenAlex
        ├── Crossref
        ├── CORE
        └── Europe PMC
```
---

## Esboço dos campos do Postgres:
```
id
title
authors
abstract
publication_year
doi
source
pdf_url
open_access
```
---

## API´s e seus respctivos Endpoints:

1. **OpenAlex**
```html
# Pesquisa por artigo:
* https://api.openalex.org/works?filter=title.search:{nome_título}

# Limitar pesquisa:
* https://api.openalex.org/works?search={nome_título}&per-page=20

# Pesquisa por ano:
*https://api.openalex.org/works?search={nome_título}&filter=publication_year:{ano}

# Pesquisa por DOI:
* https://api.openalex.org/works/https://doi.org/10.xxxx/xxxxx
```

2. **CORE API**
```html
# Pesquisa por título:
* https://api.core.ac.uk/v3/search/works?q={nome_título}

# Limitar pesquisa:
* https://api.core.ac.uk/v3/search/works?q={nome_título}&limit=20

# Paginação:
* https://api.core.ac.uk/v3/search/works?q={nome_título}&limit=20&offset=20

# Pesquisa por frases, textos e operadores:
* https://api.core.ac.uk/v3/search/works?q="data mining" 

e

https://api.core.ac.uk/v3/search/works?q=mining AND machine learning
```

3. **Crossref** — excelente para DOI e metadados
```html
# Pesquisa por artigo:
* https://api.crossref.org/works?query={nome_artigo} 

# Limitar pesquisa:
* https://api.crossref.org/works?query=mining&rows=20 

# Pesquisa por título:
* https://api.crossref.org/works?query.title=mining 

# Pesquisa por autor:
* https://api.crossref.org/works?query.author={nome_autor}

# Pesquisa por DOI
* https://api.crossref.org/works/10.xxxx/xxxxx 
```

4. **Europe PMC** - excelente para artigos biomédicos
```html
# Pesquisa por artigo:
*https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={nome_artigo}&format=json 

# Limitar pesquisa:
*https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={nome_artigo}&pageSize=20&format=json 

# Pesquisa por autor:
* https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=AUTHOR:{nome_autor}&format=json

# Pesquisa pelo DOI:
*  https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.xxxx/xxxxx&format=json 
```
---

## Criando a API da OpenAlex

1. De onde cada campo vem no OpenAlex

Seu campo |             OpenAlex
|---|---|
id |              id
title |             title
authors |            authorships[].author.display_name
abstract |           abstract_inverted_index
publication_year |       publication_year
doi |                   doi
source |                 primary_location.source.display_name
pdf_url |               primary_location.pdf_url
open_access |           open_access.is_oa
---

## Estrutura de pesquisa na OpenAlex
```
FastAPI
   ↓
OpenAlex
   ↓
API Key <- é uma key temporária
   ↓
Busca por artigos
   ↓
Normalização
   ↓
Pydantic
   ↓
JSON da sua API
```

**OBS**.: a API Key é uma chave temporária valida por 7 dias, para renovar a chave acesse https://openalex.org/settings/api-key 
tem que estar logado no site. 

**Endpoints da OpenAlex**: 

```html
1. Pesquisa por artigo:
* http://localhost:8000/api/v1/openalex/?query={nome_artigo}&limit={limite_de_artigos} 

2. Pesquisa por paginação
* http://localhost:8000/api/v1/openalex/?query={nome_artigo}&page={numero_da_pagina}&per_page={limite_de_artigos}

3. Pesquisar por ano
* http://localhost:8000/api/v1/openalex/?query={nome_artigo}&year={ano_publicado}

4. Somente Open Access
* http://localhost:8000/api/v1/openalex/?query={nome_artigo}&open_access={verdadeiro_ou_falso}

5. Ano + Open Access
* http://localhost:8000/api/v1/openalex/?query={nome_artigo}&year={ano_publicado}&open_access={verdadeiro_falso}
```

Altere em *{nome_artigo}* para o título a ser pesquisado, em *{limite_de_artigos}* altere para limitar a quantidade de registros, *{ano_publicado}* altere para o ano publicado e *{verdadeiro_ou_falso}* se o artigo é aberto ao público - true e false. **Sempre limite a aquantidade de registros, pois o servidor não irá responder.**

**Operações GET e POST**\

Para realizar somente o método **GET**, buscar dados:
```
GET /api/v1/openalex/
```

Fluxo **GET**:
```text
GET /api/v1/articles/
        ↓
Pesquisa na OpenAlex
        ↓
Retorna artigos
        ↓
NÃO salva no PostgreSQL
```

Para gravar os artigos no banco de dados, é necessário chamar o endpoint abaixo, assim ele não gera duplicidade de artigos:
```
POST /api/v1/openalex/import
```

Fluxo **POST**:
```text
POST /api/v1/articles/import
        ↓
Pesquisa na OpenAlex
        ↓
Normaliza os artigos
        ↓
save_articles()
        ↓
PostgreSQL
```

---

## Criando a API da CORE 

**Endpoints da Core**: 

```html
1. Pesquisa por palavra chave:
* http://localhost:8000/api/v1/core/works?q={nome_artigo}

2. Pesquisar por ID na CORE:
* http://localhost:8000//api/v1/core/works/{id}

3. Pesquisar por Outputs na CORE
* http://localhost:8000/api/v1/core/outputs?q={nome_artigo}

4. Pesquisar Output com Dowload 
* http://localhost:8000/api/v1/core/outputs/{id}/download

5. Pesquisa com limite
* http://localhost:8000/api/v1/core/works?q={nome_artigo}&limit={numero_artigos}

6. Pesquisa com limite e paginação
* http://localhost:8000/api/v1/core/works?q={nome_artigo}&limit={numero_artigos}&offset={numero_da_pagina}
```

---

## Criando a API da CROSSREF
### API´s
```html
1. Pesquisa por artigo
* https://api.crossref.org/works?query=mining

2. Limitar resultado
* https://api.crossref.org/works?query=mining&rows=20

3. Pesquisa por título
* https://api.crossref.org/works?query.title=mining 

4. Pesquisa por autor
* https://api.crossref.org/works?query.author=Smith

5. Pesquisa por DOI
* https://api.crossref.org/works/10.xxxx/xxxxx
```

**Endpoints da Crossref**
```html
1. Pesquisa por palavra chave:
* http://localhost:8000/api/v1/core/import?q={nome_artigo}&limit={numero_artigos}&offset=0
```

## Validar a tabela

Execute:
```sh
docker compose exec api python -m app.database.init_db
```

Depois confira:
```sh
docker compose exec postgres psql -U postgres -d scientific_articles -c "\d silver_articles"
```

## SQL
Criando Index
```sh
CREATE INDEX IF NOT EXISTS idx_silver_articles_year
ON silver_articles(publication_year);

CREATE INDEX IF NOT EXISTS idx_silver_articles_doi
ON silver_articles(doi);

CREATE INDEX IF NOT EXISTS idx_silver_articles_source
ON silver_articles(source);

CREATE INDEX IF NOT EXISTS idx_silver_articles_source_api
ON silver_articles(source_api);

ALTER TABLE silver_articles
ADD COLUMN IF NOT EXISTS source_api TEXT;

ALTER TABLE silver_articles
ADD COLUMN IF NOT EXISTS external_id TEXT;

UPDATE silver_articles
SET
    source_api = 'openalex',
    external_id = openalex_id
WHERE source_api IS NULL;
```

## Criando as tabelas de controle
```sql
-- ================================================================
-- CONTROLE ETL SILVER
-- ================================================================

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


-- ================================================================
-- CONTROLE ETL GOLD
-- ================================================================

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

## URL e Portas

Nomde do Serviço | URL e Porta
|---|---|
API | localhost:8000
LocalStack | 4566 
pgAdmin | localhost:5050
Airflow | localhost:8088
S3 Explore | localhost:8090

## Comando Úteis

* Adicionar source_api e external_id na silver_articles
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "ALTER TABLE silver_articles ADD COLUMN IF NOT EXISTS source_api TEXT; ALTER TABLE silver_articles ADD COLUMN IF NOT EXISTS external_id TEXT;"
```

* Preencher as novas colunas da Silver
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "UPDATE silver_articles SET source_api = 'openalex', external_id = openalex_id WHERE source_api IS NULL;"
```

* Verificar os dados da Silver
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "SELECT id, openalex_id, source_api, external_id, title FROM silver_articles LIMIT 10;"
```

* Criar chave única para source_api + external_id
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "ALTER TABLE silver_articles ADD CONSTRAINT uq_silver_source_external UNIQUE (source_api, external_id);"
```

* Executar a criação das tabelas pelo código Python
```shell
docker compose exec api python -c "from app.database.init_db import create_tables; create_tables()"
```

* Listar todas as tabelas do banco
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\dt"
```

* Ver a estrutura da bronze_etl_control
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\d bronze_etl_control"
```

* Criar/inicializar a tabela Silver através do código
```shell
docker compose exec api python -c "from app.database.create_silver import create_silver_table; create_silver_table()"
```

* Verifica as tabelas do Postgress
```shell
docker compose exec postgres psql -U articles_user -d scientific_articles -c "\dt"
```

* Testando a DAG Manualmente
```shell
docker compose exec airflow-scheduler airflow dags test gold_source_summary 2026-10-05
```