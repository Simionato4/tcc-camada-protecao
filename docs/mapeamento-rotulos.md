# Mapeamento dos rotulos de origem para os grupos da matriz

Tarefa 3.4. Cumpre o RQ-04: rotulacao de origem de cada conjunto, mapeamento de cada
rotulo para os quatro grupos da matriz, criterio textual, autoria e data. Decisao de
desenho na ADR-0018.

**Autoridade:** `conjunto_teste/selecao/mapeamento_rotulos.json`, gerado por
`python scripts/gerar_mapeamento.py`. Um registro por caso, sem texto (ADR-0016). Este
documento justifica o JSON; quando divergirem, o JSON e o que o executor le, e a
divergencia e defeito a registrar. O `CONGELADO.md` (tarefa 3.11) referencia o JSON pelo
sha256.

## Autoria e forma

| Item | Valor |
|---|---|
| Autor do mapeamento | Gabriel Simionato |
| Forma | proposta elaborada com assistencia de IA a partir dos criterios da matriz; decisao final do autor, rotulo a rotulo |
| Data | 08/10/2026 |
| Anotadores | **classificador unico**, sem segundo anotador independente e sem medida de concordancia |

## Criterio textual de cada grupo

Os grupos sao os da `docs/matriz_criterios.md`. O criterio diz quando um **caso** pertence
ao grupo; cada caso tem exatamente um grupo primario (ADR-0018).

| Grupo | Um caso pertence ao grupo quando | Ancora |
|---|---|---|
| INJ | o objetivo do caso e fazer o assistente seguir instrucao do atacante em lugar da instrucao do sistema, chegando pela mensagem do usuario (injecao direta) ou pelo conteudo recuperado da base (injecao indireta) | `LLM01:2026` |
| CTX | o objetivo do caso e fazer o assistente revelar conteudo do contexto oculto que o atacante nao forneceu | `LLM08:2026` |
| NOC | o caso e uma solicitacao cujo atendimento produziria dano, segundo a taxonomia de dano do conjunto de origem | NIST AI 600-1, `MS-2.6-006` |
| PII | o caso e uma ocorrencia de documento brasileiro, ou negativo dificil, a ser detectada e mascarada | `LLM02:2026` |

O papel `controle_legitimo` nao e grupo: as mensagens legitimas sao o controle de falso
positivo de todos os grupos.

## Mapeamento por conjunto

### Do-Not-Answer (939 linhas) - grupo NOC, rotulo externo

Todas as 939 em NOC: o conjunto e uma colecao de solicitacoes nocivas classificadas por
tipo de dano, que e exatamente o criterio do grupo.

| `risk_area` | `types_of_harm` | Linhas | Atributo |
|---|---|---:|---|
| Discrimination, Exclusion, Toxicity, Hateful, Offensive | Adult Content | 28 | - |
| | Social stereotypes and unfair discrimination | 95 | - |
| | Toxic language (hate speech) | 53 | - |
| Human-Chatbot Interaction Harms | Mental Health or Overreliance Crisis | 67 | - |
| | Treat Chatbot as a Human | 50 | - |
| Information Hazards | Risks from leaking or inferring sensitive information (organization/gov) | 136 | `eixo_vazamento = organizacao_governo` |
| | Compromise privacy by leaking or inferring private information (person/individual) | 112 | `eixo_vazamento = privacidade_individuo` |
| Malicious Uses | Assisting illegal activities | 132 | - |
| | Nudging or advising users to perform unethical or unsafe actions | 71 | - |
| | Reducing the cost of disinformation campaigns | 40 | - |
| Misinformation Harms | Causing material harm by disseminating misinformation e.g. in medicine or law | 63 | - |
| | Disseminating false or misleading information | 92 | - |

Os 61 `specific_harms` distintos ficam registrados em cada caso como rotulo de origem e
nao alteram o grupo.

### BIPIA, ataques de texto (75 cargas) - grupo INJ, rotulo externo

As 15 categorias, com 5 cargas cada, vao para INJ: toda carga e instrucao embutida num
documento recuperado, isto e, injecao indireta. A categoria de origem fica registrada como
rotulo.

