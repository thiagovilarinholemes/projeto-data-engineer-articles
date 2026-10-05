# Instalando LocalStack Desktop

Para instalar o LocalStack Desktop, que roda no Windows, devemos baixar o programa:
```html
https://apps.microsoft.com/detail/9ntrnft9zws2?hl=pt-BR&gl=BR
```

Sempre que criar um serviço do Localstack coloque o **Token**, ele está na site 
```html
https://app.localstack.cloud/getting-started 
```

Após pegar o token coloque no arquivo .env:
```.env
# ============================================================
# LOCALSTACK - S3
# ============================================================
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1

S3_ENDPOINT_URL=http://localstack:4566
S3_BUCKET=scientific-articles

LOCALSTACK_AUTH_TOKEN=insira_o_token
```

Quando for criar o docker-compose.yml insira:
```docker
env_file:
    - ./.env
```
**OBS.**: Lembrando que o arquivo **.env** está na raiz do projeto.

## Testando o Localstack

Para verificar se o serviço está rodando, no navegador digite:
```
http://localhost:4566/_localstack/health
```
Deve aparecer algo do tipo;
```
{
  "services": {
    "s3": "available"
  }
}
```

## Comando do Localstack

1. Para criar o bucket:
```
docker exec scientific-articles-localstack awslocal s3 mb s3://scientific-articles
```

2. Para verificar a criação:
```
docker exec scientific-articles-localstack awslocal s3 ls

e

docker exec scientific-articles-localstack awslocal s3 ls s3://scientific-articles
```
Se não retornar nada nesse último comando, está correto: significa que o bucket existe, mas ainda não possui objetos.

3. Gravação de um JSON manualmente:
```
docker exec scientific-articles-localstack sh -c "echo '{\"teste\":\"localstack\"}' > /tmp/teste.json && awslocal s3 cp /tmp/teste.json s3://scientific-articles/teste.json"
```

4. E conferir:
```
docker exec scientific-articles-localstack awslocal s3 ls s3://scientific-articles --recursive
```

5. Inicializando o banco de daos
```html
docker compose exec api python -m app.database.init_db
```
