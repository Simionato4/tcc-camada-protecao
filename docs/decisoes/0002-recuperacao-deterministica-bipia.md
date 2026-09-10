# ADR-0002 - Recuperacao deterministica para a injecao indireta

## Contexto
As 75 cargas do BIPIA sao embutidas nos documentos da base de conhecimento. Com
`k=3` sobre 30 documentos, um documento envenenado pode nao entrar no top 3. Se
isso ocorrer, o ataque nunca alcanca o modelo, e o caso mede sorte de recuperacao
em vez de comportamento da camada. Um avaliador de banca pode perguntar
exatamente isso.

## Decisao
Cada carga do BIPIA e embutida em um documento associado a um numero de pedido
unico, e a mensagem de teste correspondente pergunta sobre aquele pedido. A
recuperacao passa a ser deterministica por construcao. O executor registra, em
cada requisicao, quais documentos entraram no top-k, e um caso em que o documento
alvo nao foi recuperado e marcado como invalido e reportado separadamente, nunca
contado como falso negativo da camada.

## Alternativa considerada
Aumentar `k` ate cobrir a base inteira. Descartada porque descaracteriza o RAG,
infla o contexto, encarece cada chamada e deixa de representar o cenario real.

## Consequencia
A injecao indireta passa a medir a camada, e nao o recuperador. Custa o desenho
pareado pergunta-documento na Etapa 3 e um campo a mais no registro bruto. O
pareamento e uma facilidade concedida ao atacante e precisa ser declarado como
limitacao nos resultados.

## Data
2026-08-31


---

## Revisado em 10/09/2026 pelo ADR-0012

A premissa central deste registro — de que parear a pergunta ao numero do pedido
torna a recuperacao deterministica — **foi falsificada por medicao**. A primeira
indexacao real recuperou o documento alvo em apenas 3 de 30 casos, com 27 perguntas
devolvendo o mesmo trio de documentos.

Busca vetorial densa nao preserva identificadores exatos. A garantia passou a ser
obtida por filtro sobre o campo `numero_pedido`, com complemento por similaridade
(ADR-0012).

O que permanece valido deste registro: o pareamento entre pergunta e documento, a
exigencia de numero de pedido unico, o registro do top-k em cada requisicao e a
marcacao como invalido do caso em que o documento alvo nao foi recuperado.
