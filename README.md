# Camada intermediaria de protecao de entrada e saida em assistentes conversacionais com modelos de linguagem

Avaliacao comparativa com foco em dados pessoais brasileiros.

**Gabriel Simionato** — Bacharelado em Sistemas de Informacao, Centro Universitario Mater Dei (UNIMATER), Pato Branco/PR
**Orientador:** Prof. Me. Muriel Mazzetto
**Entrega do TCC I:** 24/11/2026

---

## O que este repositorio contem

Uma camada intermediaria que intercepta a comunicacao de um chatbot em tres
pontos — mensagem do usuario, conteudo recuperado da base de conhecimento e
resposta gerada — decidindo entre encaminhar, bloquear, mascarar e alertar.

A camada e comparada com outras tres condicoes sob o mesmo conjunto de teste
congelado. **O produto final nao e a camada. E a evidencia quantitativa
comparativa.** A camada e o instrumento.

| Condicao | Ferramenta | Eixo de atuacao |
|---|---|---|
| A | nenhuma | linha de base |
| B | camada deste trabalho | entrada, contexto e saida |
| C | Presidio | saida |
| D | moderacao de conteudo | entrada |

## Estado atual

Etapas 0 (ambiente), 1 (matriz de criterios) e 2 (assistente de referencia) concluidas.
Etapa 3 (conjunto de teste) pronta para o congelamento: 1.519 casos mapeados
(`conjunto_teste/selecao/mapeamento_rotulos.json`), formulas fechadas
(`docs/protocolo.md`, secao 8) e o congelamento preparado em `scripts/congelar.py`.
As decisoes estao em `docs/decisoes/` (ADR-0000 a ADR-0025).

A camada **ainda encaminha e nada mais**. Nao existe regra de deteccao neste
repositorio, e nenhuma pode existir antes do congelamento: os arquivos
`normalizacao.py`, `deteccao.py` e `decisao.py` so sao criados na Etapa 4, depois de
`conjunto_teste/CONGELADO.md` estar datado e com hash (`scripts/tests/test_congelado.py`
falha se existirem antes).

## Como subir o ambiente

Pre-requisitos: Windows com WSL2 e Docker Desktop usando o backend WSL2.

```bash
cp .env.example .env          # no PowerShell: copy .env.example .env
# preencha ANTHROPIC_API_KEY no .env

docker compose up -d --build
python scripts/verificar_servicos.py
```

O ambiente inteiro sobe com um comando. `verificar_servicos.py` confere que os sete
servicos respondem.

| Servico | Porta local |
|---|---|
| n8n | 5678 |
| Qdrant | 6333 |
| Presidio Analyzer | 5002 |
| Presidio Anonymizer | 5001 |
| Camada | 8000 (documentacao em `/docs`) |
| Recuperador | 8100 |
| Modelo (unico ponto que chama o modelo de linguagem) | 8200 |

O Presidio analyzer e construido a partir da imagem fixada, com adaptacao minima para
portugues (`presidio-analyzer/`, ADR-0022). Versoes e digests: `docs/versoes.md`.

## Testes

```bash
python -m venv %USERPROFILE%\venvs\tcc-camada     # fora da pasta sincronizada pelo OneDrive
%USERPROFILE%\venvs\tcc-camada\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q --import-mode=importlib
```

Nenhum teste chama API paga: todos rodam com `MODO_SIMULADO=1`.

## Orcamento da API

O credito e finito e um laco mal fechado inviabiliza o trabalho. Por isso:

- nenhum modulo chama o modelo fora de `executor/cliente_modelo.py`;
- toda chamada passa pelo `GuardaOrcamento`, com teto de chamadas e teto em dolares;
- `MODO_SIMULADO=1` e o padrao — gastar exige gesto explicito (`--real`);
- o consumo acumulado fica em `resultados/consumo.json`, somando todas as execucoes.

Plano de chamadas e projecao de custo: `docs/orcamento.md` e ADR-0001.

## Regras permanentes

1. Conjunto de teste congelado, datado e com hash **antes** da primeira regra da camada.
2. Regra nunca e ajustada a um caso do conjunto congelado. Apos a execucao, desempenho ruim e resultado, nao defeito.
3. Nenhum dado pessoal real, em nenhuma etapa. Os documentos brasileiros, a base de conhecimento e as mensagens legitimas sao sinteticos ou redigidos pelo autor; os conjuntos de ataque publicos sao prompts reais publicados, verificados quanto a dado pessoal (RQ-17, ADR-0024).
4. Modelo unico, snapshot travado, temperatura zero.
5. Ataques apenas contra este ambiente local.
6. O fluxo do assistente e variavel de controle: identico nas quatro condicoes, com os tres nos HTTP presentes desde a condicao A.
7. Latencia medida dentro da camada. Tempo de rede fora da metrica.
8. Registro bruto nunca e editado. Correcao gera nova execucao.
9. Todo codigo que chama o modelo tem teto de chamadas, modo simulado e contador.
10. Toda aleatoriedade usa a semente registrada em `.env` (`SEMENTE_MESTRA`).
11. Escopo fechado. O que for relevante e estiver fora dele vira trabalho futuro.

## Estrutura

```
specs/               artefatos do Spec Kit, por etapa
docs/decisoes/       ADRs, um arquivo por decisao relevante
docs/versoes.md      versao exata de cada componente, coletada por comando
docs/orcamento.md    plano de chamadas e consumo medido
camada/              servico Python da condicao B
assistente/          fluxo n8n exportado e prompt de sistema versionado
base_conhecimento/   30 documentos sinteticos
conjunto_teste/      ataques, mensagens legitimas, corpus de PII e CONGELADO.md
executor/            executor do protocolo e guarda de orcamento
resultados/          registros brutos, nunca editados
analise/             notebooks e tabelas finais
scripts/             verificacao de servicos, coleta de versoes, teste de fumaca
```

## Metodologia

GitHub Spec Kit. Cada etapa produz especificacao, plano tecnico e lista de
tarefas em markdown, versionados aqui. Decisoes tecnicas relevantes viram ADR em
`docs/decisoes/` no mesmo dia.

## Licenca

MIT. Os conjuntos de ataque utilizados mantem as licencas de origem, registradas
em `conjunto_teste/`.
