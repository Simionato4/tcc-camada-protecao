# ADR-0029 - Piloto no inicio da Etapa 5, e nao no fim da Etapa 4

## Contexto
O protocolo, secao 3 (FECHADA e congelada em 12/11/2026), diz que o piloto e "executado
ao fim da Etapa 4, assim que a camada tiver a primeira versao funcional": 20 mensagens,
cobrindo os quatro grupos de criterios, nas quatro condicoes, com custo estimado de
US$ 0,14. Finalidade declarada: revelar problemas de instrumentacao (formato de registro,
medicao de tempo, tratamento de erro de API, recuperacao do documento alvo).

A camada tem a primeira versao funcional (regras v0.1.0, commit `a87f409`; modo da
condicao D em `62c1d08`). O piloto, porem, depende de um **executor**: o programa que le
os casos, chama o fluxo nas quatro condicoes e grava o registro bruto. O executor e o
objeto da Etapa 5 e ainda nao existe. A condicao C (Presidio) tambem so entra pelo
executor.

## Decisao (do autor, 14/11/2026)
Fechar a Etapa 4 sem o piloto. O piloto roda **no inicio da Etapa 5, assim que o executor
existir, e antes de qualquer execucao valida**. Tamanho, condicoes e finalidade nao
mudam. O texto congelado do protocolo nao e alterado; esta ADR registra o desvio.

## Alternativas descartadas
| Alternativa | Por que nao |
|---|---|
| Fazer um executor minimo dentro da Etapa 4, so para o piloto | E trabalho da Etapa 5 feito sem especificacao, contra a ADR-0026 (especificacao, plano e tarefas antes de cada etapa) |
| Manter a Etapa 4 aberta ate o executor existir | Etapa sem fechamento, com requisitos herdados pendurados e o estado real escondido |

## Por que o desvio nao afeta o metodo
- E desvio de **calendario**: o piloto continua anterior a execucao valida (Etapa 6), que
  e o que a finalidade dele exige.
- Tudo o que o piloto procura revelar (formato de registro, medicao de tempo, erro de API,
  recuperacao do documento alvo) e comportamento do executor.
- Os registros do piloto continuam descartados e fora da analise, como o protocolo ja diz.

## Insumos ja observados, para a especificacao da Etapa 5
Nos testes de 12/11/2026 para a demonstracao (`docs/orcamento.md`,
`docs/roteiro-demonstracao.md`), que **nao** substituem o piloto:
- quando a API do modelo falha, o servico do modelo devolve erro 500 sem tratamento, e o
  fluxo termina sem resposta (protocolo, secao 6, a fechar na Etapa 5);
- os testes automaticos gravam no mesmo `resultados/camada.jsonl` da operacao: o executor
  precisa comecar com registro proprio e limpo, ou a medida do `PII-03` fica contaminada;
- a chave da API pode estar invalida sem que nada avise antes da primeira chamada;
- a moderacao da condicao D ainda nao foi chamada com o servico real, e nao se sabe se o
  campo `model` da resposta traz a versao datada (RQ-16).

## Consequencia
A especificacao da Etapa 5 traz o piloto como primeira entrega do executor. O fechamento
da Etapa 4 (T028) nao inclui o piloto.

## Data
2026-11-14
