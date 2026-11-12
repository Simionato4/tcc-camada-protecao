# Tarefas: Etapa 4 — Camada intermediaria

**Entrada**: `spec.md` e `plan.md` desta pasta; ADR-0027.
**Formato**: `[ID] [P?] [Historia] Descricao`. [P] = pode correr em paralelo (arquivos
diferentes, sem dependencia). Cada estagio: **teste primeiro**, depois o codigo, e o teste
passando antes do estagio seguinte.

## Fase 0 — Antes do congelamento (sem regra)

- [x] T001 [US1] `camada/app/contrato.py`: `Deteccao.posicao` passa a ser no texto **original**; docstring corrigida (RQ-07). Teste em `camada/tests/test_contrato.py`
- [x] T002 [US5] `camada/app/contrato.py`: texto ate 20.000 caracteres; `id_requisicao` em UUID; teste de recusa (RQ-14; ADR-0027, E2)
- [x] T003 [US5] `camada/app/contrato.py`: campo de categoria de erro na resposta (`erro_tecnico`), sem comportamento ainda (RQ-10)
- [x] T004 [P] [US5] `docker-compose.yml`: camada com `environment` explicito, sem `env_file` (RQ-15); teste que procura `env_file` no servico da camada
- [ ] T005 [P] [US1] `assistente/fluxo.json` e `assistente/README.md`: desvio por decisao `bloquear` nos tres pontos (RF-013). Conferido com a camada atual forcando `bloquear` por variavel de teste, nunca por regra **Estado em 12/11/2026 (parcial):** nos e ligacoes feitos e conferidos por `scripts/tests/test_fluxo.py`; ramo falso exercitado pelo webhook em 11/11 (`decisao: encaminhar`). O **ramo de bloqueio nao foi exercitado**: a variavel de teste para forcar `bloquear` nao foi criada. Fica para a Fase 1, com a primeira regra que bloquear, pelo webhook (commit `3780d93`)
- [x] T006 Suite completa passando; commit (`3780d93`, 263 testes)

## Congelamento

- [ ] T007 Retorno do orientador incorporado **Nao cumprida, substituida em 12/11/2026:** o congelamento foi feito sem a revisao do orientador (ADR-0028)
- [x] T008 `python scripts/congelar.py --gravar` (Python 3.13, Unicode 15.1.0); commit do `CONGELADO.md` (`b3faabd`, 12/11/2026)
- [x] T009 Fechamento da Etapa 3 (estados dos requisitos herdados) (`eb26f30`, 12/11/2026)

## Fase 1 — Regras v0.1 (so depois de T008)

### US2 — Normalizacao com mapa de posicoes (P1)
- [ ] T010 [US2] Testes: um caso por intervalo de invisivel (U+E0000–E007F, U+FE00–FE0F, U+200B, U+200C, U+200D, U+2060), caso sem invisivel (mapa identidade), caso que altera comprimento (`camada/tests/test_normalizacao.py`)
- [ ] T011 [US2] `camada/app/normalizacao.py`: remocao e mapa de posicoes; variantes tipograficas por NFKC com mapa
- [ ] T012 [US2] Configuracao para desligar a normalizacao (ablacao, RQ-12), com teste de que o resto nao muda

### US1 — Dado pessoal (P1)
- [ ] T013 [P] [US1] Testes de digito verificador com valores escritos a mao e casos de borda documentados na ADR-0015 (`camada/tests/test_documentos.py`)
- [ ] T014 [US1] `camada/app/documentos.py`: DV proprio de CPF, CNPJ (numerico e alfanumerico), PIS/NIT, CNS e titulo; celular pelos DDDs da Anatel; regra de colisao
- [ ] T015 [US1] Testes de deteccao com formatos completo, ausente e parcial, e posicao no texto original (`camada/tests/test_deteccao_pii.py`)
- [ ] T016 [US1] `camada/app/deteccao.py`: deteccao dos sete tipos
- [ ] T017 [US1] `camada/app/decisao.py`: `mascarar` em contexto e saida, cobrindo a ocorrencia inteira; testes
- [ ] T018 [US1] Conferencia contra `conjunto_desenvolvimento/pii/` (corpus e transformado), so para depuracao, sem alvo numerico

### US4 — Marcador (P2)
- [ ] T019 [US4] Teste e regra: marcador na saida, inteiro e disfarcado pelas transformacoes da normalizacao, nao chega ao usuario

### US3 — Injecao (P2)
- [ ] T020 [US3] Testes de decodificacao: base64 e percent-encoding, ate 2 niveis, limite de tamanho, texto encaminhado = original (RQ-08; ADR-0027, E1)
- [ ] T021 [US3] Decodificacao e deteccao de padroes de injecao em `deteccao.py`; decisao `bloquear` ou `alertar` em `decisao.py`
- [ ] T022 [US3] Conferencia contra `conjunto_desenvolvimento/injecao/exemplos.jsonl`, frases benignas incluidas

### US5 — Operacao (P3)
- [ ] T023 [US5] Falha fechada: teste por modo de falha (excecao na analise, texto invalido) com `bloquear` + `erro_tecnico` (RQ-10; ADR-0027, E3)
- [ ] T024 [US5] `camada/app/registro.py`: texto de entrada mascarado no registro; teste com o corpus de desenvolvimento sem dado em claro (`PII-03`)
- [ ] T025 `versao_regras` = `0.1.0`; suite completa; commit

## Fase 2 — Modo D e demonstracao

- [ ] T026 [US3] `camada/app/moderacao.py`: modo D no `/entrada`, com teste em modo simulado; identificador do modelo devolvido no registro (RQ-16; ADR-0027, E5)
- [ ] T027 Roteiro da demonstracao: mesma pergunta, documento contaminado e dado pessoal, sem e com a camada, com exemplos do conjunto de desenvolvimento
- [ ] T028 Fechamento da Etapa 4

## Dependencias
- Fase 0 nao depende do congelamento; Fase 1 depende de T008.
- US2 antes de US1 (a deteccao usa o mapa); US1 antes de US4 e US3.
- T026 depende de chave da OpenAI, criada so quando for usada.
