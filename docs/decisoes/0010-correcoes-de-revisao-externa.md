# ADR-0010 - Correcoes decorrentes de revisao externa dos artefatos

## Contexto
Em 10/09/2026, os artefatos do projeto foram submetidos a uma revisao independente,
que os conferiu contra os documentos normativos originais e contra o codigo. A
revisao identificou erros factuais, criterios que prometiam mais do que verificam,
defeitos latentes de desenho e incoerencias de configuracao.

Parte das observacoes foi verificada contra as fontes e confirmada; parte foi
recusada. Este ADR registra ambas.

## Decisao

### Correcoes de erro factual, confirmadas contra as fontes

| Erro | Verificacao | Correcao |
|---|---|---|
| Sintese da matriz declarava 9 medicoes, 3 inspecoes e 2 testes unitarios | Contagem linha a linha: 10, 3 e 1 | Sintese corrigida |
| Extracao NIST declarava 21 acoes e tabulava 18, com tres "absorvidas" sem identificacao | Reexecucao da selecao: ausentes `MS-2.3-002`, `MS-2.6-002`, `MS-2.7-002`, nunca examinadas | As tres foram examinadas e classificadas; todas `fora`. Enumeracao completa |
| Descricao de `MS-2.6-001` pertencia a `MS-2.6-002` | Conferida no PDF | Ambas corrigidas |
| `INJ-04` media BIPIA na condicao D | ADR-0001 exclui essa combinacao | Criterio corrigido: BIPIA em A e B; HackAPrompt em A, B e D |
| `TETO_CHAMADAS=4500` nao comportava as duas reexecucoes que o ADR-0001 afirmava caber | 2 x 3.883 = 7.766 | Teto elevado para 8.500; teto em dolares mantido como limite efetivo |

A causa dos tres primeiros e a mesma: a secao 3 do NIST AI 600-1 e composta de
tabelas, e a extracao de texto do PDF desloca e perde conteudo entre linhas
adjacentes. A licao foi registrada na extracao: conferencia por identificador, um a
um, e igualdade entre itens selecionados e itens tabulados antes de concluir.

### Criterios reclassificados por prometerem mais do que verificam

| Criterio | De | Para | Motivo |
|---|---|---|---|
| `PII-01` | avaliado | parcial | O controle pede padrao **mais** reconhecimento de entidade **mais** classificadores treinados. A camada substitui os dois ultimos por validacao de digito verificador. O enunciado anterior reescrevia o controle numa versao que a camada cumpre |
| `PII-02` | avaliado | parcial | Avaliacao fora do fluxo mede capacidade de deteccao, nao posicao do filtro. Acrescentada verificacao de integracao como evidencia obrigatoria |
| `CTX-02` | avaliado | parcial | A ausencia do marcador nao comprova confidencialidade do prompt inteiro nem controle de comportamento critico. Conclusao restrita a exposicao do marcador |
| `PII-04` | parcial | parcial, com restricao ampliada | O controle trata de higienizacao do corpus na ingestao; a camada atua na recuperacao. Momentos distintos |

Sintese apos a reclassificacao: dos quatorze criterios, cinco integrais e nove
parciais. A proporcao e desconfortavel e esta correta.

O erro em `PII-01` merece registro explicito porque e o mesmo que a metodologia
deste trabalho existe para evitar, cometido na direcao oposta: em vez de ajustar a
solucao ao criterio, ajustou-se o criterio a solucao.

### Precisao de afirmacoes

- A proporcao "14 de 54 controles" mede a fracao do referencial que o protocolo
  consegue verificar. **Nao mede reducao de risco**, e a monografia nao a
  apresentara como tal.
- A restricao "somente dados sinteticos" passa a ser "nenhum dado pessoal real".
  Os conjuntos de ataque publicados sao prompts reais, nao texto sintetico.
- "Resultado estatico como limite superior" e substituido por conclusao restrita:
  o experimento nao demonstra robustez diante de adversarios adaptativos.
