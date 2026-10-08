# ADR-0018 - Mapeamento dos rotulos de origem para os grupos da matriz

## Contexto
O RQ-04 exige registrar, junto ao congelamento, a rotulacao de origem de cada conjunto, o
mapeamento de cada rotulo para os quatro grupos da matriz (INJ, PII, CTX, NOC), o
criterio textual, a autoria e a data.

Tres ambiguidades apareceram ao abrir a tarefa 3.4:

1. Os quatro grupos sao **grupos de criterios**, e cada criterio ja declara seu conjunto
   de medicao. O mapeamento do RQ-04 e de outra natureza: procedencia e relato de cada
   caso.
2. As 248 solicitacoes da area *Information Hazards* do Do-Not-Answer cabiam em dois
   grupos. `conjunto_teste/ORIGEM.md` declarava o papel do conjunto como "grupos NOC e
   PII", e a ADR-0005 justifica as 248 pelo foco em dados pessoais. Mas nenhum criterio
   PII mede o Do-Not-Answer: PII-01 a PII-04 medem o corpus sintetico e os registros da
   camada, e PII-05 inspeciona o prompt de sistema. O NOC-01 mede as 939.
3. O `CTX-02` mede "os casos de tentativa de extracao", e nenhum documento declara qual
   conjunto os fornece.

## Decisao
Decisao do autor, 08/10/2026.

**Grupo primario unico.** Cada caso do conjunto de teste tem exatamente um grupo primario
e zero ou mais atributos secundarios. Os atributos sao registrados e nao entram na
contagem por grupo. E o mesmo padrao de R1 para casos mistos (ADR-0017): precedencia, e
registro das caracteristicas secundarias.

| Conjunto | Grupo primario | Atributos secundarios |
|---|---|---|
| Do-Not-Answer (939) | NOC | `risk_area` e `types_of_harm` de origem; nas 248 de *Information Hazards*, `eixo_vazamento` = `organizacao_governo` (136) ou `privacidade_individuo` (112) |
| HackAPrompt (40) | INJ | `level` de origem; estrato de codificacao (ADR-0017) |
| BIPIA, ataques de texto (75) | INJ | categoria de origem |
| Corpus de documentos (350 positivos e negativos dificeis) | PII | tipo de documento, natureza, classe de negativo (tarefas 3.5 e 3.6) |
| Mensagens legitimas (100) | nenhum: papel `controle_legitimo` | definidos na tarefa 3.8 |

As mensagens legitimas nao pertencem a um grupo de risco: sao o controle de falso
positivo de todos eles. Por isso o esquema distingue `papel` (`caso_de_risco` ou
`controle_legitimo`) de `grupo_primario`.

**Natureza do rotulo.** Cada registro declara `origem_rotulo`:
- `externa`: o rotulo vem do proprio conjunto publico;
- `propria`: o rotulo e o desenho deste trabalho (corpus de documentos, mensagens
  legitimas, e o estrato de codificacao do HackAPrompt).

**Onde fica.**

| Artefato | Papel |
|---|---|
| `conjunto_teste/selecao/mapeamento_rotulos.json` | autoridade legivel por maquina, um registro por caso, sem texto (ADR-0016) |
| `docs/mapeamento-rotulos.md` | criterio textual por rotulo, autoria, data e decisoes de fronteira |
| `conjunto_teste/CONGELADO.md` (tarefa 3.11) | a secao exigida pelo RQ-04, que **referencia o JSON pelo hash** em vez de transcreve-lo |

O `CONGELADO.md` nao transcreve a tabela porque transcricao manual e onde o erro entra
neste projeto (ADR-0017, incidentes de manuseio). Hash confere; copia, nao.

**Papel do Do-Not-Answer corrigido** em `scripts/obter_conjuntos.py`, em
`conjunto_teste/ORIGEM.md` e em `conjunto_teste/origem.json`, por substituicao pontual do
mesmo texto nos tres. O `ORIGEM.md` **nao e regenerado**: ele contem a reconciliacao da
licenca do BIPIA, escrita a mao em 17/09/2026, que o script nao produz.

**CTX-02:** o conjunto de medicao e determinado pelo inventario dos rotulos de origem
(`scripts/inventariar_rotulos.py`) e registrado em bloco proprio desta ADR. Se nenhum
conjunto fornecer casos de tentativa de extracao, o criterio segue a regra da propria
matriz para criterio sem metodo.

## Alternativa considerada
**Pertencimento multiplo declarado:** as 248 em NOC e PII ao mesmo tempo. Defensavel, mas
todo total por grupo precisaria da nota de que os grupos nao somam o total de casos, e a
sobreposicao teria de ser declarada caso a caso. Descartada por tornar ambigua cada
tabela de resultado, sem medir nada a mais: o eixo de vazamento continua disponivel como
atributo, que e o que o corte C2 e a Taxa de Compensacao usam.

## Consequencia
Contagem por grupo sem ambiguidade. A ADR-0005 continua valida: as 248 entram, e o
recorte 136 / 112 fica registrado como atributo. O que muda e so a declaracao de grupo.

Custo: o `ORIGEM.md` e o script divergem quanto a licenca do BIPIA, e essa divergencia
precisa ser resolvida antes do congelamento sem regenerar o arquivo.

## Data
2026-10-08
