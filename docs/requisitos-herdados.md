# Requisitos herdados

Requisitos que nasceram fora da etapa em que serao cumpridos. Vem dos pareceres da
banca de proposta e de uma revisao externa dos artefatos, ambos de setembro de 2026.

Existem porque um requisito descoberto na Etapa 1 e cumprido na Etapa 5 se perde,
a menos que fique escrito com dono, gatilho e criterio de aceitacao. Cada linha e
verificada no fechamento da sua etapa; nenhuma etapa fecha com requisito herdado em
aberto.

| Estado | Significado |
|---|---|
| aberto | Ainda nao cumprido |
| cumprido | Cumprido, com evidencia apontada |

---

## Etapa 2 — Assistente de referencia

### RQ-01 — Prompt de sistema sem segredo, com marcador declarado
**Origem:** OWASP LLM02 T1 #4 e LLM08 #1; criterios `PII-05` e `CTX-01`.
**Requisito:** o prompt nao contem credencial, segredo ou dado regulado. O marcador
unico e declarado como instrumento de medicao, e nao como segredo operacional.
Registrar explicitamente que a camada conhece o marcador, o que lhe confere
vantagem estrutural no criterio `CTX-02`.
**Aceitacao:** `assistente/prompt_sistema.md` versionado, e a declaracao presente na
matriz junto ao criterio. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `assistente/prompt_sistema.md` versionado e congelado (`conjunto_teste/CONGELADO.md`, secao 2); declaracao do marcador em `docs/matriz_criterios.md`, criterios `PII-05` e `CTX-02`.

### RQ-18 — Restauracao da base entre cenarios
**Origem:** revisao externa.
**Requisito:** as cargas do BIPIA contaminam documentos da base. Entre cenarios, a
base precisa ser restaurada a um estado conhecido, sob pena de contaminacao
cruzada entre casos.
**Aceitacao:** procedimento de restauracao script ado e verificavel por hash da
colecao indexada. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `recuperador/app/contaminacao.py` e `recuperador/tests/test_contaminacao.py`; ADR-0014, verificacao de 14/10/2026; `docker compose exec recuperador python -m app.indexar` em 12/11/2026, com hash dos arquivos e hash lido da colecao iguais a `f118bb58...60baa7` e recuperacao 30/30.

---

## Etapa 3 — Conjunto de teste e congelamento

### RQ-02 — Gabarito independente, com negativos dificeis
**Origem:** revisao externa. **Este e o requisito de maior impacto sobre a validade
das metricas de mascaramento.**
**Requisito:** o corpus de 350 ocorrencias precisa de gabarito com tipo e posicoes
**no texto original**, e precisa conter negativos dificeis: numeros com digito
verificador invalido, sequencias numericas de mesmo comprimento que nao sao
documento, formatos variados do mesmo tipo, sobreposicoes e ocorrencias em
contextos multiplos.
**Por que:** sem negativos dificeis, a precisao e quase nao informativa — um
detector que marca toda sequencia numerica obtem revocacao alta, e so os negativos
o denunciam.
**Aceitacao:** gabarito versionado, com contagem declarada de positivos e de
negativos dificeis por tipo. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `conjunto_teste/pii/corpus.jsonl` (355 textos; 50 positivos e 50 negativos dificeis em cada um dos 7 tipos; posicoes do gabarito conferidas contra o texto original, 0 divergencias); ADR-0015.

### RQ-03 — Recorte e formato dos documentos
**Origem:** revisao externa.
**Requisito:** declarar que CNPJ identifica pessoa juridica e nao e, por si, dado
pessoal de pessoa natural — permanece no corpus como identificador estruturado
brasileiro, com o recorte declarado. Declarar tambem qual formato de CNPJ e
suportado, uma vez que ja existe emissao em formato alfanumerico, e verificar o
suporte da biblioteca de validacao.
**Aceitacao:** declaracao em `CONGELADO.md` e verificacao do suporte por teste
unitario. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `conjunto_teste/CONGELADO.md`, secao 5; `scripts/tests/test_suporte_cnpj.py`.

### RQ-04 — Criterio de rotulacao documentado
**Origem:** parecer da banca, recomendacao 3.
**Requisito:** registrar, junto ao congelamento, a rotulacao de origem de cada
conjunto, o mapeamento de cada rotulo para os quatro grupos da matriz, o criterio
textual que orientou o mapeamento, e a autoria e data da classificacao, com a
declaracao de classificador unico.
**Aceitacao:** secao propria em `CONGELADO.md`. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `conjunto_teste/CONGELADO.md`, secao 4; `docs/mapeamento-rotulos.md`.

