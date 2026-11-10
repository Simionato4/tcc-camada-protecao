# ADR-0027 - Decisoes da especificacao da Etapa 4 (camada)

## Contexto
A especificacao da Etapa 4 (`specs/004-camada-intermediaria/spec.md`) deixou cinco pontos
marcados para decisao. Todos sao decididos antes do congelamento e antes de qualquer
regra; nenhum depende de resultado.

## Decisoes (do autor, 09/11/2026)

| # | Ponto | Escolha | Alternativa descartada | Motivo |
|---|---|---|---|---|
| E1 | Decodificacao (RF-006, RQ-08) | Ate **2 niveis** de decodificacao; o resultado de cada nivel limitado ao **tamanho maximo da entrada**; analise sobre o decodificado, encaminhamento do **original** | 1 nivel; sem limite | Cobre texto codificado duas vezes sem laco; o limite impede expansao abusiva |
| E2 | Tamanho maximo da entrada (RF-009, RQ-14) | **20.000 caracteres** por requisicao; identificador em UUID, que serve a rastreabilidade e nao a autenticacao | sem limite | O contexto tem 3 documentos de 150 a 300 tokens (ADR-0007) e a resposta, no maximo 400 tokens: o limite da folga sem permitir abuso |
| E3 | Falha da analise (RF-010, RQ-10) | **Falhar fechado**: a decisao e `bloquear`, com categoria `erro_tecnico` na resposta e no registro | falhar aberto (encaminhar com alerta) | Num gateway de seguranca, deixar passar sem inspecao e o pior caso. No experimento, erro tecnico fica fora do denominador (ADR-0020, D1) e e contado a parte, entao a escolha nao infla a contencao |
| E4 | Grupo NOC (RF-014) | **A camada nao tem regra propria para pedido nocivo.** Nos 939 casos do Do-Not-Answer, a contencao na condicao B vem do modelo ou das regras de injecao e de contexto que coincidirem; a camada registra | regras por padrao para os 12 tipos de dano | A propria matriz registra que a contencao de pedido nocivo e atributo do modelo, e que o OWASP nao tem entrada para isso; regras por palavra para 12 tipos de dano em ingles custariam dias e dariam resultado fraco |
| E5 | Condicao D (RF-015, ADR-0006) | A moderacao da OpenAI e chamada **pela camada**, num modo da condicao D, **no ponto `/entrada`**; nos pontos `/contexto` e `/saida`, a camada em modo D so encaminha | chamar no executor, antes do fluxo | O fluxo do assistente continua identico nas quatro condicoes (variavel de controle). O tempo da condicao D inclui a rede, limitacao ja declarada na ADR-0009 |

## Expectativa registrada antes da execucao (E4)
Como na ADR-0006 para a moderacao: **no grupo NOC, a condicao B deve ficar proxima da
condicao A**, porque a camada nao foi desenhada para conter pedido nocivo. Uma diferenca
pequena entre A e B no grupo NOC e resultado esperado, e nao fraqueza descoberta depois.
O criterio `NOC-01` continua medido em A, B e D pelo `resultado_final` (RQ-09); a matriz
recebe nota sobre isso.

## Consequencia
A especificacao da Etapa 4 fica sem ponto em aberto. RQ-08, RQ-10 e RQ-14 ganham politica
escrita; o RQ-16 (versao efetiva da moderacao) fica com lugar definido para o campo do
registro, na camada em modo D. A condicao D precisa de chave da OpenAI, criada so quando
for usada.

## Data
2026-11-09
