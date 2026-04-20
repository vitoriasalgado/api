# Glossário — Módulo 0

Este arquivo contém definições, com as minhas próprias palavras, dos termos fundamentais do Módulo 0 do roadmap.

## Cliente/Servidor

No funcionamento de um sistema o cliente (navegadores, aplicativos) faz o pedido e servidor é quem responde e entrega.

## HTTP

É como o cliente e o servidor se comunicam. Há regras para que a comunicação funcione e consiga formatar pedidos e respostas. Os headers dão detalhes de como processar a mensagem e o body é o conteúdo da mensagem.
Os principais verbos são GET — pede e lê informação, POST — envia dados novos pro servidor, PUT — atualiza algo já existente, DELETE — deleta algo.
2xx - Sucesso
3xx — Redirecionamento
4xx — Erro do cliente
5xx — Erro do servidor


## REST

É uma maneira de organizar uma API, formada por um verbo HTTP (pra dizer o que fazer) e uma URL (pra dizer o objeto).

## JSON

Formato de texto mais comum nas API`s atuais para troca de dados entre cliente e servidor.

## API

API é o conjunto de endereços (endpoints) que um servidor oferece pra outros sistemas pegarem ou enviarem dados que só ele tem.

## Banco relacional

Banco de dados que guarda informações em tabelas, como planilhas, e permite que as tabelas se conectem entre si.

## ORM

Funciona como tradutor entre a linguagem do código para a linguagem do banco relacional.

## Container / Docker

Um container guarda o programa e tudo que ele precisa pra rodar (linguagem, bibliotecas, configurações), enquanto o Docker é a ferramenta mais popular pra criar e rodar containers.