### RQ-05 — Versao, data e hash dos conjuntos publicos
**Origem:** parecer da banca, recomendacao 4.
**Requisito:** para Do-Not-Answer, BIPIA e HackAPrompt, registrar versao ou
identificador de commit, data de obtencao, hash SHA-256 dos arquivos e licenca.
**Aceitacao:** tabela em `CONGELADO.md`. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `conjunto_teste/CONGELADO.md`, secao 3; `conjunto_teste/origem.json`.

### RQ-06 — Conjunto de desenvolvimento separado do conjunto congelado
**Origem:** revisao externa.
**Requisito:** os exemplos usados para desenvolver e depurar as regras vivem em
`conjunto_desenvolvimento/`, versionado e distinto de `conjunto_teste/`. Congelar
antes das regras nao elimina, sozinho, o vies de desenvolvimento: e preciso que os
exemplos de trabalho sejam outros, e que isso seja verificavel.
**Aceitacao:** as duas pastas existem, e nenhum caso do conjunto congelado aparece
no de desenvolvimento — verificado por comparacao de hash caso a caso.
**Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `python scripts/verificar_separacao.py` em 12/11/2026: 0 textos em comum e 0 valores de documento em comum; ADR-0019.

### RQ-17 — Precisao da restricao sobre dados sinteticos
**Origem:** revisao externa.
**Requisito:** a restricao correta e "nenhum **dado pessoal** real". Os conjuntos
publicos sao prompts reais publicados, e nao texto sintetico. Corrigir a redacao na
constituicao, no README e na monografia, e verificar o conteudo e a licenca de cada
conjunto quanto a presenca de dados pessoais.
**Aceitacao:** redacao corrigida e verificacao registrada. **Estado:** cumprido (fechamento da Etapa 3, 12/11/2026) quanto a constituicao, ao README e a verificacao dos conjuntos (ADR-0024, 1.064 casos). A redacao na monografia fica para a escrita do texto, junto do RQ-20.

---

## Etapa 4 — Camada intermediaria

### RQ-07 — Mapeamento de posicoes entre texto normalizado e original
**Origem:** revisao externa. **Defeito latente: so apareceria depois da execucao.**
**Requisito:** a deteccao ocorre sobre o texto normalizado, e a normalizacao altera
comprimento. O gabarito usa posicoes no texto original. Sem mapeamento entre os
dois sistemas de coordenadas, o mascaramento recai no lugar errado e precisao e
revocacao ficam incorretas.
**Aceitacao:** a normalizacao devolve, alem do texto, o mapeamento indice a indice;
teste unitario com caso que altera comprimento — remocao de invisivel, remocao de
separador — conferindo que a posicao devolvida aponta para o trecho correto do
texto original. **Estado:** cumprido (fechamento da Etapa 4, 14/11/2026). Evidencia: `camada/app/normalizacao.py` devolve o texto e o mapa indice a indice; `camada/tests/test_normalizacao.py` (remocao de invisivel, caractere que vira varios, cenario do documento com largura zero) e `camada/tests/test_deteccao_pii.py` (posicao exata no original com mascara completa, parcial, ausente e com um espaco entre cada digito). Nota de desenho: os separadores nao sao removidos pela normalizacao; a deteccao os trata como parte da sequencia, e a posicao devolvida cobre a sequencia inteira no original (ADR-0030, R3). Conjunto de desenvolvimento: 350 de 350 positivos com posicao exata.

### RQ-08 — Politica de decodificacao
**Origem:** revisao externa.
**Requisito:** decodificar base64 ou percent-encoding e **encaminhar o texto
decodificado** entrega ao modelo uma instrucao que ele talvez nao compreendesse
codificada — a camada faria o trabalho do atacante. Politica: a analise ocorre sobre
o texto decodificado; o encaminhamento preserva o texto original. Definir
profundidade maxima de decodificacao e tamanho maximo do resultado.
**Aceitacao:** politica escrita no contrato da camada e teste unitario que confere
que o texto encaminhado e o original. **Estado:** cumprido (fechamento da Etapa 4, 14/11/2026). Evidencia: politica em `camada/app/contrato.py` (campo `texto` da resposta), em `camada/app/decodificacao.py` e na ADR-0027, E1 (ate 2 niveis; cada resultado limitado a 20.000 caracteres); `camada/tests/test_decodificacao.py` (niveis e limite) e `camada/tests/test_injecao.py` (o texto encaminhado e o original, nao o decodificado).

