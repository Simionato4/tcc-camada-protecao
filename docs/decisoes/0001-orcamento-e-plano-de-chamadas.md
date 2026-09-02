# ADR-0001 - Plano de contagem de chamadas e tetos de orcamento

## Contexto
O credito disponivel e de US$ 20. A proposta estimou 6.850 chamadas a cerca de
US$ 12, numero que so se sustenta com contexto pequeno e resposta curta. O plano
de desenvolvimento previa ate 3 repeticoes por caso em 4 condicoes, o que daria
13.848 chamadas e ultrapassaria o credito. Preco verificado em 31/08/2026:
US$ 1 por milhao de tokens de entrada e US$ 5 por milhao de tokens de saida.

## Decisao
O experimento executa 3.883 chamadas ao modelo, distribuidas assim:

| Condicao | Casos que passam pelo modelo | Repeticoes com LLM | Chamadas |
|---|---|---|---|
| A - sem protecao | 1.154 | 1, mais 2 extras nas 248 do eixo de vazamento | 1.650 |
| B - camada propria | 1.154 | 1 | 1.154 |
| C - Presidio | 0 (avaliada fora do fluxo, ver ADR-0003) | - | 0 |
| D - moderacao | 1.079 (exclui as 75 do BIPIA) | 1 | 1.079 |
| **Total** | | | **3.883** |

Tetos configurados em `.env`, aplicados pelo `GuardaOrcamento` antes de cada
chamada: `TETO_CHAMADAS=4500` e `TETO_USD=16.00`. Nenhum modulo do projeto chama
o modelo fora de `executor/cliente_modelo.py`. `MODO_SIMULADO=1` e o padrao, e o
consumo simulado e gravado em livro-caixa separado do real.

O BIPIA fica fora da condicao D porque a injecao indireta chega pelo documento
recuperado, e a moderacao atua sobre a mensagem de entrada. Nesses casos D seria
identica a A, e rodar as duas gastaria credito sem produzir informacao.

## Alternativa considerada
Manter 3 repeticoes com chamada real ao modelo em todas as condicoes, como o
plano original previa. Descartada por custo: excede o credito disponivel sem
acrescentar informacao, porque a dispersao que interessa e a da camada (ADR-0004).

## Consequencia
Custo projetado de US$ 6,39, deixando cerca de US$ 13,60 de margem — suficiente
para duas reexecucoes completas, o que a regra de nao editar registro bruto torna
provavel.

## Custo unitario medido (2026-08-31)

Substitui a estimativa original de US$ 0,0019 por chamada. Medido com
`python scripts/fumaca_modelo.py --real -n 3`, com contexto representativo:
prompt de sistema, k=3 documentos e uma pergunta de atendimento.

| Item | Estimado | Medido |
|---|---|---|
| Tokens de entrada por chamada | ~900 | 836 |
| Tokens de saida por chamada | ~200 | 162 |
| Custo por chamada | US$ 0,0019 | **US$ 0,001646** |
| Projecao para 3.883 chamadas | US$ 7,38 | **US$ 6,39** |

O snapshot `claude-haiku-4-5-20251001` foi confirmado na mesma execucao: um
identificador inexistente e rejeitado pela API.

## Data
2026-08-31
