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

