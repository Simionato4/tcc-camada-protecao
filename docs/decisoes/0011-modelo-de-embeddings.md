# ADR-0011 - Modelo de embeddings e local da recuperacao

## Contexto
O plano de desenvolvimento deixou o modelo de embeddings em aberto, para decidir na
Etapa 2, antes de indexar. A decisao trava a indexacao e, uma vez indexado o corpus,
troca-la obriga a reindexar tudo.

Duas escolhas estao acopladas: qual modelo, e onde a vetorizacao roda.

## Criterio de escolha
O criterio **nao e qualidade de recuperacao**, e isso precisa estar claro. Pelo
ADR-0002, a recuperacao do documento que carrega a carga de injecao indireta e
garantida por pareamento entre a pergunta de teste e o numero de pedido do
documento. Com isso, a qualidade da busca vetorial deixa de ser variavel medida, e
a comparacao entre modelos de embeddings esta explicitamente fora do escopo do
trabalho.

Sobre um corpus de 30 documentos, qualquer codificador multilingue competente
recupera corretamente. O criterio real e: execucao local, peso aberto, suporte a
portugues, fixavel por versao e licenca compativel com repositorio publico.

## Decisao

**Modelo:** `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

| Item | Valor |
|---|---|
| Dimensoes | 768 |
| Tamanho | 1,0 GB |
| Licenca | Apache-2.0 |
| Execucao | CPU, local, sem chamada a servico externo |
| Biblioteca | `fastembed` 0.8.0, com `onnxruntime` 1.30.0 |

Identificador, dimensao, tamanho e licenca **confirmados contra a propria
biblioteca**, e nao contra documentacao, por chamada a
`TextEmbedding.list_supported_models()` em 10/09/2026.

**Justificativa citavel.** O MTEB-BR, benchmark de embeddings para portugues
brasileiro (arXiv 2607.04581), reporta que os codificadores multilingues gerais
alcancam media 0,517 nas tarefas de recuperacao, contra 0,331 dos modelos de
linguagem mascarada especificos para portugues, e situa o
`paraphrase-multilingual-mpnet-base-v2` (278M de parametros) entre os competitivos.
O mesmo trabalho registra que qualidade de embedding em portugues nao exige
interface de programacao comercial — o que sustenta a escolha por modelo de peso
aberto e execucao local, coerente com a restricao de ambiente isolado.

**Local da recuperacao:** servico proprio, separado da camada.

Um segundo servico Python expoe `POST /buscar`, que vetoriza a pergunta e consulta
o Qdrant. O fluxo n8n apenas faz a chamada HTTP.

## Alternativas consideradas

**`intfloat/multilingual-e5-large`** (1024 dimensoes, 2,24 GB, licenca MIT). Lidera
o benchmark para portugues. Descartado por custo sem contrapartida mensuravel: mais
lento em CPU, mais pesado para indexar, e a recuperacao ja e deterministica por
construcao. Adotar o modelo mais forte sugeriria que a qualidade da recuperacao
importa para o resultado, o que induziria leitura equivocada.

**`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** (384 dimensoes,
220 MB). Suficiente para 30 documentos e o mais rapido. Descartado por ser o mais
dificil de defender: nao ha evidencia especifica para portugues que o sustente.

**Nos nativos de embedding do n8n.** Menos codigo. Descartado porque o modelo
passaria a ser configurado dentro do fluxo, e a reprodutibilidade dependeria da
versao dos nos do n8n, que nao esta registrada em `docs/versoes.md`. Alem disso,
manteria a recuperacao acoplada a ferramenta de orquestracao, que e a candidata a
substituicao no corte C4 do plano de corte.

**Recuperacao dentro da camada.** Descartada por contaminacao de medida: a camada e
o objeto avaliado na condicao B, e sua latencia interna e um indicador do trabalho.
Acrescentar vetorizacao e consulta ao Qdrant dentro dela tornaria o `tempo_ms`
incomparavel com as demais condicoes.

## Consequencia

O ambiente ganha um quinto servico, `recuperador`, que precisa entrar no
`docker-compose.yml`, no `scripts/verificar_servicos.py` e em `docs/versoes.md`,
com a imagem fixada por digest como as demais.

O modelo e baixado na construcao da imagem, e nao em tempo de execucao, para que o
ambiente continue subindo por um comando e para que a versao baixada fique fixada
pelo digest da imagem. Isso acrescenta cerca de 1 GB a imagem do recuperador.

Trocar o modelo depois da indexacao obriga a reindexar o corpus inteiro; depois do
congelamento do conjunto de teste, obriga tambem a nova execucao do protocolo.

## Data
2026-09-10
