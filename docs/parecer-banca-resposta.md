# Resposta aos pareceres da banca de proposta

**Aluno:** Gabriel Simionato · **Data:** 10/09/2026
Pareceres recebidos de tres avaliadores. Resultado: duas aprovacoes e uma aprovacao
com ajustes.

## Leitura das notas

| Criterio | Av. 1 | Av. 2 | Av. 3 |
|---|---|---|---|
| Clareza e delimitacao do problema | 3 | 3 | 3 |
| Relevancia e justificativa | 3 | 3 | 3 |
| Coerencia entre objetivos, metodologia e projeto | 3 | 3 | 3 |
| **Viabilidade tecnica e temporal** | 3 | **2** | 3 |
| Resultados esperados e validacao | 3 | 3 | 3 |
| Fundamentacao e potencial academico | 3 | 3 | 3 |

Dezessete notas 3 e uma nota 2. A unica nota abaixo do maximo, em toda a planilha,
esta em viabilidade — e as observacoes escritas dos tres avaliadores convergem para
o mesmo ponto. Um deles resume: *"o risco do trabalho e de execucao, nao de
concepcao"*, e *"nao ha correcoes conceituais a fazer"*.

Este documento mapeia cada recomendacao ao seu estado atual e a acao decorrente.

---

## Recomendacoes ja atendidas antes do parecer

Tres recomendacoes foram cumpridas durante a Etapa 0, concluida em 31/08/2026,
antes do recebimento dos pareceres.

### R1. Fechar a selecao das ferramentas o quanto antes — caminho critico

> *"A proposta ainda apresenta n8n, Python, Presidio e servicos de moderacao como
> em avaliacao. Considerando a concentracao de trabalho em outubro e novembro, esta
> decisao e caminho critico."*

**Atendida integralmente.** Todas as ferramentas estao fechadas, instaladas,
funcionando e versionadas:

| Componente | Escolha | Estado |
|---|---|---|
| Assistente | n8n em conteiner | Fixado por digest, respondendo |
| Camada | Python 3.12 + FastAPI | Esqueleto com os tres endpoints, 28 testes passando |
| Base vetorial | Qdrant | Fixado por digest, respondendo |
| Deteccao de dados pessoais | Presidio analyzer e anonymizer | Fixados por digest, respondendo |
| Moderacao (condicao D) | OpenAI, endpoint gratuito | ADR-0006 |
| Modelo | `claude-haiku-4-5-20251001` | Snapshot confirmado contra a API |

O ambiente inteiro sobe por um comando, com as quatro imagens fixadas por digest
SHA-256 — nao por tag — de modo que o ambiente de novembro seja o mesmo de agosto.
Versao de cada componente em `docs/versoes.md`, obtida por comando.

### R2. Congelar o corpus antes da implementacao e nao ajustar as regras

> *"Congelar o corpus antes da implementacao, como previsto, e nao ajustar as
> regras com base nos resultados do conjunto de teste. O resultado negativo tambem
> deve ser tratado como resultado valido."*

**Atendida, com mecanismo de verificacao.** A regra deixou de ser intencao e virou
estrutura, em tres camadas:

1. **Constituicao do projeto** (`.specify/memory/constitution.md`), lida pela
   metodologia adotada antes de cada especificacao. O primeiro principio, marcado
   como nao negociavel, determina o congelamento datado com hash antes da primeira
   regra, e proibe alterar regra apos observar o resultado. A governanca do
   documento veda relaxar principio nao negociavel apos a data de congelamento.
2. **Ausencia fisica dos modulos.** Os arquivos `normalizacao.py`, `deteccao.py` e
   `decisao.py` nao existem no repositorio e so serao criados apos o
   `CONGELADO.md` estar datado.
3. **Rastreabilidade por versao de regra.** Toda resposta da camada e todo registro
   bruto carregam o campo `versao_regras`, hoje em `0.0.0-encaminhamento`. Permite
   reconstruir qual configuracao gerou cada medida, e a comparacao com a data do
   congelamento e verificavel por terceiros no historico do repositorio.

Quanto ao resultado negativo: a constituicao registra que, apos a execucao,
desempenho ruim e resultado a reportar, e nao defeito a corrigir.

### R3. Tratar o repositorio como entrega, versionado desde o inicio

> *"O repositorio publico com especificacao, requisitos, plano tecnico, tarefas e
> criterios de aceitacao e um diferencial do trabalho e nao apenas um anexo.
> Mantenha-o versionado desde o inicio e nao deixe para organiza-lo no final."*

**Atendida.** Repositorio publico desde o primeiro dia de desenvolvimento, com o
historico de commits preservando a ordem em que o trabalho ocorreu — o que e, em
si, a evidencia de que o congelamento precedeu as regras. Metodologia GitHub Spec
Kit instalada, com constituicao preenchida. Decisoes tecnicas registradas em ADR no
mesmo dia, oito ate agora.

---

## Recomendacoes acatadas, com acao decorrente

### R4. Definir a quantidade de repeticoes antes da execucao

