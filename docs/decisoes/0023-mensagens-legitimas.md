# ADR-0023 - As 100 mensagens legitimas (tarefa 3.8)

## Contexto
As mensagens legitimas sao o controle de falso positivo (ADR-0018, papel
`controle_legitimo`; protocolo 8.3; ADR-0020, D2). O `docs/plano-de-corte.md`, item 3,
as coloca entre o que nao pode ser cortado e exige redacao manual: texto gerado
subestimaria a taxa de falsos positivos, que e a critica do trabalho a Alves et al.
(2025), cujo conjunto de mensagens seguras era inteiramente sintetico.

Na orientacao de 21/10/2026, o autor perguntou se poderia gerar as mensagens com IA,
revisando-as. O orientador aceitou, com a condicao de revisao uma a uma, e sugeriu
organiza-las em blocos por cenario, dando como exemplos ortografia ruim, cenario
corporativo e atendimento ao publico. Em 28/10/2026, diante do item 3 do plano de corte,
o autor decidiu **redigi-las a mao**, mantendo a organizacao em blocos.

## Decisao (do autor, 28/10/2026)
- **100 mensagens redigidas a mao pelo autor, sem IA**, em cinco blocos de 20:

| Bloco | Cenario | O que testa |
|---|---|---|
| 1 | Escrita informal: ortografia ruim, giria, abreviacao, ate 5 com emoji | se escrita fora do padrao e confundida com disfarce (ADR-0017) |
| 2 | Atendimento corporativo | vocabulario de compras e faturamento, com "cara" de documento, sem documento |
| 3 | Assuntos variados de atendimento | o atendimento comum, por variedade de assunto |
| 4 | Vocabulario sensivel em contexto legitimo | palavras associadas a ataque (senha, ignorar, codigo, sistema, hackeado), sem intencao maliciosa |
| 5 | Numeros do dia a dia | numeros comuns (pedido, CEP, rastreio, valores, datas) que nao sao documento |

  Os blocos 1 a 3 seguem os exemplos do orientador; os blocos 4 e 5 foram acrescentados
  pelo autor para cobrir as duas fontes mais provaveis de falso positivo da camada.
- **Regras escritas antes da redacao**, em `docs/guia-mensagens-legitimas.md`
  (commitado antes das mensagens): cenario da loja, o que e proibido e por que, numeros
  permitidos, os cinco blocos com exemplos de estilo. As proibicoes que evitam conflito
  com o resto do experimento: nenhum dos sete tipos de dado, nem inventado (mascara-lo
  seria correto e contaria como falso positivo); nenhuma sequencia de 10 ou mais
  digitos; nenhum pedido de dado de cadastro (grupos NOC e CTX); nenhuma ordem ao
  assistente para ignorar as proprias regras ou mostrar o prompt (injecao e extracao).
- **Conferencia so objetiva**, por `scripts/gerar_legitimas.py`: contagens, repeticao,
  endereco eletronico, sequencias de digitos, regra de colisao de documento e celular
  (ADR-0015), pedidos de 10001 a 10030, e nenhum texto igual a caso do teste ou do
  desenvolvimento. O script nao avalia estilo nem altera texto.
- O texto entra **exatamente como redigido**: erros de digitacao do bloco 1 sao
  propositais, e nos demais blocos sao os do cliente.

## Historico da redacao
- 28/10/2026: guia e modelo do arquivo commitados, antes da redacao.
- 29/10/2026, primeira entrega: 80 mensagens (blocos 2 a 5; o bloco 1 nao veio no
  arquivo). Revisao (por Claude, assistente de IA usado no desenvolvimento) contra as
  regras do guia: todas passavam, salvo a mensagem "Cadê as instruções?", ambigua entre
  instrucao do produto e instrucoes do assistente; e foi apontado que a serie tinha
  estrutura muito regular (mesma progressao de tamanho em todos os blocos, numeros de
  pedido em progressao aritmetica), caracteristica de texto gerado.
- 29/10/2026, segunda entrega: as 100 mensagens, com os blocos 2 a 5 reescritos pelo
  autor. Perguntado diretamente, o autor declarou que **foram escritas a mao**. E essa a
  versao que entra no conjunto de teste.

## Resultado
| Item | Valor |
|---|---|
| Texto redigido | `conjunto_teste/legitimas/mensagens.txt`, sha256 `cac860df6580c6e412eb79ab75c5138e25abe216264a40ca3d7ddf6ed0457f18` (LF) |
| Conjunto | `conjunto_teste/legitimas/mensagens.jsonl`, 100 registros (`leg-001` a `leg-100`), sha256 `93c90c5c1b6ca26a99fcb840eb0ff2b88d95b6d17428bbb533bcfcb232e0859d` |
| Conferencia | todas as regras objetivas do guia conferem |
| Mapeamento | 1.519 registros (100 com papel `controle_legitimo`), sha256 `12821338c19e9c43ef620d90cc06714753a49e0eb6577358a945c68415c8b053` |
| Separacao (RQ-06) | 1.518 casos distintos do teste contra 520 textos do desenvolvimento: 0 textos em comum |

## Alternativas consideradas
- **Gerar todas com IA e revisar** (o que a orientacao autorizou). Descartada pelo autor:
  contradiz o item 3 do plano de corte e enfraquece a critica a Alves et al.
- **Hibrido**: blocos 1 e 4 a mao, os demais gerados e revisados, com o falso positivo
  reportado por origem. Descartada pelo autor em favor da redacao integral a mao.

## Consequencia
O controle de falso positivo existe e entra no congelamento. A taxa de falso positivo
passa a ser reportada tambem por bloco, o que mostra onde a protecao atrapalha o
cliente. Limitacao declarada: 100 mensagens de um unico autor, num unico cenario de
loja; nao representam a variedade de clientes reais.

## Data
2026-10-28 (decisao e guia); 2026-10-29 (redacao e conversao)
