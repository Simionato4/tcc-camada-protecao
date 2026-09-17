# Procedencia dos conjuntos publicos

Gerado por `scripts/obter_conjuntos.py`. **Os conjuntos nao sao redistribuidos neste
repositorio** (ADR-0016): os arquivos ficam em `conjunto_teste/origem/`, fora do
versionamento. O que fica versionado e este registro e o `origem.json`, com o hash de
cada arquivo.

Para reconstruir:

```
python scripts/obter_conjuntos.py
python scripts/obter_conjuntos.py --conferir
```

O hash por arquivo tambem detecta se a fonte alterou o conteudo depois do
congelamento: a divergencia aparece na conferencia, em vez de passar despercebida.

## do-not-answer

| Item | Valor |
|---|---|
| Origem | `LibrAI/do-not-answer` |
| Versao | `74e74f2e4507ef256fe536f78a776f4a1ff67955` |
| Data de obtencao | 2026-09-11 |
| Licenca | CC BY-NC-SA 4.0 (dados) / Apache-2.0 (codigo) |
| Acesso | publico |
| Papel no experimento | Solicitacoes nocivas — grupos NOC e PII |
| Arquivos | 11 |

Maiores arquivos (hash completo em `origem.json`):

| Arquivo | Bytes | SHA-256 |
|---|---|---|
| `data_en.csv` | 3,912,791 | `410449674780aa73...` |
| `data/train-00000-of-00001-6ba0076b818accff.parquet` | 1,709,142 | `cc03d6e34df834c4...` |
| `assets/radar_plot.png` | 455,238 | `931fb46c161f442c...` |
| `assets/dna.png` | 409,691 | `8e6192dcc6a37361...` |
| `assets/action.png` | 248,555 | `f1037830797b05b3...` |
| `assets/instruction_dist.png` | 129,648 | `759be460916c6fb1...` |
| `assets/action_dist.png` | 44,815 | `f326083a9ddc64b1...` |
| `assets/auto_eval.png` | 34,442 | `2bfad6762e091e5e...` |
| `assets/harmful_num.png` | 13,680 | `9edebefa4520ec19...` |
| `README.md` | 4,181 | `b0e3ec62f87b1e52...` |
| `.gitattributes` | 2,307 | `f4e703ea6e44bbeb...` |

## hackaprompt

| Item | Valor |
|---|---|
| Origem | `hackaprompt/hackaprompt-dataset` |
| Versao | `25b87fbedfb86840abaf8cd09af7a029208a971a` |
| Data de obtencao | 2026-09-11 |
| Licenca | MIT |
| Acesso | restrito — exige aceite das condicoes e token de leitura |
| Papel no experimento | Injecao direta — grupo INJ |
| Arquivos | 3 |

Maiores arquivos (hash completo em `origem.json`):

| Arquivo | Bytes | SHA-256 |
|---|---|---|
| `hackaprompt.parquet` | 150,419,795 | `bedca308fbd71be5...` |
| `README.md` | 5,555 | `627ac0ec7ebfcb5b...` |
| `.gitattributes` | 2,438 | `5d4d3015ba3d332a...` |

## bipia

| Item | Valor |
|---|---|
| Origem | `https://github.com/microsoft/BIPIA.git` |
| Versao | `a004b69ec0dd446e0afd461d98cb5e96e120a5d0` |
| Data de obtencao | 2026-09-11 |
| Licenca | MIT (Microsoft Corporation), com ressalva para tres conjuntos de terceiros em `benchmark` — ver "Licenca do BIPIA" abaixo |
| Acesso | publico |
| Papel no experimento | Injecao indireta — grupo INJ |
| Arquivos | 99 |

Maiores arquivos (hash completo em `origem.json`):

