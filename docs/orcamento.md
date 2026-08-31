# Orcamento da API

Credito disponivel: **US$ 20,00**. Precos verificados em 29/08/2026:
US$ 1,00 por milhao de tokens de entrada, US$ 5,00 por milhao de tokens de saida.

## Custo unitario

Contexto por requisicao, conforme ADR-0007:

| Parte | Tokens |
|---|---|
| Prompt de sistema | ~120 |
| 3 documentos recuperados (150 a 300 cada) | 450 a 900 |
| Mensagem do usuario | ~30 |
| **Entrada total** | **~900** |
| Saida (max_tokens = 400) | ~200 |

Custo estimado por chamada: **US$ 0,0019**.

> Este numero e estimativa ate a tarefa 0.4. Substituir pelo medido com
> `python scripts/fumaca_modelo.py --real -n 5`, e anotar a data.
>
> Custo unitario medido: ______  em ____/____/______

## Plano de chamadas (ADR-0001)

Casos que passam pelo assistente: 939 (Do-Not-Answer) + 75 (BIPIA) + 40
(HackAPrompt) + 100 legitimas = **1.154**.

| Condicao | Casos | Repeticoes com LLM | Chamadas |
|---|---|---|---|
| A - sem protecao | 1.154 | 1, mais 2 extras nas 248 do eixo de vazamento | 1.650 |
| B - camada propria | 1.154 | 1 | 1.154 |
| C - Presidio | 0 - avaliada fora do fluxo (ADR-0003) | - | 0 |
| D - moderacao | 1.079 - exclui as 75 do BIPIA | 1 | 1.079 |
| **Total** | | | **3.883** |

Custo projetado: **US$ 7,38**. Sobram cerca de US$ 12,60, o que cobre uma
reexecucao completa — provavel, ja que registro bruto nao se edita e correcao
gera nova execucao.

As 350 ocorrencias de documentos brasileiros nao aparecem nesta tabela porque
sao avaliadas fora do fluxo do assistente, sem chamada ao modelo.

## Tetos aplicados em codigo

Definidos em `.env` e verificados pelo `GuardaOrcamento` **antes** de cada
chamada, nunca depois:

| Variavel | Valor | Funcao |
|---|---|---|
| `TETO_CHAMADAS` | 4500 | impede laco infinito |
| `TETO_USD` | 16.00 | impede laco caro com poucas chamadas |
| `MODO_SIMULADO` | 1 (padrao) | desenvolvimento com custo zero |

O consumo acumulado fica em `resultados/consumo.json` e soma todas as execucoes,
inclusive entre processos diferentes.

## Consumo real

Atualizar ao final de cada execucao que gaste credito.

| Data | Etapa | Chamadas | US$ gasto | US$ acumulado | Observacao |
|---|---|---|---|---|---|
| | | | | | |
