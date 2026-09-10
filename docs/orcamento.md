# Orcamento da API

Credito disponivel: **US$ 20,00**. Precos verificados em 31/08/2026:
US$ 1,00 por milhao de tokens de entrada, US$ 5,00 por milhao de tokens de saida.

## Custo unitario — medido, nao estimado

Medido em 31/08/2026 com `python scripts/fumaca_modelo.py --real -n 3`, usando
contexto representativo do protocolo: prompt de sistema, k=3 documentos de 150 a
300 tokens (ADR-0007) e uma pergunta de atendimento.

| Item | Estimado | **Medido** |
|---|---|---|
| Tokens de entrada por chamada | ~900 | **836** |
| Tokens de saida por chamada | ~200 | **162** |
| Custo por chamada | US$ 0,0019 | **US$ 0,001646** |

A medicao substitui a estimativa em todos os calculos abaixo.

## Plano de chamadas (ADR-0001)

Casos que passam pelo assistente: 939 (Do-Not-Answer) + 75 (BIPIA) + 40
(HackAPrompt) + 100 legitimas = **1.154**.

| Condicao | Casos | Repeticoes com LLM | Chamadas | Custo |
|---|---|---|---|---|
| A - sem protecao | 1.154 | 1, mais 2 extras nas 248 do eixo de vazamento | 1.650 | US$ 2,72 |
| B - camada propria | 1.154 | 1 | 1.154 | US$ 1,90 |
| C - Presidio | 0 - avaliada fora do fluxo (ADR-0003) | - | 0 | US$ 0,00 |
| D - moderacao | 1.079 - exclui as 75 do BIPIA | 1 | 1.079 | US$ 1,78 |
| **Total** | | | **3.883** | **US$ 6,39** |

O total da condicao B e teto: casos bloqueados na entrada nao chegam ao modelo,
entao o gasto real tende a ser menor. Idem para D.

Margem sobre o credito: cerca de **US$ 13,60**, suficiente para duas reexecucoes
completas. Isso importa porque registro bruto nao se edita — qualquer correcao no
protocolo obriga a rodar tudo de novo.

As 350 ocorrencias de documentos brasileiros nao aparecem nesta tabela porque sao
avaliadas fora do fluxo do assistente, sem chamada ao modelo.

## Tetos aplicados em codigo

Definidos em `.env` e verificados pelo `GuardaOrcamento` **antes** de cada
chamada, nunca depois:

| Variavel | Valor | Funcao |
|---|---|---|
| `TETO_USD` | 16.00 | limite que de fato importa; comporta duas execucoes completas (US$ 12,78) |
| `TETO_CHAMADAS` | 8500 | guarda contra laco infinito; comporta 2 x 3.883 mais piloto e testes |
| `CUSTO_ESTIMADO_CHAMADA_USD` | 0.0025 | reserva conservadora, acima do custo medido de 0,001646 |
| `MODO_SIMULADO` | 1 (padrao) | desenvolvimento com custo zero |

Os dois tetos precisam ser coerentes entre si. Na primeira versao o teto de
chamadas era 4.500, o que **nao comportava a reexecucao** de um protocolo de 3.883
chamadas que o teto em dolares permitia — inconsistencia apontada em revisao
externa e corrigida em 10/09/2026.

O guarda **reserva** o custo estimado da proxima chamada antes de autoriza-la, em
vez de apenas constatar que o teto ja foi ultrapassado. Sem a reserva, a ultima
chamada de uma execucao longa gastaria um valor que nenhum teto autorizou.

Modo simulado e modo real gravam em arquivos separados —
`resultados/consumo-simulado.json` e `resultados/consumo.json`. Sem essa
separacao, as execucoes de depuracao inflariam o consumo registrado e o teto em
dolares poderia disparar por gasto que nunca existiu. O `ClienteModelo` recusa,
na construcao, um guarda em modo divergente do seu.

O consumo acumulado soma todas as execucoes, inclusive entre processos
diferentes. A tabela abaixo e preenchida a mao a cada execucao que gaste credito,
porque `consumo.json` e estado local e nao vai para o repositorio.

## Consumo real

| Data | Etapa | Chamadas | US$ gasto | US$ acumulado | Observacao |
|---|---|---|---|---|---|
| 2026-08-31 | 0 | 3 | 0,004938 | 0,004938 | Teste de fumaca: confirma snapshot do modelo e mede custo unitario |
