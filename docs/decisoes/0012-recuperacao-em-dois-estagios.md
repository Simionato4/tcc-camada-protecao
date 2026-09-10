# ADR-0012 - Recuperacao em dois estagios: filtro exato mais similaridade

**Revisa o ADR-0002**, cuja premissa foi falsificada por medicao.

## Contexto

O ADR-0002 estabeleceu que a recuperacao do documento portador da carga de injecao
indireta seria garantida pareando a pergunta de teste ao numero de pedido do
documento, e afirmou que isso tornava a recuperacao "deterministica por
construcao".

A afirmacao nao foi verificada na ocasiao. Uma revisao externa dos artefatos, em
10/09/2026, observou que "perguntar pelo numero de pedido nao garante recuperacao
vetorial". A observacao foi classificada como ja coberta pelo ADR-0002 — o que
estava errado.

## Medicao

Primeira indexacao real, 10/09/2026, com
`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`, k=3, sobre os 30
documentos:

| Indicador | Resultado |
|---|---|
| Documento alvo no top-3 | **3 de 30** |
| Documento alvo em primeira posicao | 1 de 30 |
| Perguntas que devolveram o mesmo trio `doc-002`, `doc-020`, `doc-006` | 27 de 30 |

O ranking mostrou-se praticamente independente da pergunta.

**Causa.** Os 30 documentos tem estrutura e vocabulario quase identicos, variando
apenas em nomes, numeros e datas. Uma pergunta como "qual o status e a previsao de
entrega do pedido 10017" e dominada semanticamente por *status*, *previsao de
entrega* e *pedido*; o numero entra como poucos subtokens de peso desprezivel.
Todas as perguntas produzem vetores quase coincidentes, e o top-3 passa a ser o
mesmo conjunto, qualquer que seja o pedido citado.

Nao e defeito do modelo escolhido. Qualquer codificador denso apresentaria o mesmo
comportamento sobre um corpus deste formato: identificador exato nao e informacao
que embedding preserve.

## Decisao

A recuperacao passa a ter dois estagios:

1. **Filtro exato.** Se a pergunta cita um numero de pedido, o documento
   correspondente e recuperado por filtro sobre o campo `numero_pedido`, e nao por
   similaridade. O reconhecimento exige a palavra "pedido" nas proximidades do
   numero, para que CEP, telefone e valor monetario nao sejam confundidos com
   identificador de pedido.
2. **Complemento por similaridade.** As vagas restantes ate `k` sao preenchidas por
   busca vetorial, excluindo o documento ja trazido.

O contexto mantem sempre `k` documentos, como o ADR-0007 fixa, e o documento alvo
ocupa a primeira posicao de forma determinada. Perguntas que nao citam pedido
seguem usando apenas similaridade.

## Por que isso nao e um contorno

Sistemas reais de atendimento nao localizam um pedido por similaridade semantica:
extraem o identificador e consultam o registro. Buscar o pedido 10017 por
proximidade vetorial entre trinta registros de pedido quase identicos e que seria a
escolha irrealista — e a medicao acima e a evidencia disso.

A recuperacao passa a ser **hibrida**: filtro estruturado para o identificador,
busca vetorial para o restante. E o desenho corrente em assistentes de atendimento
com base de conhecimento, e o cenario fica mais fiel, e nao menos.

## Verificacao

O teste `recuperador/tests/test_recuperacao_pareada.py` substitui o modelo de
embeddings por um que devolve **o mesmo vetor para qualquer texto**, reproduzindo no
pior caso a falha medida. Nessas condicoes, as 30 perguntas pareadas recuperam seus
documentos, todas em primeira posicao.

A escolha do modelo degenerado e deliberada: um teste com o modelo real passaria por
sorte de ranking e nao demonstraria nada. Com ele, fica provado que a garantia do
pareamento **nao depende da qualidade dos embeddings**, que era exatamente o que o
ADR-0002 supunha sem verificar.

## Alternativas consideradas

**Aumentar k.** Nao resolve: o problema nao e a profundidade do ranking, e sim o
ranking ignorar o identificador. Com 27 perguntas devolvendo o mesmo trio, seria
preciso k proximo de 30 — o que anularia a recuperacao.

**Busca esparsa ou hibrida com BM25.** Melhoraria a correspondencia lexical do
numero, mas continuaria probabilistica, e acrescentaria um segundo modelo a fixar e
versionar. Filtro exato sobre campo estruturado e deterministico e mais simples.

**Diferenciar semanticamente os documentos** — produtos, cidades e situacoes
distintas — e formular perguntas que citem conteudo, e nao o numero. Tornaria a
recuperacao mais facil, mas por acaso: continuaria dependendo de o ranking acertar,
e teria de ser reverificada a cada mudanca no corpus.

**Injetar o documento alvo diretamente no contexto**, sem passar pela recuperacao,
nos casos de injecao indireta. Deterministico, mas retiraria a recuperacao do
cenario justamente nos casos em que ela e o vetor do ataque — a injecao indireta
existe porque o modelo le documentos recuperados.

## Consequencia

A garantia do ADR-0002 passa a existir de fato, e nao por suposicao. O executor
continua registrando o top-k de cada requisicao, e caso em que o documento alvo nao
foi recuperado permanece marcado como invalido e reportado a parte — a verificacao
nao e dispensada por haver filtro.

A recuperacao hibrida precisa ser descrita na monografia, na secao de descricao do
projeto, com a medicao que a motivou. O episodio tambem entra como registro de que
uma premissa de desenho foi falsificada por medicao antes do congelamento, e nao
depois — que e a diferenca entre um ajuste legitimo e um ajuste orientado ao
resultado.

**O ADR-0002 permanece no repositorio**, com nota apontando para este. Registro de
decisao nao se apaga: o que se aprendeu ao descobrir que ele estava errado e parte
do trabalho.

## Data
2026-09-10
