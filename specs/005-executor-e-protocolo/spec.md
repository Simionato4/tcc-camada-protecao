# Especificacao: Etapa 5 — Executor e protocolo

**Branch**: `main` (o projeto nao usa branch de funcionalidade)
**Criada**: 2026-11-15
**Estado**: Aprovada pelo autor em 21/11/2026; decisoes P1 a P8 na ADR-0031 (as oito recomendacoes da tabela "Pontos de decisao")
**Origem**: constituicao 1.1.0, fluxo item 1 (ADR-0026); `docs/protocolo.md`, secoes 4 a 7
(a fechar); requisitos herdados RQ-09, RQ-11 e RQ-16, mais a parte do RQ-10 movida da
Etapa 4; ADR-0029 (piloto no inicio desta etapa).

> **Regras que valem para toda esta etapa.**
> 1. O executor **nao e rodado sobre o conjunto de teste congelado** nesta etapa. A
>    execucao valida e a Etapa 6. Aqui ele e desenvolvido e conferido com o conjunto de
>    desenvolvimento, com mensagens escritas para o piloto e com o modelo em modo simulado.
> 2. A **rubrica de sucesso** (RQ-09) e escrita e commitada antes de qualquer resposta do
>    modelo a um caso do conjunto de teste existir.
> 3. As secoes 1, 2, 3 e 8 do protocolo estao congeladas e nao sao editadas. Esta etapa
>    preenche as secoes 4, 5 e 6, e a 7 (ver P2).
> 4. Registro bruto nao se edita. Correcao gera registro novo (constituicao, principio V).

## Cenarios de uso e testes *(obrigatorio)*

O "usuario" desta etapa e o autor, que roda o experimento, e depois o terceiro que queira
repeti-lo a partir do repositorio.

### Historia 1 — Rodar os casos do fluxo nas condicoes A, B e D (Prioridade: P1)

Dado um conjunto de casos, o executor envia cada mensagem ao assistente de referencia em
cada condicao prevista e grava, para cada caso e condicao, um registro bruto com tudo o
que a secao 8 do protocolo precisa para calcular os indicadores.

**Por que P1**: sem isso nao ha experimento. E o que produz os dados de `NOC-01`, `INJ-02`,
`INJ-04`, `INJ-05`, `CTX-02`, `PII-02`, `PII-04`, falso positivo e latencia.

**Teste independente**: rodar sobre mensagens escritas para o piloto, em modo simulado, e
conferir que cada registro tem todos os campos e que a contagem de registros e a prevista.

**Cenarios de aceitacao**:
1. **Dado** um caso e a condicao B, **quando** o executor o roda, **entao** o registro traz
   a decisao da camada em cada ponto, a resposta final, os documentos recuperados, os dois
   tempos e a `versao_regras`.
2. **Dado** um caso bloqueado na entrada, **quando** e rodado, **entao** o registro diz
   que o modelo nao foi acionado e nenhuma chamada ao modelo e cobrada.
3. **Dado** a condicao D, **quando** um caso do BIPIA aparece, **entao** ele nao e rodado
   (ADR-0001), e isso fica contado.
4. **Dado** as 248 perguntas do eixo de vazamento na condicao A, **quando** sao rodadas,
   **entao** ha 3 repeticoes com o modelo, cada uma com seu registro (protocolo, secao 1).

### Historia 2 — Injecao indireta com contaminacao e restauracao (Prioridade: P1)

Para cada cenario do BIPIA, o executor contamina um documento, reindexa, roda a pergunta
pareada nas condicoes A e B, restaura a base e confere a restauracao pelo hash lido do
banco (ADR-0014, RQ-18).

**Por que P1**: sem restauracao conferida, um cenario contamina o seguinte.

**Cenarios de aceitacao**:
1. **Dado** um cenario, **quando** o documento alvo nao esta entre os recuperados,
   **entao** o caso e marcado como invalido e nao entra em denominador (ADR-0002).
2. **Dado** uma restauracao em que o hash nao volta ao do estado limpo, **quando** o
   executor confere, **entao** ele **para** e nao roda o cenario seguinte.
3. **Dado** o fim dos cenarios, **quando** o executor termina, **entao** a base esta no
   estado limpo, com o hash conferido e registrado.

### Historia 3 — Corpus de documentos nas condicoes B e C (Prioridade: P1)

Cada texto do corpus e enviado a camada, no ponto `saida`, e ao Presidio (`/analyze`
seguido de `/anonymize`), fora do fluxo e sem modelo (ADR-0003; protocolo 8.4).

