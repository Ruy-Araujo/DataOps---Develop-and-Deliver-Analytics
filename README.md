# Projeto DataOps

- [Projeto DataOps](#projeto-dataops)
  - [Introdução](#introdução)
  - [Requisitos](#requisitos)
  - [Arquitetura do projeto](#arquitetura-do-projeto)
    - [Extração](#extração)
    - [Sanitização](#sanitização)
    - [Transformação e Disponibiliade](#transformação-e-disponibiliade)
    - [Orquestração](#orquestração)
  - [Origem dos dados](#origem-dos-dados)
  - [Como executar o projeto](#como-executar-o-projeto)
  - [Contribuidores](#contribuidores)

## Introdução

Projeto desenvolvido para avaliação final da disciplina DataOps oferecida no curso de MBA em Engenharia de Dados turma 03 (2023-2024), oferecido pela faculdade Impacta.

O projeto consite em obter dados da API “SWAPI — the Star Wars API” e gerar um arquivo .csv com os dados relativos a características do personagem, seu planeta natal e os filmes em que ele/ela participou.
A API SWAPI refere-se ao universo de Star Wars, maior franquia da cultura pop de todos os tempos, e traz dados relativos a Planetas, Naves Espaciais, Veículos, Pessoas (no nosso caso adotamos o conceito de Personagem), Filmes e Espécies. Todo o conteúdo do site em que a api está hospedada está em inglês, logo as bases estão em inglês sendo denominadas Planets, Spaceships, Vehicles, People, Films and Species.
Para esse projeto consumimos dados apenas das  fontes de dados Planets, People e Films, conforme descrição a seguir:

- Personagens: Os detalhes sobre os personagens da saga Star Wars podem ser obtidos na seguinte URL: <https://swapi.dev/api/people/>.

- Planetas: Informações sobre os planetas do universo Star Wars estão disponíveis na URL: <https://swapi.dev/api/planets/>.

- Filmes: Os dados relacionados aos filmes da franquia Star Wars podem ser acessados na URL: <https://swapi.dev/api/films/>.

## Requisitos

- [x] Formato da tabela de entrega: csv
- [x] Frequência de atualização do dado: frequência de 1x por dia
- [x] Parâmetro de coleta: 1 página por requisição
- [x] Salvar logs do processo
- [x] Armazenamento dos dados brutos
- [x] Armazenamento dos dados saneados:
  - [x] Tratamento de tipos
  - [x] Tratamento de nomes
  - [x] Tratamento de nulos
  - [x] Armazenamento dos dados agregados e tratados
- [x] Validação de qualidade de dados:
  - [X] Validação de duplicados
  - [x] Tolerância de nulos

## Arquitetura do projeto

![alt text](./misc/projeto.png)

### Extração

  Para extração dos dados foi utilizado a biblioteca httpx, com o objetivo de realizar requisições HTTP de forma assíncrona.

### Sanitização

  Para a sanitização dos dados foi utilizado a biblioteca pandas, com o objetivo de realizar a limpeza dos dados, como por exemplo, a remoção de caracteres especiais, conversão de tipos, remoção de valores nulos, etc. Levando como base os arquivos de configuração da pasta [meta](airflow/dags/swapi/meta).

### Transformação e Disponibiliade

  Após sanitizados os dados foram transformados e agrupados em um único arquivo csv para ser consulmido por outras aplicações. Todas as configurações estão disponiveis na pasta [meta](airflow/dags/swapi/meta).

### Orquestração

  Para a orquestração do projeto foi utilizado o Airflow, com o objetivo de realizar o agendamento das tarefas e monitoramento das mesmas. Todas as configurações estão disponiveis na pasta [dags](airflow/dags/swapi).

## Origem dos dados

- <https://swapi.dev/api/people/>?
- <https://swapi.dev/api/planets/>?
- <https://swapi.dev/api/films/>?

## Como executar o projeto

Para executar o projeto é necessário ter o docker e docker-compose instalados na máquina.

1. Clone o projeto

2. Execute o build da imagem do airflow customizada com as bibliotecas necessarias para o projeto.

```bash
docker build -t custom-airflow:2.7.2 -f ./Dockerfile.airflow .   
```

3. Preencha as variáveis de ambiente necessarias no arquivo .env

4. Configure o projeto com o comando abaixo.

```bash
docker compose up airflow-init   
```

5. Inicie o projeto com o comando abaixo.

```bash
docker compose up
```

6. Acesse o airflow em <http://localhost:8080>.

## Contribuidores

<a href="https://github.com/Ruy-Araujo">
<img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/53796141?v=4" width="100px;" alt=""/>
<br />
<sub><b>Ruy Araujo</b></sub></a>
<br />

<a href="https://github.com/icaloooou">
<img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/72050304?v=4" width="100px;" alt=""/>
<br />
<sub><b>Ingrid Calou Batista</b></sub></a>
<br />

<a href="https://github.com/GiselePSouza">
<img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/147109622?v=4" width="100px;" alt=""/>
<br />
<sub><b>Gisele Souza</b></sub></a>
<br />

<a href="https://github.com/ElPablitoBR">
<img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/131319344?v=4" width="100px;" alt=""/>
<br />
<sub><b>Pablo Batista</b></sub></a> 
<br />

