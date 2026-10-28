# ADR-0022 - Condicao C: Presidio com adaptacao minima para portugues (RQ-11)

## Contexto
O RQ-11 exige que o comparador esteja configurado para o idioma do experimento:
"comparar a camada em portugues com o comparador configurado para ingles invalida a
condicao C". O teste de fumaca da Etapa 0 enviou texto em portugues com
`language="en"` e comprovou apenas resposta HTTP.

Inspecao da imagem fixada (`ghcr.io/data-privacy-stack/presidio-analyzer@sha256:ae8f6f11...69885`),
em 14/10/2026, por comandos executados no conteiner:

| Fato | Evidencia |
|---|---|
| Presidio analyzer 2.2.364, instalado do codigo-fonte em `/app` (nao aparece no `pip list`) | `/app/pyproject.toml` |
| Configuracao ativa: `default_analyzer.yaml`, `default_recognizers.yaml`, `default.yaml` | variaveis `*_CONF_FILE` do conteiner |
| Unico modelo de linguagem: `en_core_web_lg` 3.8.0, sobre spaCy 3.8.13 | `pip list`, `spacy info` |
| Os tres arquivos declaram apenas `en`; limiar padrao `default_score_threshold: 0` | leitura dos arquivos |
| `language="pt"` e recusado: `{"error":"No matching recognizers were found to serve the request."}` | `GET /supportedentities?language=pt` |
| Em `en`, 19 entidades, nenhuma brasileira | `GET /supportedentities?language=en` |
| O reconhecedor de telefone inclui `BR` nas regioes padrao | `phone_recognizer.py:29` |
| O reconhecedor de entidades do spaCy e criado automaticamente para cada idioma do NLP | `recognizer_registry_provider.py:129` e `:180` |
| O inicio do conteiner nao baixa modelos: `entrypoint.sh` executa so o `gunicorn` | `cat /app/entrypoint.sh`, 28/10/2026 |

Ja estava registrado antes desta decisao que o Presidio nao reconhece documentos
brasileiros (proposta; `parecer-banca-resposta.md`; ADR-0015, cinco tipos como lacuna;
ADR-0020, D4).

## Decisao
A condicao C utiliza o Presidio Analyzer 2.2.364 com adaptacao minima de infraestrutura
e registro de idioma para aceitar portugues, preservando a logica e os parametros dos
reconhecedores existentes. Nao sao adicionados reconhecedores brasileiros nem realizados
ajustes com base nos resultados do conjunto de teste. As lacunas de cobertura
previamente declaradas permanecem no escopo da avaliacao.

Nome da condicao no texto: **Presidio com adaptacao minima para portugues** - nem
"Presidio padrao", nem "Presidio adaptado ao portugues".

O que muda, e nada alem disso (`presidio-analyzer/`):

| Item | Original | Condicao C |
|---|---|---|
| Modelo de linguagem | `en_core_web_lg` 3.8.0 | `pt_core_news_lg` 3.8.0, wheel do release oficial `explosion/spacy-models`, sha256 `2561c9a7...6191af`, conferido pelo pip na construcao |
| Idioma (NLP, analisador, registro) | `en` | `pt` |
| Reconhecedores registrados | os de `default_recognizers.yaml` para `en` | os **ativos no original e sem `country_code`**: CreditCard, Crypto, Date, Email, Iban, Ip, MacAddress, Phone, Url; mais o SpacyRecognizer, criado pelo proprio Presidio |
| Contexto dos reconhecedores | padrao da classe | igual (em ingles) |
| Mapeamento de entidades, rotulos ignorados, multiplicador de baixa confianca | `default.yaml` | identicos |
| Limiar | 0 | 0 |
| Parametros enviados na API | - | so `text` e `language="pt"`; sem `entities` nem `score_threshold` |
| Usuario, diretorio e comando de inicio | `1001`, `/app`, `./entrypoint.sh` | iguais |

Ficam fora os reconhecedores ativos com pais (EUA, Reino Unido, Espanha, Italia,
Polonia; o MedicalLicenseRecognizer e marcado `us`) e todos os desligados no original.

## Ressalvas declaradas
- `pt_core_news_lg` e o correspondente na familia spaCy do modelo usado em ingles, sem
  garantia de capacidade ou desempenho iguais. Licenca do modelo: CC BY-SA 4.0; fontes
  de treino UD Portuguese Bosque v2.8 e WikiNER (metadados da wheel).
- O modelo pt tem os rotulos PER, LOC, ORG e MISC, sem rotulo de data: em `pt`, data so e
  detectada pelo reconhecedor de padroes. ORG continua ignorado, como no original. MISC
  nao tem mapeamento no original e nenhum foi criado.