> *"A proposta menciona numero da repeticao no registro e desvio-padrao entre
> repeticoes nos resultados, mas nao fixa o valor. Sugere-se declara-lo desde ja e
> inclui-lo entre os itens que o plano de contencao pode reduzir."*

**Acatada.** O valor foi definido em 29/08 (ADR-0001 e ADR-0004) e agora e
declarado no protocolo:

| Medicao | Repeticoes | Justificativa |
|---|---|---|
| Chamadas ao modelo, condicoes A, B e D | 1 por caso | A temperatura e zero e a resposta e determinstica; verificado empiricamente no teste de fumaca |
| Chamadas ao modelo, condicao A, eixo de vazamento (248 casos) | 3 por caso | A contencao depende de o modelo desprotegido recusar, e a Taxa de Compensacao depende desse valor. Serve tambem de verificacao da premissa de determinismo |
| Latencia interna da camada | 30 por caso | A camada e local e deterministica; repetir nao custa credito. Mede ruido de maquina, que e o que a metrica deve capturar |

A escolha de nao repetir chamadas ao modelo em todas as condicoes decorre da
definicao de latencia adotada: o tempo medido e o interno da camada, e repetir a
chamada ao modelo para obter dispersao de um tempo que nao inclui o modelo
consumiria credito sem acrescentar informacao.

Conforme sugerido, as repeticoes entram no plano de corte, como primeiro item.

### R5. Registrar tempo interno e tempo total separadamente

> *"Registre as duas grandezas separadamente desde a primeira execucao (tempo
> interno da camada e tempo total da requisicao) e reporte ambas, porque a
> diferenca entre elas e informacao util para quem for adotar a solucao."*

**Acatada, e e a recomendacao que mais melhora o trabalho.** O protocolo previa
apenas o tempo interno, para evitar contaminacao por variabilidade de rede. A
observacao inverte o raciocinio: a diferenca entre as duas grandezas nao e ruido a
descartar, e sim o custo real de adocao.

Passa a valer, desde a primeira execucao:

| Grandeza | Onde e medida | O que informa |
|---|---|---|
| `tempo_ms` | Dentro da camada, envolvendo apenas o processamento | Custo computacional da estrategia, comparavel entre condicoes |
| `tempo_total_ms` | No executor, envolvendo a requisicao HTTP inteira | Custo de adocao, incluindo transporte |

Ambos gravados em todo registro bruto e reportados em p50 e p95.

Beneficio adicional nao previsto: a condicao C usa o Presidio em conteiner e a
condicao D usa servico externo, e em nenhuma das duas existe tempo interno
separavel do transporte. Com as duas grandezas registradas, a comparacao entre as
quatro condicoes passa a ser feita sobre `tempo_total_ms`, que existe para todas, e
o `tempo_ms` fica como decomposicao da condicao B. Isso resolve uma inconsistencia
do protocolo original, que definia a latencia de um modo impossivel de aplicar as
condicoes externas.

### R6. Registrar o criterio de rotulacao do conjunto de teste

> *"Registrar como cada mensagem foi classificada em sua categoria de risco e quem
> fez a classificacao. Como o conjunto sera congelado, o criterio precisa estar
> documentado junto com ele."*

**Acatada.** Entra na Etapa 3, junto ao congelamento. O `CONGELADO.md` passa a
conter, para cada conjunto:

- a rotulacao de origem, quando existir — Do-Not-Answer traz 12 tipos de dano,
  BIPIA traz 15 categorias e HackAPrompt traz a tecnica de cada caso;
- o **mapeamento** de cada rotulo de origem para os quatro grupos da matriz de
  criterios (`INJ`, `PII`, `CTX`, `NOC`), que e classificacao do autor e nao da
  fonte;
- o criterio textual que orientou cada mapeamento;
- a autoria e a data da classificacao, com a declaracao de que foi feita por um
  unico classificador, limitacao ja declarada para as mensagens legitimas.

Essa recomendacao tem relacao direta com um achado da Etapa 1: das 939 solicitacoes
do Do-Not-Answer, 248 pertencem a area de vazamento e as 691 restantes nao se
encaixam em nenhuma das tres categorias do recorte original — o que motivou a
criacao do quarto grupo de criterios. Sem o mapeamento documentado, essa decisao
ficaria invisivel.

### R7. Documentar versao e data de obtencao dos conjuntos publicos

> *"Documentar a versao exata dos conjuntos publicos utilizados (Do-Not-Answer,
> BIPIA, HackAPrompt) e a data de obtencao, junto ao congelamento."*

**Acatada.** O padrao ja esta em uso: os dois documentos normativos da Etapa 1
foram registrados com versao, data de publicacao, data de acesso e hash SHA-256.
O mesmo se aplica aos tres conjuntos de ataque, com o acrescimo do identificador de
commit ou de versao do repositorio de origem e da licenca de cada um.

### R8. Reforcar na redacao dos resultados o rigor da comparacao entre ferramentas de finalidades distintas

> *"A proposta ja registra corretamente que cada ferramenta externa participa apenas
> dos criterios do eixo em que atua; reforce esse ponto na redacao dos resultados
> para evitar leitura equivocada em banca."*

