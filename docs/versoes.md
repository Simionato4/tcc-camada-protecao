# Versoes dos componentes

Preencher com a saida de `python scripts/coletar_versoes.py`. Nao anote versao de
memoria: o que vale e o que a maquina responde, no dia da instalacao.

## Ferramentas

| Componente | Versao | Data |
|---|---|---|
| Windows | | |
| WSL | | |
| Docker Engine | | |
| Docker Compose | | |
| Python | | |
| Git | | |
| Spec Kit (specify-cli) | | |

## Imagens de conteiner

As tags em `docker-compose.yml` estao em `latest` ate esta tabela ser preenchida.
Depois de subir a primeira vez, copie o digest de cada imagem para ca e troque
`latest` pelo digest no compose. Sem isso o ambiente nao e reproduzivel por
terceiros, que e o que a proposta promete.

| Imagem | Digest | Data |
|---|---|---|
| docker.n8n.io/n8nio/n8n | | |
| qdrant/qdrant | | |
| ghcr.io/data-privacy-stack/presidio-analyzer | | |
| ghcr.io/data-privacy-stack/presidio-anonymizer | | |

## Bibliotecas Python

Fixadas em `camada/requirements.txt` e `executor/requirements.txt`.

## Modelo de linguagem

| Item | Valor |
|---|---|
| Identificador | (o valor de MODELO_ID no .env) |
| Temperatura | 0 |
| Max tokens de saida | 400 |
| Preco de entrada | US$ 1,00 / milhao de tokens |
| Preco de saida | US$ 5,00 / milhao de tokens |
| Preco verificado em | 2026-08-29 |
