# ADR-0003 - Corpus de documentos brasileiros avaliado fora do fluxo do assistente

## Contexto
As 350 ocorrencias sinteticas de documentos brasileiros servem para medir
precisao e revocacao de mascaramento. A camada (condicao B) intercepta o contexto
e a saida; o Presidio (condicao C) atua apenas sobre a saida. Se o texto passar
pelo modelo antes, B e C recebem textos diferentes, e a resposta gerada varia
entre execucoes. A comparacao ficaria contaminada pela geracao, e nao pela
deteccao.

## Decisao
O corpus de 350 ocorrencias e submetido diretamente ao endpoint da camada e ao
endpoint do Presidio, com o mesmo texto de entrada. O gabarito e o conjunto de
posicoes conhecidas no momento da geracao com semente fixa. Nenhuma chamada ao
modelo e feita para essa metrica.

## Alternativa considerada
Medir o mascaramento ponta a ponta, com o texto passando pelo assistente.
Descartada por comparar entradas diferentes e por custo de API.

## Consequencia
Isola exatamente a variavel de interesse, que e a capacidade de deteccao e
mascaramento, e zera o custo de API dessa metrica. **Limitacao a declarar nos
resultados:** os indices de precisao e revocacao medem deteccao isolada, e nao
comportamento ponta a ponta. Uma amostra pequena em fluxo real e mantida como
evidencia qualitativa complementar, sem entrar nos indices.

## Data
2026-08-29
