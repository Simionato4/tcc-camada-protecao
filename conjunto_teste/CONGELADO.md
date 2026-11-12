# Conjunto de teste congelado

**Data do congelamento:** 2026-11-12  
**Commit de referencia:** `628743f18f387d6d96f6f082c67100d194039e3a` (todos os hashes abaixo sao deste commit)  
**Gerado por:** `python scripts/congelar.py --gravar`

A partir desta data, os arquivos listados nao mudam (constituicao, principio I). As
regras da camada (`normalizacao.py`, `deteccao.py`, `decisao.py`) so podem existir
depois deste arquivo, e sao desenvolvidas contra `conjunto_desenvolvimento/`, nunca
contra o conjunto abaixo. `scripts/tests/test_congelado.py` falha se qualquer hash
mudar. Desempenho ruim apos a execucao e resultado, nao defeito. Do protocolo, ficam
congeladas as secoes marcadas FECHADO; `#fechadas` indica o hash do texto dessas secoes.

## 1. Composicao

| Conjunto | Grupo | Papel | Origem do rotulo | Casos |
|---|---|---|---|---:|
| bipia | INJ | caso_de_risco | externa | 75 |
| corpus-pii | PII | caso_de_risco | propria | 355 |
| do-not-answer | NOC | caso_de_risco | externa | 939 |
| hackaprompt | CTX | caso_de_risco | mista | 10 |
| hackaprompt | INJ | caso_de_risco | mista | 40 |
| legitimas | - | controle_legitimo | propria | 100 |
| **Total** | | | | **1519** |

Textos repetidos dentro do mesmo conjunto: 1 (Do-Not-Answer, mantido e declarado, ADR-0018).

## 2. Arquivos congelados

| Arquivo | Conteudo | SHA-256 |
|---|---|---|
| `conjunto_teste/selecao/mapeamento_rotulos.json` | todos os casos do teste, grupo e rotulo (RQ-04) | `12821338c19e9c43ef620d90cc06714753a49e0eb6577358a945c68415c8b053` |
| `conjunto_teste/selecao/hackaprompt.json` | amostra do INJ-05 (40), ADR-0017 | `161ece82fa8c45d1200dc07f6a6f059099adde4ff640c2dc3ad5cc92d68b0efe` |
| `conjunto_teste/selecao/hackaprompt_ctx.json` | subamostra do CTX-02 (10), ADR-0018 | `8cffded96be852c9366413effed15aae64ee1da9c4331639e95967ecf963f322` |
| `conjunto_teste/selecao/rotulos.json` | livro de rotulos da classificacao R1, ADR-0017 | `4d0b0b7bd564d3f1bd442208d739ba89d052c67bf63feecc4d4db7268f9d0cc5` |
| `conjunto_teste/selecao/bipia_cenarios.json` | 75 cenarios de injecao indireta, ADR-0014 | `0258be6e713563f211c4e33bcbf27ae97dc16c598d80cff0f8f0afd01996a5da` |
| `conjunto_teste/pii/corpus.jsonl` | corpus de documentos com gabarito, ADR-0015 | `2ed3eb9fc6cba2746ec60c544768d5e42b13eb730c2583e3aafe944c2990a6c7` |
| `conjunto_teste/legitimas/mensagens.txt` | mensagens legitimas como redigidas, ADR-0023 | `cac860df6580c6e412eb79ab75c5138e25abe216264a40ca3d7ddf6ed0457f18` |
| `conjunto_teste/legitimas/mensagens.jsonl` | 100 mensagens legitimas, ADR-0023 | `93c90c5c1b6ca26a99fcb840eb0ff2b88d95b6d17428bbb533bcfcb232e0859d` |
| `conjunto_teste/origem.json` | procedencia e hash dos conjuntos publicos (RQ-05) | `65cd4dbbf34657a725e3454c189c0f62d3678c724ac38852ab531ce2a1157621` |
| `conjunto_teste/ORIGEM.md` | procedencia legivel e licencas | `edb08ccc064a356446b031b7300b6199611937034ff792a266c8b83b9659be01` |
| `base_conhecimento/perguntas_pareadas.json` | perguntas dos cenarios do BIPIA, ADR-0012 | `ddf33084897289d12201f2ac7035b6809b8950e31b56f7d6c14ee40a21058ded` |
| `assistente/prompt_sistema.md` | prompt de sistema, variavel de controle | `9206744b63259c0482fdc4415ec653e18c4ea3badde90cc7e44894b6f6e04a8c` |
| `docs/protocolo.md#fechadas` | secoes FECHADAS do protocolo: repeticoes, tempo, piloto e formulas (RQ-19) | `70937108338cda0ca5090faedf868ba8423409b61db2de5f169c6087e0d20896` |
| `docs/mapeamento-rotulos.md` | criterio textual do mapeamento (RQ-04) | `7a8040d079fee23a7211222342ebabd1ed066136b486cafddba6593eee384f4d` |
| `docs/guia-mensagens-legitimas.md` | regras de redacao das legitimas | `dabaf1051003252a366101d1f12910ff9f7feb51e9bd4cb476b0dd7f1549f95d` |
| `presidio-analyzer/conf/nlp_pt.yaml` | condicao C, ADR-0022 | `404b0a8ef4dc6d51117c3683f3326d4139865f28d9cdb5f49dd99037f1db229f` |
| `presidio-analyzer/conf/analyzer_pt.yaml` | condicao C, ADR-0022 | `f70778a36d2a57d0e81a465da66c07af9e89bf445b49b661ceb46d77afc75119` |
| `presidio-analyzer/conf/recognizers_pt.yaml` | condicao C, ADR-0022 | `76d0afbf3c3387b3c401af13585feced14a2fb8f0597afaf3e674adf81fbea70` |
| `base_conhecimento/documentos/` | base de conhecimento, 30 arquivos; hash do encadeamento dos hashes por arquivo, em ordem de nome | `f2a0cfef92a576d37a0ee49434058ec4373a136e68b4db41f0d2179ecea97e4b` |

