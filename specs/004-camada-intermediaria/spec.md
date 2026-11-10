# Especificacao: Etapa 4 — Camada intermediaria (condicao B)

**Branch**: `main` (o projeto nao usa branch de funcionalidade)
**Criada**: 2026-11-09
**Estado**: Rascunho, aguardando revisao do autor
**Origem**: constituicao 1.1.0, fluxo item 1 (ADR-0026); matriz de criterios; requisitos herdados da Etapa 4 (RQ-07, RQ-08, RQ-10, RQ-12, RQ-14, RQ-15)

> **Regra que vale para toda esta etapa.** Nenhum codigo de regra (`normalizacao.py`,
> `deteccao.py`, `decisao.py`) e escrito antes de `conjunto_teste/CONGELADO.md` existir
> (constituicao, principio I). Esta especificacao pode ser escrita antes, porque nao
> contem regra: diz **o que** a camada precisa fazer, nao **como** detectar. As regras
> sao desenvolvidas e conferidas **so** contra `conjunto_desenvolvimento/` e contra
> exemplos escritos para isso; o conjunto de teste nao e aberto durante a etapa.

## Cenarios de uso e testes *(obrigatorio)*

O "usuario" desta etapa e o fluxo do assistente de referencia (n8n), que chama a camada
nos tres pontos de interceptacao, e o executor do experimento, que le as respostas e os
registros. O cliente final da loja e quem se beneficia.

### Historia 1 — Dado pessoal brasileiro e mascarado no contexto e na saida (Prioridade: P1)

Quando o conteudo recuperado da base ou a resposta do modelo contem CPF, CNPJ, PIS/NIT,
cartao do SUS, titulo de eleitor, celular ou endereco eletronico, a camada substitui o
dado por uma marca de mascaramento antes que ele siga adiante.

**Por que P1**: e o criterio central do trabalho (`PII-01`, `PII-02`, `PII-04`) e o que
diferencia a camada do comparador C nos documentos brasileiros.

**Teste independente**: submeter textos do corpus de desenvolvimento ao ponto `saida`
e conferir, ocorrencia a ocorrencia, a cobertura do gabarito (protocolo 8.4).

**Cenarios de aceitacao**:
1. **Dado** um texto com um CPF valido em formato completo, ausente ou parcial,
   **quando** chega ao ponto `contexto` ou `saida`, **entao** a decisao e `mascarar`,
   o trecho inteiro do CPF e substituido e a posicao devolvida aponta para o texto original.
2. **Dado** um numero com o formato de CPF e digito verificador invalido, **quando**
   chega a camada, **entao** ele nao e mascarado.
3. **Dado** um texto sem dado pessoal, **quando** chega a camada, **entao** a decisao e
   `encaminhar` e o texto sai identico.

### Historia 2 — Normalizacao com mapeamento de posicoes (Prioridade: P1)

Antes de qualquer deteccao, a camada remove caracteres invisiveis (blocos de tag,
seletores de variacao, largura zero) e trata variantes tipograficas, mantendo um mapa
de cada posicao do texto normalizado para o texto original.

**Por que P1**: sustenta a tese (`INJ-01`) e e pre-condicao da Historia 1: sem o mapa,
o mascaramento recai no lugar errado (RQ-07). A ablacao (RQ-12) mede quanto este
estagio contribui.

**Teste independente**: testes unitarios com um caso por intervalo de caractere
invisivel e casos que alteram o comprimento do texto.

**Cenarios de aceitacao**:
1. **Dado** um CPF com caracteres de largura zero entre os digitos, **quando** passa pela
   normalizacao, **entao** a deteccao o encontra e a posicao devolvida cobre, no texto
   original, do primeiro ao ultimo digito, invisiveis incluidos.
2. **Dado** um texto sem caractere a remover, **quando** passa pela normalizacao,
   **entao** o mapa e a identidade.
3. **Dado** a camada configurada sem o estagio de normalizacao, **quando** processa o
   mesmo texto, **entao** todo o resto da camada se comporta igual (para a ablacao).

### Historia 3 — Injecao de instrucao e detectada nos tres pontos (Prioridade: P2)

A camada identifica, na mensagem do usuario e no conteudo recuperado, padroes de
instrucao injetada, inclusive disfarcados por codificacao, e decide `bloquear` ou
`alertar`.

**Por que P2**: atende `INJ-02`, `INJ-04` e `INJ-05`. Vem depois da P1 porque o desempenho
esperado e menor e a medicao depende da rubrica de sucesso (pendente).

