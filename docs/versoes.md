# Versoes dos componentes

Coletado em **2026-08-31** com `python scripts/coletar_versoes.py`, na maquina em
que o experimento e executado. Nenhum valor foi anotado de memoria: todos vieram
da resposta do proprio componente.

Equipamento: notebook Intel i5-13420H, 24 GB de memoria, Windows com WSL2.

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

O Spec Kit foi instalado com `uv tool install specify-cli`, o que exige o
diretorio de ferramentas do `uv` no PATH (`uv tool update-shell`). Registrado aqui
porque uma dependencia que so funciona com PATH ajustado a mao precisa ser
reproduzivel por quem for repetir o procedimento.

O ambiente virtual de desenvolvimento fica fora da pasta do projeto, em
`%USERPROFILE%\venvs\tcc-camada`, para nao ser sincronizado pelo OneDrive.

## Imagens de conteiner

Fixadas por digest em `docker-compose.yml`. Um digest identifica os bytes exatos
da imagem e nao muda; uma tag como `latest` passa a apontar para outra imagem a
qualquer momento. Sem esse pin, o ambiente descrito aqui deixaria de ser o mesmo
que produziu os resultados.

| Imagem | Digest |
|---|---|
| docker.n8n.io/n8nio/n8n | `sha256:a9e2e3c8006ed453238266669ea1274be7136f515abe290a2f75a0ab9044c93d` |
| qdrant/qdrant | `sha256:057ee3a8da769fe7310dd3537b4dc7583bf87a95ce8ac43c0af5a46bc580d1fc` |
| ghcr.io/data-privacy-stack/presidio-analyzer | `sha256:ae8f6f111ac2f04e3fec552f7f80edd0dcbfa2dd69ee1b9e030475be31669885` |
| ghcr.io/data-privacy-stack/presidio-anonymizer | `sha256:e567013893ebc80994e3799f6f55c86aa1f0b0fadb779571ab346f0ec45365c1` |

## Bibliotecas Python

Fixadas por versao exata em `camada/requirements.txt` e
`executor/requirements.txt`. Resolucao verificada por instalacao antes do primeiro
commit.

| Pacote | Versao | Onde |
|---|---|---|
| fastapi | 0.115.6 | camada |
| uvicorn[standard] | 0.34.0 | camada |
| pydantic | 2.10.4 | camada |
| pydantic-settings | 2.7.1 | camada |
| anthropic | 0.69.0 | executor |
| httpx | 0.28.1 | executor |
| pandas | 2.2.3 | executor |
| matplotlib | 3.10.0 | executor |
| python-dotenv | 1.0.1 | executor |
| pytest | 8.3.4 | executor |

## Modelo de linguagem

| Item | Valor |
|---|---|
| Identificador | `claude-haiku-4-5-20251001` |
| Snapshot confirmado contra a API em | **2026-08-31** |
| Temperatura | 0 |
| Max tokens de saida | 400 |
| Preco de entrada | US$ 1,00 por milhao de tokens |
| Preco de saida | US$ 5,00 por milhao de tokens |
| Preco verificado em | 2026-08-31 |
| Custo unitario medido | **US$ 0,001646 por chamada** (836 tokens de entrada, 162 de saida) |

A confirmacao do snapshot e a medicao do custo foram feitas com
`python scripts/fumaca_modelo.py --real -n 3`, registrado em `docs/orcamento.md`.
Na mesma execucao, as tres respostas sairam identicas, o que da verificacao
preliminar a premissa de determinismo a temperatura zero (ver ADR-0004).
