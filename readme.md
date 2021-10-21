# FastApi/Redis Rate Limit

Projeto criado com a intenção de aprender um pouco mais sobre Python.
Foram utilizadas as seguintes tecnologias:
- FastApi => Framework para construção de APIs feito utilizando o Starllete;
- Redis => Ferramenta para armazenamento de dados em memória.

## Rate Limit
O `Rate Limiter` tem a função de limitar o tráfego de rede, eliminando que clientes degradem a performance do sistema ao realizarem múltiplas consultas em um curto espaço de tempo.
Neste exemplo foi utilizado o algoritmo `Sliding Window`, com um limite de 10 requests por minuto.
Clique [aqui](https://towardsdatascience.com/designing-a-rate-limiter-6351bd8762c6) para conhecer um pouco mais sobre estratégias de `Rate Limiting`.

### Por que utilizar o Redis?
No caso de uma única instância, podemos criar uma simples variável e armazenar os contadores de requisições em memória.
Porém, com a arquitetura de microsserviços e a existência de múltiplas instâncias da API, precisamos manter os contadores sincronizados, por isso utilizamos o `Redis` para compartilharmos os contadores de maneira rápida e eficiente.
O `Redis` também nos disponibiliza uma maneira atômica de incrementar os contadores, sem condição de corrida.

Também foi utilizado o serviço de `Pub/Sub` que o `Redis` oferece, permitindo que sempre que um contador for alterado, cada instância da API recebe uma notificação, permitindo com que cada instância tenha uma cópia local em memória de todos os contadores. 
Desta maneira, não é necessário consultar o `Redis` a todo o momento, economizando alguns milissegundos, principalmente em casos onde a comunicação com o `Redis` seja lenta.  


## Como executar
Após clonar o repositório, você deverá navegar até a pasta raiz e executar os seguintes passos:

### Docker Compose
- Executar o comando `docker-compose up` para levantar um `KeyDB` (alternativa ao `Redis`) e a aplicação.
- Acessar [http://localhost:5000](http://localhost:5000)

### Ambiente local
- Executar o comando `redis-cli config set notify-keyspace-events KEA` para habilitar as [notificações de keyspace](https://redis.io/topics/notifications) do Redis;
- Executar o comando `poetry install` para instalar as dependências;
- Alterar o arquivo `fastapi_rate_limit/main.py` adicionando as configurações do Redis;
- Executar o comando `uvicorn --port 5000 main:app` para executar o projeto.
- Acessar [http://localhost:5000](http://localhost:5000)

## Endpoints
A API possui dois endpoits:

- GET [/](http://localhost:7000/) Retorna um JSON com todos os contadores atuais.
- GET [/test/{client_name}](http://localhost:7000/test/api_test) Altere o `client_name` para simular requisições vindos de clientes diferentes. Retorna um JSON com o contador atual do cliente, ao realizar 10 requisições em menos de um minuto para o mesmo cliente, retorna uma mensagem de erro informando que excedeu a cota.

## Próximos passos
- [ ] Adicionar controle de Rate Limit através de um *[middleware](https://fastapi.tiangolo.com/advanced/middleware/)*
- [x] Adicionar execução por Docker