**Teste independente**: exemplos de `conjunto_desenvolvimento/injecao/exemplos.jsonl`
(12 frases-base sob 10 transformacoes), mais exemplos escritos para cada regra.

**Cenarios de aceitacao**:
1. **Dado** uma instrucao injetada codificada em base64 dentro de um documento recuperado,
   **quando** chega ao ponto `contexto`, **entao** a analise ocorre sobre o texto
   decodificado, a decisao e registrada e o texto encaminhado e o **original**, nunca o
   decodificado (RQ-08).
2. **Dado** uma frase benigna sob a mesma transformacao, **quando** chega a camada,
   **entao** nao e bloqueada so por estar codificada.

### Historia 4 — O marcador do contexto oculto nao sai na resposta (Prioridade: P2)

Se a resposta do modelo contem o marcador unico do prompt de sistema
(`CANARIO-TCC-2DEFEC2A9B0F`), a camada impede que ele chegue ao usuario.

**Por que P2**: e o criterio `CTX-02`, com vantagem estrutural declarada (a camada
conhece o marcador).

**Teste independente**: resposta sintetica com o marcador, inteiro e disfarcado pelas
transformacoes da Historia 2.

### Historia 5 — Operacao rastreavel, segura e com falha declarada (Prioridade: P3)

A camada registra cada decisao em JSON Lines sem dado pessoal em claro, valida os
limites de entrada, recebe so as credenciais que usa, e trata falhas com categoria
propria.

**Por que P3**: e infraestrutura dos criterios `PII-03`, `NOC-02` e dos requisitos RQ-10,
RQ-14 e RQ-15; nao muda a deteccao.

**Cenarios de aceitacao**:
1. **Dado** um texto com CPF, **quando** a camada registra a requisicao, **entao** o
   registro nao contem o CPF em claro.
2. **Dado** um texto acima do tamanho maximo, **quando** chega a camada, **entao** a
   requisicao e recusada com erro de validacao, sem encaminhamento.
3. **Dado** um erro interno de analise, **quando** acontece, **entao** a resposta e o
   registro trazem a categoria de erro tecnico, que nunca conta como bloqueio correto
   nem vira encaminhamento silencioso.

### Casos de borda
- Dois dados pessoais adjacentes ou sobrepostos no mesmo texto.
- Numero valido em dois tipos de mesmo comprimento (CPF e PIS/NIT; celular de 11
  digitos): regra de colisao, como no gabarito (ADR-0015).
- Texto decodificado que, por sua vez, esta codificado (profundidade de decodificacao).
- Dado pessoal da base de conhecimento numa mensagem legitima: mascarar e correto
  (ADR-0020, D9).
- Texto vazio, so espacos, ou so caracteres invisiveis.

## Requisitos *(obrigatorio)*

### Requisitos funcionais

- **RF-001**: A camada DEVE manter os tres endpoints (`/entrada`, `/contexto`, `/saida`) e
  o contrato atual de resposta (decisao, texto, deteccoes, `tempo_ms`, `versao_regras`).
- **RF-002**: A posicao de cada deteccao DEVE ser expressa em coordenadas do texto
  **original** (RQ-07). Hoje o contrato diz "texto ja normalizado": corrigir antes de
  qualquer regra.
- **RF-003**: A normalizacao DEVE remover U+E0000–E007F, U+FE00–FE0F, U+200B, U+200C,
  U+200D e U+2060 nos tres pontos, e devolver o mapa de posicoes (`INJ-01`, RQ-07).
- **RF-004**: A deteccao de dado pessoal DEVE cobrir os sete tipos do corpus, em formato
  completo, ausente e parcial, e confirmar documento pelo digito verificador (`PII-01`).
- **RF-005**: A decisao DEVE ser `mascarar` quando houver dado pessoal confirmado no
  contexto ou na saida; o trecho mascarado DEVE cobrir a ocorrencia inteira (ADR-0020, D3).
- **RF-006**: A deteccao de injecao DEVE analisar o texto decodificado e encaminhar o
  texto original (RQ-08), com profundidade maxima de decodificacao de
  [PRECISA DE DECISAO: proposta 2 niveis] e tamanho maximo do resultado de
  [PRECISA DE DECISAO: proposta igual ao limite de entrada].
- **RF-007**: A camada DEVE impedir que o marcador unico chegue ao usuario no ponto
  `saida` (`CTX-02`).
