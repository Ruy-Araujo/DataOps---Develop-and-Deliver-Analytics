# Projeto DataOps

- [Projeto DataOps](#projeto-dataops)
  - [Introdução](#introdução)
  - [Estrutura do projeto](#estrutura-do-projeto)
    - [Extração](#extração)
  - [Origem dos dados](#origem-dos-dados)
  - [Requisitos](#requisitos)

## Introdução

Projeto desenvolvido durante a aula de DataOps do curso de MBA de Engenharia de dados turma 03, oferecido pela faculdade Impacta.

Nesta disciplica abordamos os seguintes temas:

- Conceito de DataOps
- Níveis de maturidade de projetos em Engenharia de Dados
- Tecnologias em Engenharia de Dados
- Princípios e boas práticas em projetos de Engenharia de Dados
- Orquestração e monitoramento

## Estrutura do projeto

![alt text](./misc/projeto.png)

### Extração

  Para extração dos dados foi utilizado a biblioteca httpx, com o objetivo de realizar requisições HTTP de forma assíncrona.

## Origem dos dados

- <https://swapi.dev/api/people/>?
- <https://swapi.dev/api/planets/>?
- <https://swapi.dev/api/films/>?

## Requisitos

- Formato da tabela de entrega: csv
- Frequência de atualização do dado: frequência de 1x por dia
- Parâmetro de coleta: 1 página por dia
- Salvar logs do processo
- Armazenamento dos dados brutos
- Armazenamento dos dados saneados: Tratamento de tipos, nomes e nulos
- Armazenamento dos dados agregados e tratados
- Validação de qualidade de dados: Validação de duplicados e Tolerância de nulos
- Orquestração realizada via airflow