### RQ-10 — Comportamento em falha dos filtros
**Origem:** revisao externa.
**Requisito:** definir o que ocorre em tempo esgotado, indisponibilidade do Presidio
ou da moderacao, e erro de analise. Erro tecnico recebe categoria propria no
registro: **nunca e contado como bloqueio correto, e nunca resulta em
encaminhamento silencioso sem inspecao.** Declarar se a politica e falhar fechado
ou falhar aberto, e justificar.
**Aceitacao:** politica no protocolo, campo proprio no registro bruto, teste
unitario por modo de falha. **Estado:** cumprido na parte da camada; o restante **movido para a Etapa 5** (fechamento da Etapa 4, 14/11/2026). Feito: politica de falhar fechado (ADR-0027, E3); campo `erro` na resposta e no registro da camada; teste por modo de falha, um por estagio e por ponto, mais falha do registro e falha da moderacao (`camada/tests/test_falha_e_registro.py`, `camada/tests/test_moderacao.py`). Falta, e depende do executor: a politica escrita no protocolo (secao 6, a fechar na Etapa 5), o campo no registro bruto e o comportamento em indisponibilidade do Presidio (condicao C).

### RQ-12 — Ablacao da normalizacao
**Origem:** revisao externa. **Melhor relacao custo-beneficio do parecer.**
**Requisito:** executar o corpus de 350 ocorrencias na camada com e sem o estagio de
normalizacao, mantendo o restante identico. Custo de API: zero. Isola a
contribuicao do estagio que sustenta a tese do trabalho.
**Aceitacao:** tabela de revocacao com e sem normalizacao, por tipo de documento.
**Estado:** **movido para a Etapa 6** (fechamento da Etapa 4, 14/11/2026). Motivo: a aceitacao e uma tabela de revocacao sobre o corpus de 350 ocorrencias, que e o corpus congelado; executar a camada sobre ele antes da execucao valida seria ver resultado antes da hora. A Etapa 4 entrega o mecanismo: configuracao `NORMALIZACAO` (ligada ou desligada), registrada em cada linha do registro, e testes de que desligar o estagio nao muda mais nada (`camada/tests/test_ablacao.py`). Nota para a analise: o disfarce por espaco entre digitos e coberto pela deteccao, e nao pela normalizacao; a diferenca entre os dois modos vem dos invisiveis e das variantes tipograficas.

### RQ-14 — Limites de entrada
**Origem:** revisao externa.
**Requisito:** tamanho maximo de texto por requisicao e formato validado do
identificador. O UUID serve a rastreabilidade, nao a autenticacao nem a
autorizacao, e isso deve estar declarado.
**Aceitacao:** validacao no contrato Pydantic e teste que confere a recusa.
**Estado:** cumprido (fechamento da Etapa 4, 14/11/2026). Evidencia: `camada/app/contrato.py` (texto ate 20.000 caracteres, `id_requisicao` em UUID, com a declaracao de que serve a rastreabilidade); `camada/tests/test_contrato.py` (recusa); recusa sem eco do conteudo em `camada/tests/test_falha_e_registro.py` (ADR-0030, R17).

### RQ-15 — Menor privilegio nas variaveis de ambiente
**Origem:** revisao externa.
**Requisito:** a camada recebe hoje o `.env` inteiro, incluindo credenciais de que
nao precisa. Cada servico recebe apenas as variaveis que usa.
**Aceitacao:** `docker-compose.yml` com `environment` explicito por servico, sem
`env_file` global na camada. **Estado:** cumprido (fechamento da Etapa 4, 14/11/2026). Evidencia: `docker-compose.yml` sem `env_file` em nenhum servico, com `environment` explicito na camada; `scripts/tests/test_compose_privilegio.py` (a camada recebe so `ARQUIVO_LOG`, `NORMALIZACAO`, `MARCADOR`, `MODERACAO_SIMULADA` e `OPENAI_API_KEY`; a chave da Anthropic so vai para o servico do modelo).

---

## Etapa 5 — Executor e protocolo

### RQ-09 — Rubrica unica de sucesso
**Origem:** revisao externa e parecer da banca. **Ameaca direta a validade interna.**
**Requisito:** na condicao A, "contido" significa que o modelo recusou; nas demais,
que a camada bloqueou. Sao medidas diferentes apresentadas na mesma tabela. Cada
caso passa a registrar tres campos independentes:

1. **decisao do componente** — encaminhar, bloquear, mascarar, alertar, ou nenhuma;
2. **comportamento do modelo** — recusou, atendeu, atendeu parcialmente, nao foi
   acionado;
3. **resultado final do ataque** — contido, bem-sucedido, indeterminado.

O indicador comparativo entre condicoes usa o terceiro campo, unico com significado
igual em todas.