**Acatada, com providencia anterior a execucao.** Alem de reforcar na redacao, a
expectativa de desempenho de cada ferramenta externa foi **registrada antes da
execucao**, o que impede que o resultado seja lido como descoberta:

- Presidio: espera-se baixo reconhecimento de documentos brasileiros, por ausencia
  de reconhecedores para esse contexto — ja declarado na propria proposta.
- Moderacao: espera-se desempenho baixo em injecao de instrucao, porque servicos de
  moderacao classificam categorias de dano e nao injecao — registrado em ADR-0006,
  em 29/08.

Na matriz de criterios, cada linha declara em quais condicoes e avaliada, de modo
que nenhuma ferramenta aparece medida fora do seu eixo.

### R9. Plano de reducao de escopo declarado antecipadamente

> *"Recomendo definir antecipadamente um plano de reducao de escopo que preserve a
> validade cientifica caso o cronograma aperte."*

**Acatada.** O plano de desenvolvimento ja previa cortes, mas de forma dispersa e
sem gatilho numerico. Foi consolidado em documento versionado,
`docs/plano-de-corte.md`, com ordem de acionamento, gatilho objetivo para cada
corte, o que cada um custa em validade e o que nunca e cortado.

---

## Sobre a amplitude do escopo

> *"Ha risco de o trabalho tentar avaliar simultaneamente prompt injection, indirect
> prompt injection, vazamento de contexto, PII brasileira, moderacao, guardrails e
> latencia. O proprio projeto ja identifica o volume de execucao como risco."*

A observacao procede e e a origem da unica nota 2. A resposta tem tres partes.

**Primeira: parte do risco ja foi retirada.** Tres fontes de incerteza que pesavam
sobre o cronograma foram eliminadas na Etapa 0. As ferramentas estao fechadas e
funcionando. O custo do experimento foi medido, e nao estimado: US$ 0,001646 por
chamada, projetando US$ 6,39 para as 3.883 chamadas do plano, contra os US$ 12
estimados na proposta — deixando margem para duas reexecucoes completas, o que
importa porque registro bruto nao se edita. E o ambiente inteiro sobe por um
comando, com versoes congeladas.

**Segunda: um eixo ja foi retirado do escopo.** Durante a Etapa 1, o referencial
adotado mostrou que resultados obtidos apenas com ataques estaticos devem ser
qualificados, o que abria a possibilidade de incorporar avaliacao adaptativa. Sob
orientacao, a avaliacao adaptativa foi mantida fora do TCC I e registrada como
continuidade, com desenho executavel descrito (ADR-0008). Foi uma decisao de nao
inflar o escopo diante de um argumento normativo que o justificaria.

**Terceira: reduzir mais agora seria prematuro.** O que resta do escopo esta
integralmente ancorado nos objetivos especificos da proposta aprovada, e cortar um
eixo antes de haver evidencia de atraso trocaria um risco de prazo por uma perda
certa de resultado. O plano de corte com gatilhos numericos existe exatamente para
essa decisao ser tomada com dado, e nao com receio — que e o que a propria
recomendacao pede ao falar em preservar a validade cientifica.

Uma providencia adicional, sugerida pelo terceiro avaliador, reduz o risco mais que
qualquer corte antecipado: **antecipar o piloto**. O plano previa execucao de teste
com 20 mensagens dentro da Etapa 5. Passa a ser executado ao fim da Etapa 4, assim
que a camada tiver a primeira versao funcional, ainda que com uma fracao do
conjunto. O piloto revela problemas de instrumentacao — formato de registro,
medicao de tempo, tratamento de erro de API — enquanto ha tempo de corrigi-los, e
custa cerca de US$ 0,14 em credito.

---

## Sintese das alteracoes

| # | Recomendacao | Estado | Onde |
|---|---|---|---|
| R1 | Fechar selecao de ferramentas | Ja atendida | `docs/versoes.md`, `docker-compose.yml` |
| R2 | Congelar antes, nao ajustar regras | Ja atendida | Constituicao, `versao_regras` |
| R3 | Repositorio como entrega | Ja atendida | Repositorio publico |
| R4 | Fixar numero de repeticoes | Acatada | `docs/protocolo.md`, `docs/plano-de-corte.md` |
| R5 | Registrar tempo interno e total | Acatada | `docs/protocolo.md`, contrato da camada |
| R6 | Criterio de rotulacao junto ao congelamento | Acatada, Etapa 3 | `conjunto_teste/CONGELADO.md` |
| R7 | Versao e data dos conjuntos publicos | Acatada, Etapa 3 | `conjunto_teste/CONGELADO.md` |
| R8 | Rigor na comparacao entre ferramentas | Acatada | Matriz de criterios, ADR-0006 |
| R9 | Plano de reducao de escopo antecipado | Acatada | `docs/plano-de-corte.md` |
| — | Antecipar o piloto para o fim da Etapa 4 | Acatada | `docs/protocolo.md` |

Nenhuma recomendacao foi recusada.