**Cenarios de aceitacao**:
1. **Dado** um texto, **quando** passa pelos dois componentes, **entao** o registro traz,
   de cada um, os trechos mascarados em posicoes do texto original, o tipo atribuido e o
   `tempo_total_ms`.
2. **Dado** o Presidio, **quando** e chamado, **entao** a configuracao usada (idioma,
   entidades, modelo de linguagem, limiar, versao) esta no registro da execucao (RQ-11).
3. **Dado** a ablacao (RQ-12), **quando** o corpus e rodado com a normalizacao desligada,
   **entao** os registros dos dois modos sao distinguiveis pelo campo de configuracao.

### Historia 4 — Latencia com repeticoes (Prioridade: P2)

A camada e repetida 30 vezes sobre a mesma entrada de cada caso, sem nova chamada ao
modelo (ADR-0004; protocolo, secoes 1, 2 e 8.9).

**Cenarios de aceitacao**:
1. **Dado** um caso, **quando** as repeticoes rodam, **entao** cada uma tem `tempo_ms` e
   `tempo_total_ms`, e nenhuma chamada ao modelo e feita.
2. **Dado** a condicao D, **quando** se mede a latencia, **entao** ha uma medida por caso,
   sem repeticao (protocolo 8.9).

### Historia 5 — Erro declarado, parada e retomada (Prioridade: P1)

Falha de rede, tempo esgotado, teto de orcamento e indisponibilidade de um componente tem
tratamento definido antes de acontecer (RQ-10; protocolo, secoes 5 e 6).

**Cenarios de aceitacao**:
1. **Dado** uma falha de API depois das tentativas previstas, **quando** o executor
   desiste, **entao** o registro traz `resultado_final = erro_tecnico`, que nunca conta
   como contido nem como bem-sucedido.
2. **Dado** o teto de orcamento atingido, **quando** o servico do modelo recusa,
   **entao** o executor para e informa onde parou.
3. **Dado** uma execucao interrompida, **quando** e retomada, **entao** os casos ja
   registrados nao sao rodados de novo nem sobrescritos.

### Historia 6 — Rubrica unica de resultado (Prioridade: P1)

Cada caso recebe `decisao_componente`, `comportamento_modelo` e `resultado_final`
(protocolo 8.1). O criterio que decide os dois ultimos e escrito antes de existir qualquer
resposta a um caso do teste.

**Por que P1**: e a ameaca direta a validade interna apontada no RQ-09: na condicao A
"contido" quer dizer que o modelo recusou; nas outras, que o componente bloqueou.

**Cenarios de aceitacao**:
1. **Dado** a rubrica commitada, **quando** se olha o historico, **entao** o commit dela e
   anterior ao primeiro registro bruto de caso do teste.
2. **Dado** uma resposta, **quando** a rubrica automatica nao decide, **entao** o campo
   fica `indeterminado` ate o julgamento manual, e nunca e preenchido por omissao.

### Historia 7 — Piloto (Prioridade: P1)

Assim que o executor rodar de ponta a ponta, o piloto de 20 mensagens nas quatro
condicoes e executado com o modelo real (protocolo, secao 3; ADR-0029).

**Cenarios de aceitacao**:
1. **Dado** o piloto concluido, **quando** se leem os registros, **entao** cada problema
   de instrumentacao encontrado esta listado, com a correcao feita antes da Etapa 6.
2. **Dado** os registros do piloto, **quando** a analise comeca, **entao** eles estao
   separados dos da execucao valida e nao entram em nenhum indicador.

### Casos de borda
- Resposta do modelo vazia ou cortada pelo limite de tokens.
- Caso bloqueado no contexto (o modelo nao e acionado) e caso bloqueado na saida (o modelo
  foi acionado e cobrado).
- Mesmo texto em dois casos (o repetido do Do-Not-Answer, ADR-0018): dois registros.
- Chave de API invalida ou saldo esgotado no meio da execucao.
- Moderacao da condicao D fora do ar: a camada falha fechado (`erro_tecnico`).
- Presidio fora do ar no meio do corpus.
- Registro da camada com linhas de outras origens (testes automaticos, demonstracao).

## Requisitos *(obrigatorio)*

### Requisitos funcionais

- **RF-101**: O executor DEVE ler os casos de `conjunto_teste/selecao/mapeamento_rotulos.json`
  e dos arquivos por ele apontados, e conferir os hashes de `CONGELADO.md` antes de rodar;
  hash divergente impede a execucao.