**Sub-requisito critico:** determinar recusa em 939 respostas da condicao A nao cabe
em julgamento manual integral. Definir rubrica automatizavel — padroes de recusa
mais criterio textual escrito antes — com validacao manual de amostra estratificada
e concordancia medida. Se a rubrica nao atingir concordancia aceitavel, `NOC-01`
passa a ser reportado sobre amostra estratificada, com a reducao declarada.
**Aceitacao:** rubrica escrita e congelada antes da execucao; tres campos no
registro bruto; concordancia reportada. **Estado:** aberto.

### RQ-11 — Configuracao do comparador declarada e adequada ao idioma
**Origem:** revisao externa. **Pre-requisito da validade da condicao C.**
**Requisito:** registrar idioma, entidades habilitadas, modelo de processamento de
linguagem, limiar de confianca e versao do Presidio. A configuracao precisa ser
adequada ao portugues: comparar a camada em portugues com o comparador configurado
para ingles invalida a condicao C. O teste de fumaca da Etapa 0, que enviou texto em
portugues com `language="en"`, comprova resposta HTTP e nada mais.
**Aceitacao:** configuracao versionada e registrada em `docs/versoes.md`; execucao
de sanidade em portugues antes do congelamento. **Estado:** aberto. Nota de 12/11/2026: a parte exigida antes do congelamento esta feita (configuracao versionada e congelada, `docs/versoes.md`, sanidade em portugues, ADR-0022); o estado muda no fechamento da Etapa 5.

### RQ-16 — Versao efetiva do servico de moderacao
**Origem:** revisao externa.
**Requisito:** `omni-moderation-latest` e referencia mutavel. O executor grava, em
cada registro bruto, o identificador de modelo devolvido pela propria resposta.
**Aceitacao:** campo no registro bruto e transcricao para `docs/versoes.md` apos a
execucao. **Estado:** aberto. Nota de 14/11/2026: a camada grava no registro o campo `model` devolvido pela moderacao (`camada/app/moderacao.py`, commit `62c1d08`), testado so em modo simulado. **Pendencia:** a referencia oficial nao garante que esse campo traga a versao datada; o exemplo dela repete o apelido `omni-moderation-latest`. So uma chamada real mostra o que vem. Se vier o apelido, o requisito e reescrito na Etapa 5.

### RQ-19 — Formulas dos indicadores fechadas antes do congelamento
**Origem:** revisao externa.
**Requisito:** o desenho e os criterios de calculo sao definidos antes do
congelamento; apos ele, so se completam detalhes operacionais. Fechar as formulas de
bloqueio, falso positivo, falso negativo, precisao, revocacao, F1 por tipo e Taxa de
Compensacao.
**Aceitacao:** secao 8 de `docs/protocolo.md` fechada antes de `CONGELADO.md`.
**Estado:** cumprido (fechamento da Etapa 3, 12/11/2026). Evidencia: `docs/protocolo.md`, secao 8, fechada em 14/10/2026 (ADR-0020), com hash em `conjunto_teste/CONGELADO.md` (`docs/protocolo.md#fechadas`).

---

## Etapa 7 — Analise

### RQ-13 — Incerteza junto aos percentuais
**Origem:** revisao externa.
**Requisito:** todo percentual e acompanhado da contagem que o originou e de
intervalo de confianca. Zero falso positivo observado em 100 mensagens nao
significa taxa real nula.
**Aceitacao:** tabelas de resultado com contagem e intervalo. **Estado:** aberto.

---

## Redacao da monografia

### RQ-20 — Conferencias e enquadramentos
**Origem:** revisao externa.

1. Conferir no texto integral de Alves et al. (2025) os numeros atribuidos ao
   artigo: sensibilidade de 51,97% e 122 falsos negativos.
2. Enquadrar o incidente do ChatGPT de marco de 2023 como exposicao por
   infraestrutura e cache, sem sugerir que a camada proposta o teria evitado.
3. Tratar mascaramento, anonimizacao, cifragem e conformidade juridica como
   conceitos distintos. Mascaramento nao comprova conformidade com a LGPD, e a
   conformidade juridica ja esta fora do escopo declarado.
4. Declarar a circulacao dos dados para o fornecedor do modelo e os limites do
   laboratorio.
5. Registrar que a metodologia de desenvolvimento adotada organiza o
   desenvolvimento e nao substitui o metodo cientifico, que e o desenho
   experimental descrito na metodologia.
6. Sobre falsos positivos: declarar a limitacao de autoria unica sem afirmar que a
   redacao manual **evita** subestimacao; o que se afirma e que texto gerado
   automaticamente tende a subestima-la.

**Estado:** aberto.
