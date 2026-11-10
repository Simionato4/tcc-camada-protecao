# ADR-0026 - Emenda da constituicao: especificacoes por etapa e atualizacoes semanais

## Contexto
A constituicao (versao 1.0.0, 31/08/2026), secao "Fluxo de desenvolvimento", exige:
- item 1: especificacao, plano tecnico e lista de tarefas por etapa (Spec Kit),
  versionados antes da implementacao;
- item 7: atualizacao semanal ao orientador.

Revisao externa de 31/10/2026, conferida pelo autor em 09/11/2026, confirmou que as duas
regras nao foram cumpridas: `specs/` tem so o `.gitkeep` desde a Etapa 0; as tarefas das
Etapas 1 a 3 existiram so no `CONTEXTO_TCC.md`, fora do repositorio; `docs/atualizacoes/`
nao recebeu nenhum commit depois de 10/09/2026. O README e a constituicao afirmavam um
metodo que nao foi seguido, e o parecer da banca (R3) elogiava justamente esse artefato.

A governanca exige ADR e incremento de versao para emendar. Nenhum principio marcado
como NAO NEGOCIAVEL e tocado, e o conjunto de teste ainda nao foi congelado.

## Decisao (do autor, 09/11/2026)
- **Item 1:** da Etapa 4 em diante, especificacao, plano e tarefas em `specs/`, com os
  modelos de `.specify/templates/`, versionados **antes** da implementacao de cada etapa.
  Para as Etapas 0 a 3, declara-se que esses artefatos nao foram produzidos, e que o
  registro delas esta nos ADRs (0000 a 0026), nas atualizacoes e nos roteiros de
  `docs/`. **Nenhuma especificacao retroativa e produzida**: seria um documento com
  aparencia de anterior a implementacao, escrito depois.
- **Item 7:** a regra continua. A lacuna de 11/09 a 09/11/2026 e declarada, e o periodo e
  coberto por uma atualizacao datada de hoje (`docs/atualizacoes/2026-11-09-etapa-3.md`),
  sem atualizacoes com datas passadas.
- Constituicao: versao **1.0.0 -> 1.1.0**, "Last Amended" 2026-11-09.
- README, secoes "Estrutura" e "Metodologia": ajustadas ao texto emendado.

## Alternativas consideradas
- **So a emenda, sem specs daqui em diante:** mais barata, mas abandona o metodo
  declarado na proposta tambem para as etapas que faltam. Descartada pelo autor.
- **Specs so da Etapa 4:** recomendada na analise, descartada pelo autor em favor de
  specs para as Etapas 4 a 7, ainda que custe mais tempo.
- **Specs retroativas das Etapas 0 a 3:** descartada por ser enganosa.

## Consequencia
A constituicao volta a descrever o que de fato acontece. O trabalho declara a lacuna, em
vez de a banca encontra-la. Custo: escrever especificacao, plano e tarefas antes de cada
uma das Etapas 4 a 7, dentro do prazo de 24/11/2026.

## Data
2026-11-09