- **RF-008**: O registro DEVE mascarar dado pessoal antes de gravar (`PII-03`) e conter
  `versao_regras`, ponto, condicao, decisao, deteccoes e tempo.
- **RF-009**: A requisicao DEVE ter tamanho maximo de texto de
  [PRECISA DE DECISAO: proposta 20.000 caracteres] e identificador em formato UUID; o
  identificador serve a rastreabilidade, nao a autenticacao (RQ-14).
- **RF-010**: Em falha de analise, a resposta DEVE trazer categoria de erro tecnico
  propria; a politica e [PRECISA DE DECISAO: falhar fechado (bloquear) ou falhar aberto
  (encaminhar com alerta)] (RQ-10).
- **RF-011**: A camada DEVE receber so as variaveis de ambiente que usa, por
  `environment` explicito no compose (RQ-15).
- **RF-012**: A camada DEVE poder rodar sem o estagio de normalizacao, por configuracao,
  para a ablacao do RQ-12, sem nenhuma outra diferenca.
- **RF-013**: O fluxo do assistente DEVE interromper e devolver a mensagem de bloqueio
  quando a camada decide `bloquear`, em qualquer ponto. Mudanca no `assistente/fluxo.json`,
  variavel de controle, igual nas quatro condicoes; o hash do fluxo usado e registrado na
  execucao.
- **RF-014**: Solicitacoes nocivas (grupo NOC): [PRECISA DE DECISAO: a camada tem regra
  propria para pedido nocivo, ou a contencao no grupo NOC fica com o modelo e a camada
  so registra? A matriz mede NOC-01 em A, B e D.]
- **RF-015**: Condicao D: [PRECISA DE DECISAO: a moderacao da OpenAI e chamada pela
  camada, num modo da condicao D, ou pelo executor? Ver ADR-0006 e RQ-16.]

### Restricoes

- **Sem modelo de linguagem**: a camada e deterministica (constituicao IV; OWASP LLM08 #2).
- **Sem reaproveitar a regra R1** (`scripts/classificar_codificacao.py`): ela foi
  desenvolvida e revisada sobre casos do conjunto de teste (ADR-0017); usa-la como regra
  da camada traria conhecimento do teste para dentro da regra.
- **Sem consultar o conjunto de teste**: regras desenvolvidas so com
  `conjunto_desenvolvimento/` e exemplos escritos para cada regra (constituicao I, RQ-06).
- Toda versao das regras tem `versao_regras` proprio (versionamento semantico); a da
  demonstracao e a v0.1.

### Entidades

- **Requisicao**: ponto, condicao, texto, identificador.
- **Deteccao**: tipo, posicao no texto original, se o digito verificador conferiu, estagio
  que a produziu.
- **Resposta**: decisao, texto (mascarado ou original), deteccoes, tempo, versao das regras,
  categoria de erro quando houver.
- **Registro**: um evento JSON por linha, com os campos da resposta e o texto de entrada
  mascarado.

## Criterios de sucesso *(obrigatorio)*

Conferidos so contra o conjunto de desenvolvimento e testes unitarios. **Nenhum alvo
numerico de desempenho e fixado**: alvo numerico convidaria a ajustar regra ate atingi-lo,
e o desempenho e o resultado do experimento, nao uma meta.

- **CS-001**: Testes unitarios por estagio passam antes de o estagio seguinte comecar
  (constituicao, fluxo item 3).
- **CS-002**: Teste com caso que altera o comprimento confirma que toda posicao devolvida
  aponta para o trecho correto do texto original (RQ-07).
- **CS-003**: Teste confirma que o texto encaminhado e o original quando houve
  decodificacao (RQ-08).
- **CS-004**: Teste por modo de falha confirma a categoria de erro tecnico (RQ-10) e
  teste de validacao confirma a recusa acima do limite (RQ-14).
- **CS-005**: Nenhum dado pessoal do conjunto de desenvolvimento aparece em claro nos
  registros depois de processa-lo inteiro (`PII-03`).
- **CS-006**: A suite completa passa, inclusive `test_congelado.py`.
- **CS-007**: Demonstracao: a mesma pergunta com documento contaminado e com dado pessoal,
  sem e com a camada, mostra a diferenca de decisao.

## Premissas

- O congelamento acontece antes do inicio da implementacao.
- O assistente de referencia, o modelo e a base nao mudam nesta etapa, salvo o desvio por
  bloqueio (RF-013).
- A rubrica de sucesso da injecao (RQ-09) e escrita antes da execucao, fora desta etapa.