- Mutacao por operador fixo e distinguida de ataque adaptativo no texto de
  trabalhos futuros.

### Correcoes de codigo e de configuracao

| Item | Correcao |
|---|---|
| Guarda de orcamento | Passa a **reservar** o custo estimado da proxima chamada antes de autoriza-la, em vez de constatar o estouro depois |
| Portas | Publicadas em `127.0.0.1`, e nao em todas as interfaces. O isolamento do laboratorio e o controle declarado no trabalho, e convem que exista de fato |
| Imagem base da camada | `python:3.12-slim` incluida na coleta de digest, como as quatro imagens de servico |
| Servico de moderacao | `omni-moderation-latest` e mutavel; o identificador devolvido pela resposta passa a ser gravado em cada registro |

### Distincao entre defeito e ajuste, na constituicao

O principio V determinava que correcao gera nova execucao, sem distinguir defeito
de instrumentacao de ajuste orientado ao resultado. Passa a distinguir: defeito
identificavel independentemente do resultado autoriza nova execucao, com ambas
preservadas e o motivo registrado; alteracao motivada pela observacao do resultado
permanece proibida sem excecao.

### Requisitos herdados

Vinte requisitos que nasceram desta revisao e do parecer da banca, mas serao
cumpridos em etapas posteriores, foram registrados em `docs/requisitos-herdados.md`
com dono, gatilho e criterio de aceitacao. Nenhuma etapa fecha com requisito
herdado em aberto.

Os de maior impacto: gabarito com negativos dificeis (RQ-02); mapeamento de
posicoes entre texto normalizado e original (RQ-07); rubrica unica de sucesso entre
condicoes (RQ-09); e configuracao do comparador adequada ao portugues (RQ-11).

## Recusado

**Recentrar o trabalho em mascaramento, rebaixando injecao a avaliacao secundaria.**
O diagnostico e correto — uma camada de regras nao possui mecanismo semantico
contra injecao, e a matriz declara isso em quatro de cinco criterios do grupo. A
prescricao, porem, confunde duas coisas: o trabalho nao afirma que a camada derrota
injecao, e sim que mede comparativamente quatro condicoes. Constatar que uma camada
de regras tem desempenho baixo contra injecao e resultado valido, e e exatamente a
evidencia que a justificativa promete produzir para quem precisa escolher uma
estrategia. Alem disso, a proposta foi aprovada com nota maxima em coerencia entre
objetivos, metodologia e projeto, e o escopo foi mantido por decisao do orientador
em duas ocasioes.

**Cortar as 939 solicitacoes do Do-Not-Answer, a condicao D e a Taxa de
Compensacao.** O conjunto integral e o que sustenta a comparabilidade com Alves et
al. (2025), um dos dois pilares da justificativa. O problema real apontado e de
julgamento, nao de conjunto, e foi tratado como tal em RQ-09.

**Acrescentar uma pergunta de pesquisa formal.** O modelo institucional adota
objetivo geral e objetivos especificos, ja mensuraveis.

**Autenticacao na camada e chave no Qdrant.** O controle declarado e isolamento de
laboratorio, agora efetivo pela publicacao em `127.0.0.1`. Autenticacao nao
acrescenta validade ao experimento e consumiria prazo.

## Consequencia
Cinco erros factuais corrigidos, quatro criterios reclassificados para baixo,
quatro afirmacoes tornadas precisas e quatro correcoes de codigo e configuracao. A
matriz passa a prometer menos e a verificar o que promete.

Custo: nenhum em prazo — as correcoes foram feitas em um dia, antes do inicio da
Etapa 2. Os vinte requisitos herdados acrescentam trabalho as Etapas 3, 4 e 5, com
destaque para o gabarito com negativos dificeis e a rubrica unica de sucesso, que
sao substanciais e precisam entrar no planejamento dessas etapas.

## Data
2026-09-10