- Registrar um reconhecedor para `pt` nao traduz o seu comportamento. Os padroes sao os
  originais (exemplo: data por extenso em portugues nao e coberta), e o contexto continua
  em ingles. E limitacao funcional, nao cosmetica: o contexto participa do escore.
- Os resultados sustentam conclusoes sobre esta configuracao do Presidio, e nao sobre o
  desempenho maximo que ele poderia alcancar em portugues.
- O `en_core_web_lg` permanece instalado na imagem e nao e usado.

## Sanidade em portugues (28/10/2026)
`scripts/sanidade_presidio_pt.py` sobre os 353 textos do **conjunto de desenvolvimento**
(`conjunto_desenvolvimento/pii/corpus.jsonl`; o script recusa `conjunto_teste/`).
Registro bruto: `resultados/sanidade_presidio_pt_2026-10-28.json`.

- `GET /supportedentities?language=pt`: 12 entidades. `GET /recognizers?language=pt`:
  exatamente os 9 da lista mais o SpacyRecognizer.
- Resumo descritivo, nao e medicao do experimento:

| Tipo | Positivos inteiramente cobertos | Cobertura parcial | Negativos tocados |
|---|---|---|---|
| CNPJ | 7 / 50 | 8 | 8 / 50 |
| CNS | 1 / 50 | 0 | 2 / 50 |
| CPF | 6 / 50 | 0 | 10 / 50 |
| E-mail | 46 / 50 | 4 | 29 / 50 |
| PIS | 4 / 50 | 0 | 12 / 50 |
| Telefone | 50 / 50 | 0 | 8 / 50 |
| Titulo | 8 / 50 | 0 | 10 / 50 |

- As coberturas de CPF, PIS e titulo vem todas de `PHONE_NUMBER` (escore 0,4): o
  numero e lido como telefone, e nao reconhecido como documento. No CNPJ aparecem
  tambem `URL` e `LOCATION`, e no CNS um `CREDIT_CARD`. Fora do gabarito: 42 `PERSON` e
  3 `LOCATION` (nomes e lugares das frases).
- Tempo: cerca de 2 s por texto curto nesta maquina (intervalo entre requisicoes no
  `docker logs`). Registrado como dado; nenhuma configuracao foi alterada por isso.

O resultado confirma o que ja estava declarado antes da execucao: o Presidio cobre
telefone e e-mail e nao reconhece os documentos brasileiros como tais.

## Alternativas consideradas
- **Manter `language="en"` sobre texto em portugues.** Descartada: viola o RQ-11 e
  enfraquece o comparador por construcao.
- **Acrescentar reconhecedores brasileiros (CPF, CNPJ etc.) ao Presidio.** Descartada: a
  deteccao do comparador passaria a ser escrita pelo autor da camada, e o resultado
  mediria esse ajuste, e nao o Presidio; contradiz o registrado antes da execucao.
- **Traduzir o contexto dos reconhecedores para o portugues.** Uma traducao definida
  antes, sem consultar o corpus, poderia ser localizacao legitima; descartada para
  preservar o escopo de adaptacao minima, com a limitacao declarada.
- **Restringir entidades ou subir o limiar.** Descartada: restringir com base no corpus
  e ajustar o comparador ao conjunto.
- **Motor Stanza ou transformers para portugues.** Descartada: foge da configuracao
  padrao da ferramenta.
- **Volume com YAML e modelo baixado ao iniciar.** Descartada: cada inicio poderia baixar
  outra coisa; a imagem derivada deixa a configuracao versionada.

## Consequencia
A condicao C passa a ser executavel em portugues, com configuracao versionada e
conferida por `scripts/tests/test_presidio_pt.py`. A imagem do analyzer deixa de ser
usada diretamente e passa a ser construida (`build: ./presidio-analyzer`); o digest de
origem fica no `FROM`, conferido por `scripts/tests/test_imagens_fixadas.py`.

As deteccoes fora dos sete tipos (PERSON e outras) nao contam como falso positivo do
tipo (ii) do protocolo 8.4: revisao registrada na ADR-0020.

## Data
2026-10-14 (decisao); 2026-10-28 (implementacao e sanidade)

## Origem das ressalvas (registro de 28/10/2026)
As ressalvas incorporadas a esta decisao em 14/10/2026 - o nome "adaptacao minima", o
modelo pt como "correspondente" e nao "equivalente", a lista exata de reconhecedores, a
manutencao do contexto original, o conjunto de entidades originalmente ativo com o limiar
registrado como numero, e a separacao entre deteccao fora dos sete tipos e falso
positivo (ADR-0020, D8) - vieram de uma revisao feita pelo autor com **outra ferramenta
de IA**, e nao da orientacao. O autor avaliou e adotou cada ponto. Onde esta ADR e a
D8 dizem "revisao", e a essa revisao que se referem.
