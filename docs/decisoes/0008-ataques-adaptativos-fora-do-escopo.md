# ADR-0008 - Ataques adaptativos ficam fora do escopo do TCC I

## Contexto
Durante a extracao dos controles do OWASP GenAI LLM Top 10 2026 para a matriz de
criterios, o controle de prevencao 11 do `LLM01:2026 Prompt Injection` (p. 15)
determina testar contra atacantes adaptativos e **rejeitar afirmacoes de sucesso
baseadas apenas em ataque estatico**, citando Nasr et al. (2025): sucesso estatico
proximo de zero contra sucesso adaptativo acima de 90% na maioria de doze defesas
recentes.

A proposta aprovada exclui ataques adaptativos e usa conjuntos publicados, isto e,
ataques estaticos. O referencial adotado no trabalho contesta esse tipo de
resultado quando apresentado sem qualificacao.

A analise de viabilidade esta em `docs/analise-ataques-adaptativos.md`, com quatro
niveis possiveis, custo e risco de cada um. Foi submetida ao orientador em
31/08/2026.

## Decisao
Orientacao do Prof. Me. Muriel Mazzetto, em 02/09/2026:

> Deixar escopo atual e colocar como sugestao de continuidade. Mostrar que teve
> contato e conhecimento sobre isso, dar a ideia de como pode ser abordado em
> trabalhos futuros, e deixar claro o escopo reduzido. Dai se ver que da tempo de
> abordar isso, ai faz no TCC II. Pra nao inflar demais a expectativa da banca ja.

Adotado o **nivel 0**, com tres obrigacoes decorrentes:

1. **Escopo em toda afirmacao de bloqueio.** Nenhum resultado e enunciado como
   "a camada bloqueia X%", e sim como "a camada bloqueia X% dos ataques publicados
   e nao adaptativos do conjunto congelado". Vale para tabelas, graficos, resumo e
   apresentacao.
2. **Limitacao declarada com fundamento normativo**, citando o controle 11 do
   LLM01:2026 e Nasr et al. (2025), e nao como ressalva generica.
3. **Trabalho futuro descrito com desenho concreto**, e nao como mencao vaga: o
   nivel 2 da analise — motor de mutacao deterministico sobre o corpus de
   documentos brasileiros — fica documentado como proposta executavel para o
   TCC II.

## Alternativa considerada
Incorporar o nivel 2 ao TCC I como secao exploratoria separada, restrita ao eixo
de dados pessoais, apos a execucao principal. Descartada por orientacao: acrescenta
um conjunto de teste ao escopo aprovado, custa cerca de uma semana de calendario
que o cronograma nao tem, e eleva a expectativa da banca sobre um resultado
secundario.

## Consequencia
O escopo aprovado permanece intacto e o cronograma nao muda. O trabalho demonstra
conhecimento da limitacao mais seria do seu proprio metodo, fundamentada na norma
que adota, sem prometer o que nao entrega. A continuidade em TCC II ganha um
desenho pronto em vez de uma intencao.

Custo: os indicadores de bloqueio ficam restritos a ataques nao adaptativos, e
essa restricao precisa estar visivel em toda apresentacao do resultado — inclusive
nos slides. Um numero apresentado sem o escopo, ainda que correto no texto, e
atacavel.

## Data
2026-09-09
