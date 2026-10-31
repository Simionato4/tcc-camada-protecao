# ADR-0025 - Reconciliacao das citacoes do OWASP 2026 e da referencia de Wilson

## Contexto
Duas pendencias de reconciliacao antes do congelamento: (1) as citacoes do OWASP na
matriz de criterios e a afirmacao de que `LLM08:2026 Hidden Context Exposure` sucede
`LLM07 System Prompt Leakage` de 2025 (`docs/matriz/01-extracao-bruta.md`; atualizacao da
Etapa 1); (2) a referencia bibliografica do metodo de Wilson (ADR-0020, D6, "a
reconciliar antes de entrar na monografia"). Na orientacao de 21/10/2026, o orientador
indicou o OWASP GenAI Security Project (https://genai.owasp.org/) como leitura.

## 1. OWASP GenAI LLM Top 10 2026

**Copia lida:** `docs/referencial/OWASP-GenAI-LLM-Top-10-2026-v1.0 (1).pdf`, sha256
`ef87993a4e50ae9d83b41ff7a3d3e6320a82dfa8d4ec6bf98d0ce264b2e6108e`; metadados: criado em
01/08/2026, modificado em 03/08/2026. Texto extraido com `pdftotext -layout`, pagina a
pagina, e lido diretamente. Consulta em 31/10/2026.

**Citacoes da matriz, identificador por identificador** (9 citacoes, 9 conferidas):

| Criterio | Citacao | Pagina do PDF | Texto do controle (resumo fiel) | Confere |
|---|---|---|---|---|
| INJ-01 | LLM01 #5, p. 14 | 14 | remover blocos de tag U+E0000-E007F, seletores de variacao U+FE00-FE0F e largura zero U+200B, U+200C, U+200D, U+2060 em toda fronteira de ingestao e exibicao; nao alcanca carga visivel nem esteganografia futura | sim |
| INJ-02 | LLM01 #3, p. 14 | 14 | filtrar em toda fronteira de modalidade; filtros semanticos sao evadiveis por reformulacao ou codificacao | sim |
| INJ-03 | LLM01 #6, p. 14 | 14 | conteudo externo por canal estruturalmente separado e rotulado por procedencia; reduz sucesso so em teste nao adaptativo | sim |
| PII-01 | LLM02 Tier 1 #5, p. 20 | 20 | "Sanitize with classifiers, not regex alone: pattern matching plus NER plus trained classifiers" | sim |
| PII-03 | LLM02 Tier 1 #7, p. 20 | 20 | higiene operacional: restringir e limpar logs e traces | sim |
| PII-04 | LLM02 Tier 1 #1, p. 20 | 20 | governar corpus; "Scrub PII at ingest" | sim |
| PII-05 | LLM02 Tier 1 #4, p. 20 | 20 | nunca guardar segredo, credencial ou dado regulado no prompt de sistema | sim |
| CTX-01 | LLM08 #1, p. 48 | 48 | nao colocar dado sensivel no contexto oculto; assumir que todo contexto e acessivel ao usuario | sim |
| CTX-02 | LLM08 #2, p. 48 | 48 | impor comportamentos criticos por sistemas independentes e deterministicos, fora do modelo | sim |

A pagina impressa no rodape ("Page N") coincide com o indice do PDF nas tres paginas.
Sumario (p. 2): LLM01 na p. 10, LLM02 na p. 18, LLM08 na p. 46.

**Sucessao LLM07:2025 -> LLM08:2026.**

| Campo | Registro |
|---|---|
| Claim | `LLM08:2026 Hidden Context Exposure` era `LLM07 System Prompt Leakage` em 2025; renomeado, ampliado e movido para a 8a posicao |
| Fonte 1 (forca 1) | PDF 2026, p. 6: "What used to be System Prompt Leakage is now Hidden Context Exposure, a broader framework for the same failure"; a figura 1 classifica as mudancas em "renamed/re-scoped"; sumario: LLM08:2026 Hidden Context Exposure |
| Fonte 2 (forca 2) | pagina oficial da edicao 2025: "LLM07:2025 System Prompt Leakage", https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/ (titulo conferido por busca, 31/10/2026) |
| Divergencia | nenhuma no conteudo. Uma nota de pesquisa da Cloud Security Alliance descreve a entrada de 2025 como "retired and replaced"; prevalece o texto do proprio OWASP, "is now ... a broader framework" |
| Decisao | a afirmacao fica como esta, com remissao a p. 6 do PDF |

**Vigencia da edicao 2026.**

| Campo | Registro |
|---|---|
| Claim | a matriz usa a edicao 2026, v1.0, de 03/08/2026 |
| Divergencia 1 | o historico de revisoes do PDF (p. 2) traz "[2026 release date] Version 2026 Release", com a data por preencher |
| Divergencia 2 | a pagina inicial do GenAI Security Project, consultada em 31/10/2026, ainda lista "LLM Top 10 for 2025" e "2023/24" entre os destaques, e cita a edicao 2026 em publicacao do blog |
| Fonte externa (forca 2, nao oficial) | Cloud Security Alliance: edicao 2026 publicada em 03/08/2026; noticias de 06/08/2026 sobre o lancamento |
| Decisao | manter a edicao 2026 como fonte da matriz, com a data dos metadados do PDF (03/08/2026) e as duas divergencias declaradas na monografia; o PDF lido fica identificado pelo sha256 acima |
| Impacto | todos os criterios INJ, PII e CTX da matriz |

## 2. Metodo de Wilson (ADR-0020, D6)

| Campo | Registro |
|---|---|
| Claim | o intervalo de 95% e calculado pelo metodo de Wilson |
| Referencia | WILSON, Edwin B. Probable Inference, the Law of Succession, and Statistical Inference. **Journal of the American Statistical Association**, v. 22, n. 158, p. 209-212, jun. 1927 |
| DOI | `10.1080/01621459.1927.10502953` (editora); `10.2307/2276774` (JSTOR) |
| Fontes consultadas | Scilit (periodico, volume, numero, paginas, DOI JSTOR) e portal MaRDI (autor, data, DOI da editora), 31/10/2026 |
| Divergencia | nenhuma entre as fontes |
| Pendencia | o texto integral do artigo nao foi lido; a referencia e bibliografica. A formula usada esta em `docs/protocolo.md`, 8.10, e e conferida pelos testes, nao pelo artigo |
| Decisao | a referencia entra na monografia como acima |

## Decisao
As nove citacoes do OWASP e a sucessao LLM07 -> LLM08 conferem com a fonte; a edicao 2026
fica como fonte da matriz, com as divergencias de vigencia declaradas. A referencia de
Wilson esta completa. As duas pendencias deixam de bloquear o congelamento.

## Alternativa considerada
Voltar a matriz para a edicao 2025, que a pagina inicial ainda destaca. Descartada: a
edicao 2026 e posterior, e o proprio OWASP a publica como sucessora; trocar exigiria
refazer a extracao de 54 controles sem ganho de validade.

## Data
2026-10-31