| Arquivo | Bytes | SHA-256 |
|---|---|---|
| `benchmark/table/train.jsonl` | 1,639,381 | `495491f72a499bf7...` |
| `benchmark/table/test.jsonl` | 183,402 | `b84d81e80f5ab9e3...` |
| `benchmark/code/train.jsonl` | 125,976 | `d7644a1e49688384...` |
| `benchmark/code/test.jsonl` | 100,501 | `70fb021fd4977c62...` |
| `NOTICE.md` | 59,893 | `39732640c4798db5...` |
| `benchmark/email/train.jsonl` | 31,636 | `0130a694116e295d...` |
| `benchmark/email/test.jsonl` | 30,384 | `2d71aae20a843730...` |
| `bipia/metrics/regist.py` | 23,315 | `908670766b632166...` |
| `defense/white_box/finetune.py` | 20,037 | `36930b3eb0ee636f...` |
| `examples/collect_clean_response.py` | 19,350 | `1c3ebb4a8dbffc8a...` |
| `defense/black_box/few_shot.py` | 17,027 | `a7233246e95bbd88...` |
| `examples/run.py` | 16,832 | `3968253de93c6d33...` |
| `benchmark/code_attack_test.json` | 16,427 | `ab9f0563c7674074...` |
| `benchmark/code_attack_train.json` | 16,414 | `ab13b6cf99afd82a...` |
| `demo.ipynb` | 15,198 | `4990388f0c7b78c6...` |

## Licenca do BIPIA — reconciliada em 2026-09-17

Lida no arquivo `LICENSE` da versao obtida (`a004b69ec0dd446e0afd461d98cb5e96e120a5d0`),
e nao na descricao do repositorio.

O repositorio e **MIT, Microsoft Corporation**, com uma ressalva textual:

> NOTE: This license applies to all parts of this repository except for the datasets
> specified below. See the respective datasets for their individual licenses.

Os conjuntos de terceiros excetuados estao em `benchmark` e sao **tres, nomeados um a um**:

| Componente | Licenca declarada | Onde |
|---|---|---|
| WikiTableQuestions | CC BY-SA 4.0 | tarefa TableQA |
| Stack Exchange (100 questoes do Stack Overflow) | CC BY-SA 4.0 | tarefa CodeQA |
| Invoices data do OpenAI Evals | MIT | — |

**O que este trabalho usa:** apenas `benchmark/text_attack_test.json`, o arquivo de cargas
de ataque de texto — 75 cargas em 15 categorias (ADR-0014). Esse arquivo **nao e** nenhum
dos tres componentes de terceiros nomeados: e contribuicao propria do BIPIA. Pela leitura
do texto da licenca, a ressalva e delimitada por componente, e nao pelo diretorio inteiro;
do contrario os arquivos de ataque ficariam sem licenca alguma, o que contraria a propria
frase "See the respective datasets for their individual licenses", que pressupoe
conjuntos identificados. **Conclusao adotada: MIT.**

**Ressalva registrada.** A conclusao acima e leitura do texto da licenca, feita pelo autor
com apoio de assistente, e nao parecer juridico. O proprio arquivo `LICENSE` adverte que o
usuario deve consultar a fonte original de cada conjunto. Se a monografia afirmar algo
sobre a licenca, convem submeter a redacao ao orientador.

**Nao ha redistribuicao.** Os arquivos de origem ficam fora do versionamento (ADR-0016),
de modo que a questao relevante e o **uso**, nao a redistribuicao. MIT e CC BY-SA 4.0
permitem o uso feito aqui.

### O clone do BIPIA e incompleto por construcao

`benchmark/qa` e `benchmark/abstract` **nao contem** os arquivos de contexto
`test.jsonl` e `train.jsonl`. O proprio repositorio declara o motivo — "Due to the license
issue" — e fornece `process.py`, `index.json` e `md5.txt` para que o usuario os gere a
partir do NewsQA e do XSum.

Isso **nao bloqueia este trabalho**: as cargas do BIPIA sao embutidas nos 30 documentos
sinteticos proprios (ADR-0002, ADR-0014), e os arquivos de contexto do BIPIA nao sao
usados. Fica registrado porque a contagem de 99 arquivos, acima, poderia sugerir que o
conjunto foi obtido completo.

## Licencas

Confirme na pagina de cada fonte, no dia do download. A restricao nao comercial do
Do-Not-Answer acompanha o uso e precisa ser declarada na monografia, junto a
referencia do conjunto.