- **RF-102**: Casos do fluxo (1.164): condicoes A e B para todos; condicao D para os 1.089
  que nao sao do BIPIA (ADR-0001). Mensagens legitimas entram nas tres condicoes.
- **RF-103**: Repeticoes com o modelo conforme a secao 1 do protocolo: 1 por caso; 3 na
  condicao A para as 248 do eixo de vazamento.
- **RF-104**: O registro bruto DEVE conter, por caso, condicao e repeticao: identificador
  do caso, conjunto, grupo, categoria de origem, condicao, numero da repeticao, decisao e
  deteccoes (tipo e posicao) da camada em cada ponto, se o modelo foi acionado, resposta
  final, documentos recuperados no top-k, `tempo_ms` por ponto, `tempo_total_ms`,
  `versao_regras`, configuracao da normalizacao, modelo e hash do prompt, hash do fluxo,
  hash da colecao, instante, e os tres campos da secao 8.1. **[DECISAO P1]** se o texto da
  entrada e o da resposta ficam no registro bruto.
- **RF-105**: BIPIA: contaminar, reindexar, rodar, restaurar e conferir o hash, um cenario
  por vez (ADR-0014). Documento alvo fora do top-k: caso invalido (ADR-0002). Hash que nao
  volta: parada.
- **RF-106**: Corpus (355 textos): camada no ponto `saida`, condicao B, e Presidio
  (`/analyze` e `/anonymize`), uma vez cada; trechos mascarados em posicoes do texto
  original; `tempo_total_ms` de C como soma das duas requisicoes (protocolo 8.9).
- **RF-107**: Ablacao (RQ-12): o corpus roda tambem com `NORMALIZACAO=desligada`, em
  registros separados e identificados.
- **RF-108**: Latencia: 30 repeticoes da camada por caso e por ponto, sem modelo; a
  condicao D, uma medida por caso.
- **RF-109**: Rubrica (RQ-09): **[DECISAO P2]** forma da rubrica e quando ela e escrita;
  **[DECISAO P3]** o que fazer com as 939 respostas do grupo NOC.
- **RF-110**: Erro e nova tentativa: **[DECISAO P4]**.
- **RF-111**: Ordem de execucao e criterio de parada: **[DECISAO P5]**.
- **RF-112**: O executor DEVE passar pelo orcamento existente (`executor/orcamento.py`):
  teto em dolares e em chamadas, reserva antes de chamar, livro separado para o modo
  simulado. Modo simulado e o padrao; modo real exige gesto explicito.
- **RF-113**: Registros da camada usados no `PII-03` e no `NOC-02`: **[DECISAO P6]** como
  garantir que so as linhas da execucao entram na conta.
- **RF-114**: Piloto: **[DECISAO P7]** de onde vem as 20 mensagens.
- **RF-115**: Moderacao (RQ-16): **[DECISAO P8]** reescrita do requisito, ja que o
  servico devolve o apelido e nao a versao (verificado em 15/11/2026).
- **RF-116**: Configuracao do Presidio registrada na execucao e em `docs/versoes.md`
  (RQ-11); comportamento em indisponibilidade segue P4.
- **RF-117**: O executor NAO calcula indicador. Calculo e Etapa 7, a partir do registro
  bruto, por script versionado.

### Pontos de decisao

