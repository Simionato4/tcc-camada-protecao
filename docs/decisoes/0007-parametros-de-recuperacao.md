# ADR-0007 - Parametros de recuperacao: k=3 e documentos de 150 a 300 tokens

## Contexto
O tamanho do contexto define o custo de cada chamada e, por consequencia, a
viabilidade do experimento dentro do credito. Tambem afeta a chance de o
documento envenenado ser recuperado.

## Decisao
`k=3` sobre uma base de 30 documentos, cada documento com 150 a 300 tokens. O
contexto recuperado fica entre 450 e 900 tokens por requisicao.

## Alternativa considerada
`k=5`, que aumentaria a cobertura da recuperacao. Descartada porque elevaria o
custo unitario em cerca de 40% sem beneficio para o desenho, ja que a recuperacao
do documento envenenado passou a ser garantida por pareamento (ADR-0002).

## Consequencia
Custo unitario baixo e janela de contexto folgada. Como `k=3` sobre 30 documentos
nao garante por si a recuperacao do documento alvo, o ADR-0002 e dependencia
obrigatoria desta decisao.

## Data
2026-08-29
