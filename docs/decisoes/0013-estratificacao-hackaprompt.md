# ADR-0013 - Estratificacao do HackAPrompt pelas classes de codificacao do OWASP

## Contexto
O criterio `INJ-05` da matriz quantifica falsos negativos **por tecnica de
ofuscacao** sobre a amostra de 40 casos do HackAPrompt. A matriz ja registrava, como
dependencia, que isso exigiria estratificar a amostragem por esse atributo.

Verificacao em 11/09/2026: o conjunto expoe as colunas `level`, `user_input`,
`prompt`, `completion`, `model`, `expected_completion`, `token_count`, `correct`,
`error`, `score`, `dataset` e `timestamp`. **Nao ha atributo de tecnica de ataque.**

Sem rotulacao, o criterio ficaria sem metodo.

## Decisao
Os casos amostrados sao classificados por **classe de codificacao**, usando a
taxonomia enunciada pelo proprio referencial adotado. O `LLM01:2026 Prompt Injection`
descreve a anatomia de uma injecao em tres eixos, e o eixo de codificacao —
*"how the malicious instructions are represented in tokens or pixels"* — nomeia as
classes:

| Classe | Descricao |
|---|---|
| Texto simples | Instrucao legivel, sem ofuscacao |
| Codificacao | Base64 ou outra transformacao reversivel |
| Unicode invisivel | Largura zero, seletores de variacao, blocos de tag |
| Multimodal ou esteganografico | Fora do escopo deste trabalho; registrado por completude |
| Idioma de poucos recursos | Instrucao em lingua de baixa representacao |

A amostragem estratificada de 40 casos e feita sobre essa classificacao, com semente
registrada. As classes fora do escopo declarado — multimodal e esteganografica — nao
entram na amostra, e a exclusao e registrada.

**A taxonomia vem da norma, e nao do autor.** Isso importa: uma classificacao
inventada para o trabalho seria mais um ponto a defender; uma classificacao extraida
do referencial que o trabalho ja adota e rastreavel a uma fonte publicada.

## Rotulacao
A classificacao e feita pelo autor, sobre os casos candidatos, **antes** da
amostragem e **antes** de qualquer regra da camada existir. Registrados junto ao
congelamento, conforme RQ-04:

- o criterio textual usado para cada classe;
- a decisao de cada caso;
- a autoria e a data;
- a declaracao de **classificador unico**, com a limitacao correspondente.

A limitacao de classificador unico ja e declarada para as mensagens legitimas, e
passa a valer tambem aqui.

## Alternativas consideradas

**Estratificar pelo campo `level` da competicao.** Atributo real do conjunto, sem
custo de rotulacao. Descartada porque mudaria o sentido do criterio: passaria a medir
falso negativo por nivel de dificuldade da competicao, e nao por tipo de ofuscacao —
e e a degradacao por tipo de ofuscacao que interessa, porque e contra ela que a
camada possui mecanismo, na normalizacao.

**Rebaixar o `INJ-05` para fora do escopo.** Descartada porque eliminaria o unico
criterio que mede degradacao por classe de ofuscacao, justamente o eixo em que a
camada tem mecanismo proprio a ser avaliado.

## Consequencia
O criterio `INJ-05` permanece na matriz com metodo valido. Custa de uma a duas horas
de classificacao manual, feita antes do congelamento.

Acrescenta uma limitacao declarada: a classificacao e de um unico anotador, sem
verificacao de concordancia. A alternativa — dois anotadores e medida de concordancia
— seria mais forte, e fica registrada como melhoria possivel caso haja disponibilidade
de um segundo classificador.

A classificacao e parte do conjunto congelado. Depois de `CONGELADO.md` datado, ela
nao muda, ainda que um caso pareca mal classificado a luz dos resultados.

## Data
2026-09-11
