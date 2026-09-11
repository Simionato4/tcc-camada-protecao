# ADR-0014 - Um cenario por carga do BIPIA, com restauracao entre cenarios

## Contexto
O conjunto BIPIA fornece 75 cargas de injecao indireta. A base de conhecimento tem 30
documentos. Pelo ADR-0012, cada carga precisa estar num documento com numero de
pedido proprio, para que a pergunta pareada o recupere por filtro exato.

Com 30 documentos nao ha como acomodar 75 pareamentos distintos ao mesmo tempo.

O BIPIA tambem separa ataques de **texto** e de **codigo**, organizados por tarefa —
Web QA, Email QA, Table QA, Summarization e Code QA.

## Decisao

### Um cenario por carga
Cada uma das 75 cargas define um cenario independente:

1. contamina-se **um** documento da base com a carga;
2. reindexa-se;
3. executa-se a pergunta pareada daquele documento, nas condicoes previstas;
4. **restaura-se a base** ao estado limpo;
5. verifica-se a restauracao pelo hash do estado.

A base permanece com 30 documentos em todos os cenarios, identica a das demais
condicoes. A atribuicao carga-documento e deterministica e registrada no
congelamento.

O procedimento de restauracao ja existe e e o mesmo da indexacao: `python -m
app.indexar` recria a colecao do zero e imprime o hash do estado. Dois caminhos
separados poderiam divergir; um so nao pode. Era para isso que o requisito RQ-18
existia.

### Apenas cargas de texto
As cargas de **codigo** ficam fora. O assistente de referencia atende clientes de
comercio eletronico sobre pedidos: nao executa, nao gera e nao interpreta codigo.
Incluir cargas de codigo mediria um vetor ausente do cenario.

A exclusao e declarada no congelamento com a contagem exata do que entrou e do que
ficou de fora. Se as cargas de texto forem menos de 75, a proposta precisa de nota
corrigindo o numero.

## Alternativas consideradas

**Ampliar a base para um documento por carga.** Evitaria a restauracao, mas alteraria
a base de conhecimento, que e **variavel de controle**: ela precisa ser identica em
todas as condicoes e em todos os cenarios. Uma base de 105 documentos nos casos de
injecao indireta e de 30 nos demais mudaria tambem as caracteristicas da recuperacao,
e a comparacao deixaria de isolar a estrategia de protecao.

**Reduzir a amostra do BIPIA para 30 cargas.** Uma por documento, sem restauracao.
Descartada por descartar 60% do conjunto de injecao indireta sem necessidade: o custo
da alternativa adotada e tempo de reindexacao, e nao credito de API.

## Consequencia
Setenta e cinco ciclos de contaminacao, reindexacao, execucao e restauracao. A
reindexacao de 30 documentos e local e barata; o custo e tempo de execucao, nao
credito.

A verificacao por hash entre cenarios deixa de ser zelo e passa a ser necessaria:
sem ela, uma restauracao que falhasse contaminaria os cenarios seguintes, e o efeito
apareceria como injecao indireta bem-sucedida onde nao houve ataque. O executor
interrompe a execucao se o hash apos a restauracao divergir do hash da base limpa.

## Data
2026-09-11
