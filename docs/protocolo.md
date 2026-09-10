# Protocolo de execucao

Receita que permite a um terceiro repetir o experimento e obter os mesmos numeros.
Congelado junto com o conjunto de teste, ao fim da Etapa 3.

Este documento esta em construcao. As secoes ja fechadas estao marcadas; as demais
sao preenchidas na Etapa 5, antes da execucao completa.

---

## 1. Repeticoes — FECHADO (ADR-0001, ADR-0004; recomendacao da banca)

| Medicao | Repeticoes | Justificativa |
|---|---|---|
| Chamada ao modelo, condicoes A, B e D | 1 por caso | Temperatura zero e resposta deterministica. Verificado no teste de fumaca de 31/08: tres chamadas consecutivas com mesmo prompt e contexto produziram resposta identica, com a mesma contagem de tokens de saida |
| Chamada ao modelo, condicao A, eixo de vazamento (248 casos) | 3 por caso | A contencao depende de o modelo desprotegido recusar, e a Taxa de Compensacao depende desse valor. Serve tambem de verificacao em escala da premissa de determinismo |
| Latencia da camada, todos os casos | 30 por caso | A camada e local e deterministica; repetir nao consome credito. Mede ruido de maquina, que e o que a metrica de latencia deve capturar |
| Corpus de documentos brasileiros (350 ocorrencias) | 1 por caso | Avaliado fora do fluxo do assistente, sem chamada ao modelo (ADR-0003). Deteccao deterministica |

Total de chamadas ao modelo: 3.883. Custo projetado: US$ 6,39 sobre credito de
US$ 20, a partir do custo unitario medido de US$ 0,001646 por chamada.

As repeticoes da condicao A sao o primeiro item do plano de corte (C1).

## 2. Medicao de tempo — FECHADO (recomendacao da banca)

Duas grandezas sao registradas **em todo registro bruto, desde a primeira
execucao**, e ambas sao reportadas.

| Campo | Onde e medida | O que informa |
|---|---|---|
| `tempo_ms` | Dentro da camada, envolvendo apenas o processamento. Excluidos serializacao HTTP e transporte | Custo computacional da estrategia |
| `tempo_total_ms` | No executor, envolvendo a requisicao HTTP completa, do envio ao recebimento | Custo de adocao, incluindo transporte |

Ambas reportadas em p50 e p95, com desvio-padrao entre repeticoes.

**Comparacao entre condicoes.** A comparacao das quatro condicoes e feita sobre
`tempo_total_ms`, unica grandeza que existe para todas: a condicao C usa o Presidio
em conteiner e a condicao D usa servico externo, e em nenhuma das duas ha tempo
interno separavel do transporte. O `tempo_ms` e reportado como decomposicao da
condicao B, respondendo quanto do custo e processamento e quanto e transporte.

A diferenca entre as duas grandezas e reportada explicitamente: e o dado que
interessa a quem for adotar a solucao.

## 3. Piloto — FECHADO (recomendacao da banca)

Executado **ao fim da Etapa 4**, assim que a camada tiver a primeira versao
funcional, e nao dentro da Etapa 5 como previa o plano original.

- Amostra: 20 mensagens, cobrindo os quatro grupos de criterios.
- Quatro condicoes.
- Custo estimado: cerca de US$ 0,14.

Finalidade: revelar problemas de instrumentacao — formato de registro, medicao de
tempo, tratamento de erro de API, recuperacao do documento alvo — enquanto ainda ha
prazo para corrigi-los. Os registros do piloto sao descartados e nao entram na
analise; a execucao valida e a da Etapa 6.

## 4. Formato do registro bruto — A FECHAR na Etapa 5

Campos previstos: identificador, condicao, conjunto de origem, grupo de criterio,
categoria de risco de origem, entrada, decisao adotada, resposta final, `tempo_ms`,
`tempo_total_ms`, numero da repeticao, `versao_regras`, documentos recuperados no
top-k.

## 5. Ordem de execucao e criterio de parada — A FECHAR na Etapa 5

## 6. Tratamento de erro de rede e politica de nova tentativa — A FECHAR na Etapa 5

## 7. Criterio de julgamento manual da condicao A — A FECHAR na Etapa 6

Escrito **antes** de julgar, conforme regra permanente.

## 8. Formulas dos indicadores — A FECHAR na Etapa 5

Bloqueio, falso positivo, falso negativo, precisao e revocacao de mascaramento,
Taxa de Compensacao, latencia em p50 e p95.
