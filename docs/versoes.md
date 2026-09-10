# Versoes dos componentes

Coletado com `python scripts/coletar_versoes.py`, na maquina em que o experimento e
executado. Nenhum valor anotado de memoria: todos vieram da resposta do proprio
componente.

Equipamento: notebook Intel i5-13420H, 24 GB de memoria, Windows com WSL2.

| Coleta | Data |
|---|---|
| Etapa 0 | 2026-08-31 |
| Etapa 2 | 2026-09-10 |

## Ferramentas

| Componente | Versao |
|---|---|
| Windows | 10.0.26200.9168 |
| WSL | 2.7.3.0 |
| Docker Engine | 29.5.2 (build 79eb04c) |
| Docker Compose | v5.1.4 |
| Python | 3.13.2 |
| Git | 2.50.1.windows.1 |
| Spec Kit (specify-cli) | 1.0.2 |

O Spec Kit foi instalado com `uv tool install specify-cli`, o que exige o diretorio
de ferramentas do `uv` no PATH (`uv tool update-shell`). Registrado porque uma
dependencia que so funciona com PATH ajustado a mao precisa ser reproduzivel por
quem for repetir o procedimento.

O ambiente virtual de desenvolvimento fica fora da pasta do projeto, em
`%USERPROFILE%\venvs\tcc-camada`, para nao ser sincronizado pelo OneDrive. As
dependencias de teste estao em `requirements-dev.txt`.

## Imagens de conteiner

Todas fixadas por digest em `docker-compose.yml` e nos `Dockerfile`. Um digest
identifica os bytes exatos da imagem e nao muda; uma tag passa a apontar para outra
imagem a qualquer momento. Sem esse pin, o ambiente descrito aqui deixaria de ser o
mesmo que produziu os resultados.

| Imagem | Digest |
|---|---|
| docker.n8n.io/n8nio/n8n | `sha256:a9e2e3c8006ed453238266669ea1274be7136f515abe290a2f75a0ab9044c93d` |
| qdrant/qdrant | `sha256:057ee3a8da769fe7310dd3537b4dc7583bf87a95ce8ac43c0af5a46bc580d1fc` |
| ghcr.io/data-privacy-stack/presidio-analyzer | `sha256:ae8f6f111ac2f04e3fec552f7f80edd0dcbfa2dd69ee1b9e030475be31669885` |
| ghcr.io/data-privacy-stack/presidio-anonymizer | `sha256:e567013893ebc80994e3799f6f55c86aa1f0b0fadb779571ab346f0ec45365c1` |
| python (base da camada, do recuperador e do modelo) | `sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea` |

## Servicos

| Servico | Porta local | Papel no experimento |
|---|---|---|
| n8n | 5678 | Assistente de referencia (variavel de controle) |
| Qdrant | 6333 | Base de conhecimento indexada |
| Presidio analyzer | 5002 | Condicao C, eixo de saida |
| Presidio anonymizer | 5001 | Condicao C, eixo de saida |
| camada | 8000 | Condicao B, objeto avaliado |
| recuperador | 8100 | Parte do assistente: vetorizacao e busca |
| modelo | 8200 | Unico ponto do fluxo autorizado a chamar o modelo de linguagem |

Todas publicadas em `127.0.0.1`. Os conteineres conversam entre si pela rede interna
do Compose, pelo nome do servico.

## Bibliotecas Python

Fixadas por versao exata nos `requirements.txt` de cada servico. Resolucao verificada
por instalacao antes do commit.

| Pacote | Versao | Onde |
|---|---|---|
| fastapi | 0.115.6 | camada, recuperador, modelo |
| uvicorn[standard] | 0.34.0 | camada, recuperador, modelo |
| pydantic | 2.10.4 | camada, recuperador, modelo |
| pydantic-settings | 2.7.1 | camada |
| qdrant-client | 1.19.0 | recuperador |
| fastembed | 0.8.0 | recuperador |
| onnxruntime | 1.30.0 | recuperador (dependencia do fastembed) |
| anthropic | 0.69.0 | executor, modelo |
| httpx | 0.28.1 | executor |
| pandas | 2.2.3 | executor |
| matplotlib | 3.10.0 | executor |
| python-dotenv | 1.0.1 | executor |
| pytest | 8.3.4 | executor |
| faker | 40.38.0 | scripts (geracao de dados sinteticos) |
| validate-docbr | 2.0.0 | scripts, e testes de digito verificador |

## Modelo de embeddings

| Item | Valor |
|---|---|
| Identificador | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` |
| Dimensoes | 768 |
| Metrica de distancia | Cosseno |
| Tamanho | 1,0 GB |
| Licenca | Apache-2.0 |
| Execucao | CPU, local, sem chamada a servico externo |
| Confirmado em | 2026-09-10, por `TextEmbedding.list_supported_models()` |

**A unidade de reproducao e o par modelo mais versao da biblioteca, e nao o
identificador do modelo.** A biblioteca alterou a estrategia de agregacao dos
vetores de token — de vetor de classe para media —, de modo que o mesmo modelo
produz vetores diferentes conforme a versao do `fastembed`. Indices construidos com
versoes distintas nao sao comparaveis. Ver ADR-0011.

O modelo e baixado na **construcao** da imagem do recuperador, e nao em tempo de
execucao, para que a versao usada fique fixada pelo digest da imagem.

## Modelo de linguagem

| Item | Valor |
|---|---|
| Identificador | `claude-haiku-4-5-20251001` |
| Snapshot confirmado contra a API em | 2026-08-31 |
| Temperatura | 0 |
| Max tokens de saida | 400 |
| Preco de entrada | US$ 1,00 por milhao de tokens |
| Preco de saida | US$ 5,00 por milhao de tokens |
| Preco verificado em | 2026-08-31 |

### Custo unitario medido

| Medicao | Data | Entrada | Saida | Custo | Contexto |
|---|---|---|---|---|---|
| Teste de fumaca | 2026-08-31 | 836 | 162 | US$ 0,001646 | Documento sintetico de exemplo, k=3 |
| Primeira conversa ponta a ponta | 2026-09-10 | 1.041 | 71 | US$ 0,001396 | Base real, k=3, prompt de sistema definitivo |

A entrada subiu porque o contexto real e maior que o do teste de fumaca; a saida caiu
porque o prompt de sistema limita a resposta a tres frases. A projecao do ADR-0001
**nao foi recalibrada** com base nessas duas amostras: mensagens de ataque tendem a
produzir saidas de comprimento diferente, e o piloto do fim da Etapa 4, com 20
mensagens cobrindo os quatro grupos de criterios, e o que fixa o valor.

### Servico de moderacao (condicao D)

`omni-moderation-latest` e referencia mutavel. O executor gravara, em cada registro
bruto, o identificador de modelo devolvido pela propria resposta da API, e esse valor
sera transcrito para ca apos a execucao (RQ-16).

## Artefatos versionados com hash

| Artefato | Valor |
|---|---|
| Semente mestra | `20260829` |
| Hash do estado da base de conhecimento | `f118bb5851f1ce54d4053f8ca9b1eac5276cd0ca40bb006062436c343d60baa7` |
| Marcador unico do prompt de sistema | `CANARIO-TCC-2DEFEC2A9B0F` |
| Hash do prompt de sistema (16 primeiros digitos) | `5ab9ed98e5cde6da` |

Os hashes por arquivo dos 30 documentos estao em `base_conhecimento/MANIFESTO.md`.
O hash do prompt viaja em toda resposta do servico do modelo, ligando cada resultado
a versao do prompt que o produziu.