| # | Ponto | Opcoes | Recomendacao |
|---|---|---|---|
| P1 | Texto no registro bruto | (a) entrada e resposta inteiras, fora do Git; (b) so resumo e tamanho | **(a)**: a rubrica e o julgamento manual precisam da resposta; o registro bruto fica fora do Git (texto de ataque, ADR-0016) e so hashes e contagens sao versionados |
| P2 | Rubrica | (a) escrita nesta etapa, antes do executor rodar qualquer caso do teste, preenchendo a secao 7 do protocolo; (b) so na Etapa 6, como diz o titulo da secao 7 | **(a)**: e o que o RQ-09 exige ("escrita e congelada antes da execucao") |
| P3 | Grupo NOC (939 respostas por condicao) | (a) rubrica automatica (padroes de recusa escritos antes) + validacao manual de amostra estratificada, com concordancia medida; se a concordancia for baixa, `NOC-01` sobre amostra; (b) julgamento manual integral | **(a)**: e o proprio texto do RQ-09; (b) nao cabe no prazo |
| P4 | Erro de rede | (a) ate 3 tentativas com espera crescente para erro transitorio (tempo esgotado, 429, 5xx); erro permanente (401, 400) para a execucao; esgotadas as tentativas, `erro_tecnico`; ao fim, uma unica reexecucao dos casos com erro, em registros novos; (b) sem nova tentativa | **(a)** |
| P5 | Ordem e parada | (a) por caso: as condicoes do mesmo caso rodam em sequencia (A, B, D), para verem a mesma janela de tempo; BIPIA por cenario; corpus e latencia depois. Parada: teto de orcamento, erro permanente, hash divergente, 5 erros transitorios seguidos; (b) uma condicao inteira por vez | **(a)**: uma condicao por vez separaria A e B por horas, e uma mudanca no servico do modelo no meio viraria diferenca entre condicoes |
| P6 | Registro da camada na execucao | (a) cada execucao tem pasta propria, e a camada grava num arquivo dessa execucao; (b) arquivo unico, com o executor anotando a linha inicial e a final | **(a)**: hoje os testes automaticos gravam no mesmo arquivo da operacao |
| P7 | Mensagens do piloto | (a) 20 mensagens escritas para o piloto (5 por grupo), nenhuma do conjunto de teste; (b) 20 casos sorteados do conjunto de teste | **(a)**: rodar casos do teste no piloto mostraria respostas antes da rubrica e da execucao valida |
| P8 | RQ-16 | (a) registrar o apelido devolvido e o instante de cada chamada, rodar a condicao D numa janela continua e declarar que a versao efetiva nao e observavel; (b) manter o requisito como esta | **(a)**: (b) nao e cumprivel |

### Restricoes

- **Sem tocar no congelado**: casos, gabarito, prompt, base, secoes 1, 2, 3 e 8 do protocolo.
- **Sem regra nova na camada por causa do que o executor mostrar.** Mudanca de regra antes
  da execucao valida so com base no conjunto de desenvolvimento, e com nova `versao_regras`.
- **Texto de ataque e resposta ficam fora do Git** (ADR-0016): versionam-se hashes,
  contagens e os scripts.
- **Nenhum segredo** em registro, log ou evidencia.
- **Custo**: piloto em torno de US$ 0,14; execucao valida projetada em 3.913 chamadas e
  US$ 6,44 (protocolo, secao 1), dentro do teto de US$ 16.

### Entidades

- **Caso**: identificador, conjunto, grupo, papel, texto, atributos.
- **Execucao**: identificador, instante, commit, versoes, hashes (fluxo, prompt, colecao,
  conjunto), configuracao (normalizacao, modo do modelo, modo da moderacao).
- **Registro bruto**: uma linha por caso, condicao e repeticao (RF-104).
- **Julgamento**: caso, condicao, repeticao, `comportamento_modelo`, `resultado_final`,
  origem (rubrica automatica ou manual), em arquivo proprio; o registro bruto nao muda.

## Criterios de sucesso *(obrigatorio)*

Nenhum alvo numerico de desempenho: desempenho e resultado, nao meta.

- **CS-101**: Em modo simulado, sobre as mensagens do piloto, o executor produz o numero
  previsto de registros, todos com os campos do RF-104.
- **CS-102**: Teste de contaminacao e restauracao: depois de um ciclo, o hash lido do banco
  e o do estado limpo; restauracao que falha interrompe a execucao.
- **CS-103**: Teste por modo de falha: erro transitorio com nova tentativa, erro permanente
  com parada, teto de orcamento com parada, retomada sem sobrescrever.
- **CS-104**: Sobre o conjunto de desenvolvimento, as posicoes mascaradas gravadas para B
  conferem com as devolvidas pela camada; o mesmo para C, contra o Presidio.
- **CS-105**: A rubrica esta commitada antes de qualquer registro bruto de caso do teste.
- **CS-106**: Piloto executado com o modelo real, com a lista dos problemas encontrados e
  das correcoes.
- **CS-107**: Secoes 4, 5, 6 e 7 do protocolo preenchidas; requisitos RQ-09, RQ-10 (parte
  restante), RQ-11 e RQ-16 com estado e evidencia.
- **CS-108**: A suite completa passa, inclusive `test_congelado.py`.

## Premissas

- As regras da camada podem mudar ate a execucao valida, so contra o conjunto de
  desenvolvimento; a versao usada na Etapa 6 fica registrada em cada linha.
- O assistente de referencia (fluxo n8n), o modelo e a base nao mudam nesta etapa, salvo o
  que o plano mostrar ser necessario para o executor obter os campos do RF-104; nesse
  caso a mudanca vale igual nas quatro condicoes e o hash do fluxo e registrado.
- A execucao valida (Etapa 6) e a analise (Etapa 7) tem especificacao propria.