Colecao do Qdrant no estado limpo (hash lido do banco, RQ-18, ADR-0014): `f118bb5851f1ce54d4053f8ca9b1eac5276cd0ca40bb006062436c343d60baa7`.

Arquivos historicos da amostragem do HackAPrompt, versionados como registro e **nao usados**:
`conjunto_teste/selecao/hackaprompt-v1-regra-com-defeito.json`;
`conjunto_teste/selecao/hackaprompt-v2-regra-rev2.json`;
`conjunto_teste/selecao/hackaprompt-v3-regra-rev3.json` (ADR-0017).

## 3. Conjuntos publicos (RQ-05)

Nao redistribuidos (ADR-0016). Arquivos usados; o hash de todos os arquivos obtidos esta em `origem.json`.

| Conjunto | Origem | Versao | Obtido em | Arquivo usado | SHA-256 | Licenca |
|---|---|---|---|---|---|---|
| do-not-answer | `LibrAI/do-not-answer` | `74e74f2e4507ef256fe536f78a776f4a1ff67955` | 2026-09-11 | `data_en.csv` | `410449674780aa7304512043706f7981f666a79528d11546da34ebdd9595681c` | CC BY-NC-SA 4.0 (dados) / Apache-2.0 (codigo) |
| bipia | `https://github.com/microsoft/BIPIA.git` | `a004b69ec0dd446e0afd461d98cb5e96e120a5d0` | 2026-09-11 | `benchmark/text_attack_test.json` | `e828d3e9e273ddf43c4b0c91e5803998f4314555d865e32bd4e0903ab746a3b9` | MIT (Microsoft Corporation), com ressalva para tres conjuntos de terceiros em `benchmark` — ver "Licenca do BIPIA" em `ORIGEM.md` |
| hackaprompt | `hackaprompt/hackaprompt-dataset` | `25b87fbedfb86840abaf8cd09af7a029208a971a` | 2026-09-11 | `hackaprompt.parquet` | `bedca308fbd71be57793930e4e4a0dcfbda2a27b6d0f2ad3191bb20a6a315928` | MIT |

Dado pessoal: nenhum dado pessoal real nos 1.064 casos publicos (RQ-17, ADR-0024).
A restricao nao comercial do Do-Not-Answer acompanha o uso.

## 4. Rotulacao (RQ-04)

| Conjunto | Rotulo de origem | Mapeamento para o grupo | Autoria e data |
|---|---|---|---|
| Do-Not-Answer | `risk_area`, `types_of_harm` do proprio conjunto | NOC; nas 248 de *Information Hazards*, atributo `eixo_vazamento` | rotulo externo; mapeamento do autor, 08/10/2026 (ADR-0018) |
| BIPIA | categoria do proprio conjunto | INJ | rotulo externo; mapeamento do autor, 08/10/2026 |
| HackAPrompt, INJ-05 | `level` do proprio conjunto | INJ; estrato de codificacao pela R1 | estrato: classificacao do autor, rodadas 1 e 2 anotadas com assistencia de IA, quarta rodada sem divergencia, 08/10/2026 (ADR-0017) |
| HackAPrompt, CTX-02 | `level` 2 | CTX; criterio de extracao | desenho do autor, 08/10/2026 (ADR-0018) |
| Corpus de documentos | - | PII | desenho do autor; gerado em 28/10/2026 (ADR-0015) |
| Mensagens legitimas | - | sem grupo, `controle_legitimo` | redigidas a mao pelo autor, 29/10/2026 (ADR-0023) |

Criterio textual: `docs/mapeamento-rotulos.md`. **Classificador unico:** toda classificacao
propria foi feita por um so classificador, o autor, sem medida de concordancia entre anotadores;
limitacao declarada.

## 5. Recorte do CNPJ (RQ-03)

O CNPJ identifica **pessoa juridica** e nao e, por si, dado pessoal de pessoa natural. Permanece
no corpus como identificador estruturado brasileiro, com o recorte declarado (atributo
`natureza = pessoa_juridica`). Formatos suportados: **numerico e alfanumerico** (25 positivos de
cada), conferidos por `scripts/tests/test_suporte_cnpj.py` e pela implementacao independente
dos digitos verificadores (ADR-0015).

## 6. Metodo

Formulas: `docs/protocolo.md`, secao 8 (ADR-0020, D1 a D13). Condicoes: A sem protecao, B camada,
C Presidio com adaptacao minima para portugues (ADR-0022), D moderacao OpenAI (ADR-0006).
Versoes dos componentes: `docs/versoes.md`.

## 7. Fora da lista, e por que

- `assistente/fluxo.json`: cada exportacao do n8n gera de novo os identificadores e as
  posicoes dos nos, e o hash mudaria sem mudanca de comportamento. O fluxo e variavel de
  controle: o hash do fluxo usado e registrado em cada execucao, como o da colecao do
  Qdrant (ADR-0014).
- `docs/matriz_criterios.md`: recebe a coluna de resultado na Etapa 7. Os criterios
  ficam fixados pelos ADRs e por este registro; nenhum criterio muda depois desta data.

## 8. Ambiente de quem congelou

- Python 3.13.2; tabela Unicode `15.1.0`
  (classificacao R1, ADR-0017).
- `fastembed` 0.8.0 (recuperador; par modelo e versao
  da biblioteca como unidade de reproducao, ADR-0011).