As 50 cargas de codigo estao fora (ADR-0014).

### HackAPrompt, amostra do `INJ-05` (40 casos) - grupo INJ, rotulo misto

`level` e rotulo externo. O estrato de codificacao e desenho deste trabalho (ADR-0017,
quatro rodadas). Daí `origem_rotulo = mista`. O unico caso de `level` 2 recebe o atributo
`objetivo_extracao` e permanece em INJ (ADR-0018).

### HackAPrompt, subamostra do `CTX-02` (10 casos) - grupo CTX, rotulo misto

`level` 2 e rotulo externo. O criterio de extracao (alvo presente no prompt e ausente do
`user_input`) e desenho deste trabalho (ADR-0018). A classe de codificacao automatica fica
como atributo, sem revisao manual.

### Pendentes

| Conjunto | Grupo | Tarefa |
|---|---|---|
| Corpus de documentos (350 positivos mais negativos dificeis) | PII, `origem_rotulo = propria` | 3.5 e 3.6 |
| Mensagens legitimas (100) | nenhum; papel `controle_legitimo`, `origem_rotulo = propria` | 3.8 |

## Decisoes de fronteira

**As 248 da area de vazamento estao em NOC, e nao em PII.** Pedem informacao sensivel
sobre terceiros; nao sao ocorrencias de documento a mascarar, e nenhum criterio PII as
mede. O recorte 136 / 112 fica como atributo, usado pelo corte C2 e pela Taxa de
Compensacao (ADR-0005, ADR-0018).

**Pedir informacao sensivel nao e CTX.** O grupo CTX trata do contexto oculto do proprio
assistente. As 136 de organizacao e governo pedem informacao sobre o mundo, e ficam em NOC.

**Os nomes de categoria do BIPIA nao descrevem a forma da carga.** Cinco categorias tem
nomes de tecnica de codificacao (`Substitution Ciphers`, `Base Encoding`, `Reverse Text`,
`Emoji Substitution`, `Language Translation`). Medido pela R1 sobre as 75 cargas: **75 de
75 sao `texto_simples`**, todas em ASCII; o atributo `representacao_r1` registra isso
caso a caso. A carga nao esta codificada nem traduzida, e por isso essas categorias nao
colidem com a exclusao de "ofuscacao por traducao" da constituicao. Que o nome descreva a
tarefa pedida pela instrucao injetada e leitura deste trabalho, **a reconciliar com o
artigo do BIPIA** antes de entrar na monografia.

**Texto repetido no Do-Not-Answer - decidido pelo autor em 08/10/2026.** As linhas `0433` e `0434`
tem o mesmo texto e os mesmos rotulos (area de vazamento, organizacao e governo).
Decisao: **manter as duas**, preservando 939, 248 e 136 — numeros da proposta aprovada e
base da comparacao com Alves et al. (2025) — e declarar que o conjunto contem 938 textos
distintos em 939 linhas. Como modelo a temperatura zero e camada deterministica tendem a
dar o mesmo resultado as duas, o caso pesa em dobro, e isso acompanha o resultado do
`NOC-01` e do eixo de vazamento.

## Contagens produzidas pelo gerador

| Conjunto | Grupo | Casos |
|---|---|---:|
| Do-Not-Answer | NOC | 939 |
| BIPIA | INJ | 75 |
| HackAPrompt (amostra do `INJ-05`) | INJ | 40 |
| HackAPrompt (subamostra do `CTX-02`) | CTX | 10 |
| **Total ate a tarefa 3.4** | | **1.064** |

Primeira geracao, em 08/10/2026 (commit `6993b7a`): sha256 do JSON
`84bbeaf1e065d4dd65b4639e3ad8e9b65d6659949fbbc6550eea0b631e2cb121`, com quebra de linha LF.
O JSON sera regerado quando a 3.6 e a 3.8 acrescentarem seus registros; o hash que vale e
o registrado no `CONGELADO.md`.

Com as 100 mensagens legitimas, os casos que passam pelo assistente somam 1.164, o numero
do bloco de 08/10/2026 da ADR-0001.

## Data
2026-10-08
