# ADR-0009 - Registro de duas grandezas de tempo

## Contexto
A proposta aprovada define a latencia como o tempo de processamento interno da
camada, com o tempo de rede deliberadamente excluido da metrica, para evitar
contaminacao pela variabilidade da rede. Essa definicao consta entre as restricoes
metodologicas do projeto.

Ao avaliar a proposta, um dos avaliadores recomendou registrar as duas grandezas
separadamente desde a primeira execucao — tempo interno da camada e tempo total da
requisicao — e reportar ambas, observando que a diferenca entre elas e informacao
util para quem for adotar a solucao.

Ha ainda uma inconsistencia interna do protocolo original, identificada durante a
Etapa 0: a condicao C usa o Presidio em conteiner e a condicao D usa servico
externo. Em nenhuma das duas existe tempo interno separavel do transporte, de modo
que a metrica definida na proposta so e aplicavel a condicao B. Comparar as quatro
condicoes em latencia era, na definicao original, impossivel.

## Decisao
Todo registro bruto passa a conter duas grandezas, ambas reportadas em p50 e p95:

| Campo | Onde e medida | O que informa |
|---|---|---|
| `tempo_ms` | Dentro da camada, envolvendo apenas o processamento | Custo computacional da estrategia |
| `tempo_total_ms` | No executor, envolvendo a requisicao HTTP completa | Custo de adocao, incluindo transporte |

A comparacao de latencia entre as quatro condicoes e feita sobre `tempo_total_ms`,
unica grandeza existente em todas. O `tempo_ms` e reportado como decomposicao da
condicao B, respondendo quanto do custo e processamento e quanto e transporte. A
diferenca entre as duas e reportada explicitamente.

## Relacao com a restricao metodologica original
A restricao determinava que o tempo de rede nao entrasse na metrica de latencia
interna. Ela permanece integralmente valida: `tempo_ms` continua sendo medido
dentro da camada, isoladamente, exatamente como definido. O que muda e o
acrescimo de uma segunda grandeza, e a escolha de qual delas sustenta a comparacao
entre condicoes.

Trata-se de ampliacao do registro, nao de flexibilizacao da regra. A alteracao e
declarada nos resultados, junto ao motivo.

## Alternativa considerada
Manter apenas o tempo interno e reportar latencia somente para a condicao B,
declarando que as demais nao sao comparaveis nesse eixo. Descartada porque o
objetivo geral do trabalho enuncia a avaliacao comparativa quanto a latencia
adicional, e essa alternativa deixaria um objetivo especifico parcialmente sem
resposta.

## Consequencia
A comparacao de latencia passa a existir para as quatro condicoes, cumprindo o
objetivo. O custo e que `tempo_total_ms` incorpora variabilidade de rede, o que se
mitiga pelas 30 repeticoes de medicao previstas e pelo reporte do desvio-padrao.
Ambas as grandezas precisam existir no formato de registro bruto desde a primeira
execucao, inclusive no piloto: acrescentar campo depois obrigaria a nova execucao,
ja que registro bruto nao se edita.

## Data
2026-09-10
