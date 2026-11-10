# Plano de implementacao: Etapa 4 — Camada intermediaria

**Branch**: `main` | **Data**: 2026-11-09 | **Spec**: `specs/004-camada-intermediaria/spec.md`
**Decisoes**: ADR-0027 (E1 a E5)

## Resumo
Transformar o esqueleto da Etapa 0 (so encaminha) numa camada deterministica em tres
estagios — normalizacao, deteccao, decisao — sobre os tres pontos de interceptacao, com
mapa de posicoes para o texto original, mascaramento de dado pessoal confirmado por digito
verificador, deteccao de injecao sobre texto decodificado, contencao do marcador, registro
sem dado pessoal, falha fechada e um modo para a condicao D. A ordem de trabalho separa o
que pode ser feito **antes** do congelamento (contrato, limites, credenciais, fluxo) do que
so pode ser feito **depois** (as regras).

## Contexto tecnico
- **Linguagem**: Python 3.12 na imagem da camada (base fixada por digest); 3.13 na maquina
  de desenvolvimento.
- **Dependencias**: FastAPI, Pydantic, uvicorn (ja fixadas). Decodificacao com a biblioteca
  padrao (`base64`, `urllib.parse`, `unicodedata`). Cliente HTTP so no modo D.
- **Armazenamento**: nenhum; registro em JSON Lines.
- **Testes**: pytest, um arquivo por estagio, em `camada/tests/`.
- **Plataforma**: conteiner local, porta 8000.
- **Restricoes**: deterministica, sem modelo de linguagem; sem importar nada de `scripts/`
  (a regra R1 e o gerador do gabarito ficam de fora, ver "Independencia").
- **Escala**: 1.164 casos no fluxo, 355 textos no corpus, 30 repeticoes de latencia.

## Verificacao contra a constituicao

| Principio | Como este plano o cumpre |
|---|---|
| I. Congelamento antes das regras | Fase 0 so mexe em contrato, compose e fluxo. `normalizacao.py`, `deteccao.py` e `decisao.py` so sao criados depois de `CONGELADO.md`; `test_congelado.py` falha se existirem antes |
| II. Nenhum dado pessoal real | Exemplos de teste unitario gerados ou escritos; registro mascarado |
| III. Variaveis de controle fixas | O desvio por bloqueio entra no fluxo das quatro condicoes; o hash do fluxo e registrado na execucao |
| IV. Custo sob controle | A camada nao chama modelo de linguagem; o modo D chama so a moderacao, com chave criada quando for usada |
| V. Registro imutavel | Registro operacional da camada separado do registro bruto do executor |
| Fluxo, item 3 | Cada estagio com testes que passam antes do seguinte |

## Independencia entre a camada e o gabarito
- **Digito verificador**: a camada tem implementacao **propria**, em `camada/app/`, escrita a
  partir das regras oficiais documentadas na ADR-0015, e **nao importa**
  `scripts/dv_independente.py` nem a `validate-docbr`. Se a camada usasse o mesmo codigo que
  produziu o gabarito, um erro comum aos dois seria invisivel na medicao.
- **Normalizacao e decodificacao**: escritas do zero; a regra R1
  (`scripts/classificar_codificacao.py`) foi revisada sobre casos do conjunto de teste e
  nao entra na camada.

## Estrutura

```
camada/app/
  contrato.py        # Fase 0: posicao no texto original, limites, categoria de erro
  normalizacao.py    # Fase 1: remocao de invisiveis, variantes, mapa de posicoes
  documentos.py      # Fase 1: digitos verificadores proprios dos 5 documentos
  deteccao.py        # Fase 1: dado pessoal (7 tipos), injecao (sobre decodificado), marcador
  decisao.py         # Fase 1: politica por ponto, mascaramento, falha fechada
  moderacao.py       # Fase 2: modo D (/entrada)
  registro.py        # Fase 1: registro com texto mascarado
  main.py            # liga os estagios; modo sem normalizacao (ablacao)
camada/tests/        # um arquivo por estagio
assistente/fluxo.json  # Fase 0: desvio por decisao de bloquear
docker-compose.yml     # Fase 0: environment explicito da camada
```

## Fases
- **Fase 0 — antes do congelamento**: contrato (RQ-07 no contrato, RQ-14, categoria de erro),
  credenciais (RQ-15), desvio por bloqueio no fluxo (RF-013). Nenhuma regra.
- **Congelamento**: `python scripts/congelar.py --gravar`, depois do retorno do orientador.
- **Fase 1 — regras v0.1**: normalizacao com mapa; documentos; deteccao de dado pessoal;
  mascaramento e decisao; marcador; injecao com decodificacao; falha fechada; registro
  mascarado; modo de ablacao. Conferidas so contra `conjunto_desenvolvimento/`.
- **Fase 2 — modo D e demonstracao**: moderacao no `/entrada`; roteiro da demonstracao sem e
  com a camada, com exemplos do conjunto de desenvolvimento.

## Riscos
| Risco | Mitigacao |
|---|---|
| Prazo (24/11) | Fase 1 por prioridade da spec: P1 (dado pessoal e normalizacao) antes de P2 (injecao e marcador) |
| Congelamento atrasar por falta de retorno do orientador | Fase 0 inteira cabe antes; a Fase 1 e o caminho critico |
| Regra de injecao fraca | E resultado, nao defeito; expectativa declarada antes (ADR-0006 para D, ADR-0027 para NOC) |

## Complexidade
Nenhuma violacao da constituicao a justificar.
