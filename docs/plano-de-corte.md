# Plano de corte

Documento exigido pela recomendacao da banca de proposta: um plano de reducao de
escopo declarado **antes** de haver atraso, que preserve a validade cientifica.

## Por que declarar antes

Um corte decidido sob pressao de prazo tende a recair sobre o que e mais trabalhoso
de fazer, e nao sobre o que custa menos em validade. Declarar a ordem antes, com
gatilho objetivo, transfere a decisao do momento de panico para o momento de
projeto. Se um corte for acionado, ele e registrado em ADR e declarado nos
resultados.

## Principio de ordenacao

Corta-se primeiro o que reduz **precisao de estimativa**; por ultimo o que reduz
**fidelidade do cenario**. Nunca se corta o que sustenta a **validade interna** da
comparacao.

---

## Cortes, na ordem de acionamento

### C1 — Reduzir as repeticoes reais de LLM na condicao A

**Gatilho:** a Etapa 6 (execucao completa) ultrapassar 5 dias de trabalho.

**O corte:** as 3 repeticoes com chamada real ao modelo na condicao A, sobre os 248
casos do eixo de vazamento, passam a 1.

**Custo em validade:** a dispersao da contencao do modelo desprotegido deixa de ser
medida, e a premissa de determinismo a temperatura zero passa a ser assumida em vez
de verificada em escala. A verificacao preliminar de 31/08 — tres chamadas
identicas no teste de fumaca — passa a ser a unica evidencia dessa premissa, e a
limitacao e declarada.

**O que preserva:** todos os indicadores comparativos entre as quatro condicoes,
inclusive a Taxa de Compensacao, que continua calculavel sobre uma unica execucao.

**Economia:** 496 chamadas ao modelo e o tempo correspondente de execucao.

### C2 — Restringir o julgamento manual da condicao A

**Gatilho:** o julgamento manual das respostas da condicao A ultrapassar 4 horas.

**O corte:** o julgamento passa a cobrir apenas as 136 solicitacoes de vazamento de
informacao de organizacao ou governo, em vez das 248 da area completa.

**Custo em validade:** a Taxa de Compensacao passa a cobrir somente a categoria
diretamente comparavel a Alves et al. (2025), perdendo as 112 solicitacoes
relativas a privacidade de individuos, que sao as mais alinhadas ao foco do
trabalho em dados pessoais.

**O que preserva:** a comparabilidade com o trabalho de referencia, que e a
finalidade principal desse indicador.

**Observacao:** este corte ja estava previsto no plano de desenvolvimento e foi
formalizado em ADR-0005.

### C3 — Reduzir a amostra do HackAPrompt

**Gatilho:** a Etapa 6 ultrapassar 7 dias de trabalho, ou C1 ter sido acionado sem
recuperar o prazo.

**O corte:** a amostra estratificada de injecao direta passa de 40 para 20 casos,
mantida a estratificacao por tecnica de ofuscacao.

**Custo em validade:** a estimativa de bloqueio de injecao direta perde precisao, e
o criterio `INJ-05` — falsos negativos por tecnica de ofuscacao — passa a ter
estratos pequenos demais para leitura por tecnica, devendo ser reportado apenas de
forma agregada.

**O que preserva:** a presenca do eixo de injecao direta na comparacao.

### C4 — Substituir o n8n por cliente Python equivalente

**Gatilho:** a Etapa 2 (assistente de referencia) ultrapassar 6 dias de trabalho.

**O corte:** o fluxo do assistente deixa de ser montado em n8n e passa a ser um
cliente Python que executa a mesma sequencia — entrada, recuperacao, modelo, saida
— com os mesmos tres pontos de chamada a camada.

**Custo em validade:** o fluxo deixa de ser exportavel como definicao declarativa em
JSON, e a reproducao por terceiros passa a depender da leitura do codigo. A
variavel de controle permanece controlada, mas menos evidente para quem for
verificar.

**O que preserva:** integralmente o desenho experimental. Os tres pontos de
intercepcao, o prompt de sistema, a base de conhecimento e o modelo nao mudam.

**Observacao:** a mudanca e declarada nos resultados e nos recursos tecnologicos.

### C5 — Substituir a busca vetorial por busca por palavra-chave

**Gatilho:** a indexacao no Qdrant travar por mais de 2 dias de trabalho.

**O corte:** a recuperacao passa a ser por correspondencia de palavra-chave sobre os
30 documentos.

**Custo em validade:** o cenario perde fidelidade em relacao a implantacoes reais,
que usam busca vetorial. A decisao de modelo de embeddings deixa de existir.

**O que preserva:** a recuperacao deterministica dos documentos com carga do BIPIA,
que ja e garantida por pareamento entre pergunta e numero de pedido (ADR-0002), e
portanto nao depende do mecanismo de busca.

---

## O que nunca e cortado

Os itens abaixo sustentam a validade interna do experimento. Corta-los nao reduz o
escopo: invalida o trabalho.

1. **O congelamento datado do conjunto de teste antes da primeira regra**, e a
   proibicao de ajustar regra apos observar resultado.
2. **As quatro condicoes de comparacao.** Reduzir a tres elimina a comparacao que e
   o objeto da pesquisa.
3. **As 100 mensagens legitimas redigidas manualmente.** Substitui-las por texto
   gerado subestimaria a taxa de falsos positivos, que e precisamente a critica
   metodologica que este trabalho dirige a literatura.
4. **O corpus de 350 ocorrencias de documentos brasileiros.** E avaliado fora do
   fluxo do assistente, sem chamada ao modelo, entao nao pressiona nem prazo nem
   orcamento.
5. **A integridade do registro bruto.** Correcao gera nova execucao; registro nao
   se edita.
6. **A declaracao das limitacoes**, incluindo a restricao a ataques nao adaptativos.

## Resultado negativo

Registrado aqui por recomendacao expressa da banca: **desempenho ruim da camada e
resultado valido**. Se os indicadores mostrarem taxa alta de falsos positivos,
revocacao baixa de mascaramento ou contencao inferior a das ferramentas externas,
o resultado e reportado e discutido, nunca corrigido por ajuste de regra. Essa
possibilidade esta prevista desde o desenho e nao constitui falha do trabalho.

## Acionamento

Acionar um corte exige, na ordem: registrar o gatilho observado com a medida que o
disparou; abrir ADR com o corte adotado e a validade perdida; declarar a reducao no
capitulo de resultados e na apresentacao.

Nenhum corte foi acionado ate a data deste documento.
