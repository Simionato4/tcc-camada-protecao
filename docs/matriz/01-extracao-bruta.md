# Etapa 1 — Extracao bruta e classificacao de escopo

Tarefas 1.3, 1.4 e 1.5. Insumo para a conversao em criterios (tarefa 1.6).

**Fontes**
- OWASP GenAI LLM Top 10 2026, v1.0, 03/08/2026. Entradas `LLM01:2026` (p. 10),
  `LLM02:2026` (p. 18) e `LLM08:2026` (p. 46), secoes "Prevention and Mitigation
  Strategies".
- NIST AI 600-1, jul. 2024. Secao 3, funcao MEASURE, acoes etiquetadas com
  `Information Security` ou `Data Privacy`: 21 de 72 acoes MEASURE.

**Criterio de classificacao.** Um controle e marcado `avaliado` somente se ao menos
uma metrica que o protocolo produz o verifica. As metricas disponiveis sao: taxa de
bloqueio por categoria de risco; taxa de falsos positivos sobre as mensagens
legitimas; taxa de falsos negativos; precisao e revocacao do mascaramento por tipo
de documento; taxa de compensacao; latencia interna em p50 e p95; e retencao do
prompt de sistema verificada por marcador unico.

Controle sem metrica correspondente e marcado `fora`, com motivo. Nao ha categoria
intermediaria silenciosa: `parcial` significa avaliado sob restricao declarada.

---

## Correspondencia de identificadores

O recorte da proposta foi redigido antes da publicacao da versao 2026. A tabela
abaixo fixa a correspondencia.

| Categoria de risco da proposta | Identificador 2026 | Observacao |
|---|---|---|
| Injecao de instrucao, direta e indireta | `LLM01:2026 Prompt Injection` | Posicao inalterada em relacao a 2025 |
| Divulgacao de informacao sensivel | `LLM02:2026 Sensitive Information Disclosure` | Posicao inalterada |
| Exposicao de contexto interno | `LLM08:2026 Hidden Context Exposure` | Era `LLM07 System Prompt Leakage` em 2025; renomeado, ampliado e movido para a 8a posicao |

O `LLM08:2026` e mais amplo que vazamento de prompt de sistema: abrange esquemas de
ferramentas, texto de politica recuperado e regras de configuracao. Exclui
explicitamente o vazamento de dados de usuario, que permanece no `LLM02:2026`. O
recorte da proposta — retencao do prompt de sistema sob tentativa de extracao — e
subconjunto delimitado do `LLM08:2026`.

---

## OWASP LLM01:2026 Prompt Injection — 11 controles (p. 13 a 15)

| # | Controle (resumo) | Escopo | Metrica ou motivo |
|---|---|---|---|
| 1 | Restringir papel e capacidades no prompt de sistema, com declaracoes de permissao e negacao | parcial | Presente no prompt de sistema, identico nas 4 condicoes. Verificado pela taxa de contencao da condicao A, em que a recusa depende so do modelo. O proprio controle se declara parcial |
| 2 | Definir esquema de saida estrito e valida-lo em codigo confiavel | fora | Validacao de esquema de saida e `LLM10:2026`, excluido do recorte |
| 3 | Filtrar em toda fronteira de modalidade, nao so texto | parcial | Apenas texto. Ataques multimodais estao explicitamente fora do escopo da proposta |
| 4 | Manter credenciais e capacidade de mudanca de estado no codigo, com menor privilegio | fora | O assistente nao expoe ferramentas nem executa acoes privilegiadas |
| 5 | Remover blocos de tag (U+E0000–E007F), seletores de variacao (U+FE00–FE0F) e largura zero (U+200B, U+200C, U+200D, U+2060) em toda fronteira | **avaliado** | Especificacao direta de `normalizacao.py`. Verificado pela revocacao da deteccao sobre casos com caracteres invisiveis. Ressalva da propria norma: nao detem carga em texto visivel |
| 6 | Passar conteudo externo por canal separado e rotulado por procedencia | **avaliado** | O ponto de intercepcao de contexto e esse canal. Verificado pelo bloqueio de injecao indireta na condicao B contra a condicao A |
| 7 | Exigir confirmacao humana antes de acao privilegiada ou irreversivel | fora | Nao ha acao privilegiada no cenario |
| 8 | Orcar capacidades do agente pela Regra de Dois | fora | O assistente nao e agentico |
| 9 | Tratar escrita em memoria do agente como operacao privilegiada | fora | Ausencia de historico entre requisicoes e variavel de controle do experimento |
| 10 | Fixar, assinar e verificar servidores MCP e pacotes de ferramentas | fora | `LLM04:2026`, fora do recorte; nao ha ferramentas |
| 11 | Testar contra atacantes adaptativos e rejeitar afirmacao so-estatica | **fora, declarado** | Ver ADR-0008. Fundamenta a limitacao e o trabalho futuro |

Nota da propria entrada (p. 13): nao existe hoje mecanismo confiavel de prevencao
de injecao, e a defesa e arquitetural, nao interceptiva. Esse trecho sustenta o
enunciado dos criterios desta categoria: mede-se reducao de sucesso, nao prevencao.

---

## OWASP LLM02:2026 Sensitive Information Disclosure — 19 controles em 3 niveis (p. 20 e 21)

### Nivel 1 — fundacional

| # | Controle (resumo) | Escopo | Metrica ou motivo |
|---|---|---|---|
| 1 | Governar corpora: procedencia, classificacao, deduplicacao; remover PII na ingestao | parcial | A base e sintetica e contem PII deliberada. A remocao na ingestao corresponde ao ponto de contexto. Verificado pela revocacao do mascaramento no contexto |
| 2 | Minimizar contexto: enviar so campos necessarios | fora | `k=3` e fixo por desenho (ADR-0007), variavel de controle e nao variavel medida |
| 3 | Autorizar antes da recuperacao, no nivel de documento e de trecho | fora | O cenario simulado nao possui modelo de autorizacao por usuario |
| 4 | Higiene do prompt de sistema: nunca armazenar segredo nele | **avaliado** | O prompt contem apenas o marcador unico, nao segredo. Verificado pela severidade declarada da exposicao de contexto |
| 5 | Sanitizar com classificadores, nao so regex, porque regex falha em saida codificada e multilingue | **avaliado — central** | E a questao central do trabalho: regex mais digito verificador contra a abordagem por reconhecedores. Verificado por precisao e revocacao por tipo de documento, camada contra Presidio |
| 6 | Orcar consultas por usuario e por sessao em endpoints sensiveis | fora | Nao ha enumeracao nem sondagem de pertencimento no desenho |
| 7 | Higiene operacional: restringir e higienizar registros e rastros | **avaliado** | A camada mascara os proprios registros. Verificado pela contagem de documentos nao mascarados nos registros da camada |

### Nivel 2 — endurecimento

| # | Controle (resumo) | Escopo | Motivo |
|---|---|---|---|
| 1 | DP-SGD calibrado, com sobreajuste monitorado | fora | Atua no treinamento; o modelo e consumido como servico |
| 2 | Protecao do armazenamento vetorial: cifragem, ACL, exportacao restrita | fora | Infraestrutura; nao ha adversario com acesso ao Qdrant no cenario |
| 3 | Restringir log-probabilidades, confianca e explicacoes | fora | Nao expostos pelo desenho |
| 4 | Classificar e redigir rastros de raciocinio como saida de primeira classe | fora | O modelo empregado nao expoe rastro de raciocinio no fluxo montado |
| 5 | Defesas de canal lateral: preenchimento aleatorio, lotes de tokens, cache particionado | fora | Canais laterais de inferencia estao fora do recorte |
| 6 | Cifragem que preserva formato, com separacao de rota interna e externa | fora | Nao ha rota externa distinta no cenario |
| 7 | Registro de auditoria integrado a SIEM, DLP e AI-SPM continuos | fora | Infraestrutura organizacional |

### Nivel 3 — avancado

| # | Controle (resumo) | Escopo | Motivo |
|---|---|---|---|
| 1 | Computacao confidencial ou inferencia com preservacao de privacidade | fora | Infraestrutura de hardware |
| 2 | Apagamento verificavel em dados, embeddings e adaptadores | fora | Atua no ciclo de treinamento |
| 3 | Red-teaming de divulgacao como porta de liberacao | fora | Exige extracao, inferencia de pertencimento e inversao; fora do recorte |
| 4 | Auditar dados sinteticos contra extratores; resistir a destilacao | fora | Atua no ciclo de treinamento |
| 5 | Exercitar manual de resposta a incidente de divulgacao | fora | Processo organizacional; conformidade juridica esta fora do escopo |

---

## OWASP LLM08:2026 Hidden Context Exposure — 3 controles (p. 48)

| # | Controle (resumo) | Escopo | Metrica ou motivo |
|---|---|---|---|
| 1 | Nao colocar dado sensivel no contexto oculto; assumir que todo contexto e descobrivel | **avaliado** | O prompt de sistema carrega apenas o marcador unico. Verificado pela classificacao de severidade: informacional, conforme a escala da propria entrada |
| 2 | Usar metodos deterministicos e barreiras externas para controle de comportamento, sem depender do contexto oculto | **avaliado — central** | E a tese do trabalho: a camada e o sistema deterministico externo. Verificado pela comparacao entre a condicao A e a condicao B |
| 3 | Aplicar autorizacao e controle de acesso independentemente do modelo | fora | O cenario nao possui separacao de privilegio entre usuarios |

---

## NIST AI 600-1, funcao MEASURE — 21 acoes etiquetadas

| Action ID | Acao (resumo) | Etiquetas | Escopo | Metrica ou motivo |
|---|---|---|---|---|
| MS-2.2-002 | Anonimizar dados; usar filtros de privacidade na saida; remover PII para evitar dano ou uso indevido | Data Privacy; Information Security | **avaliado** | Filtro de privacidade na saida e o ponto de saida da camada. Precisao e revocacao do mascaramento |
| MS-2.6-005 | Verificar que a arquitetura monitora saidas e trata, recupera e repara erros quando anomalias e ameacas de seguranca sao detectadas | Information Security | **avaliado** | Decisao de alerta e registro estruturado da camada. Contagem de eventos registrados por categoria |
| MS-2.6-006 | Verificar que o sistema trata adequadamente consultas que possam dar origem a uso inadequado, malicioso ou ilegal, incluindo manipulacao e ataques | Information Security | **avaliado** | Correspondencia direta com o conjunto Do-Not-Answer. Taxa de bloqueio por tipo de dano |
| MS-2.6-007 | Avaliar regularmente vulnerabilidades a circunvencao de medidas de seguranca | Information Security | parcial | A circunvencao por ofuscacao e avaliada; a circunvencao adaptativa nao (ADR-0008) |
| MS-2.7-001 | Avaliar probabilidade e magnitude de ameacas como contorno, extracao e inferencia | Data Privacy; Information Security | parcial | Extracao de contexto e avaliada; as demais ameacas listadas estao fora do recorte |
| MS-2.7-007 | Realizar red-teaming para avaliar resiliencia contra ataques de IA generativa, entre eles injecao de instrucao | Information Security | parcial | Avaliado por conjuntos publicados, nao por red-teaming adaptativo (ADR-0008) |
| MS-2.2-001 | Avaliar e gerir vieses estatisticos de procedencia de conteudo | Information Security e outras | fora | Vies e procedencia estao fora do recorte |
| MS-2.2-003 | Oferecer a titulares opcao de retirar consentimento | Data Privacy | fora | Nao ha titular real; dados sinteticos |
| MS-2.2-004 | Usar anonimizacao e privacidade diferencial para impedir religacao ao individuo | Data Privacy | fora | Atua sobre dados de treinamento |
| MS-2.3-001 | Considerar desempenho de referencia em benchmarks ao selecionar modelo | Information Security | fora | Comparacao entre modelos esta fora do escopo |
| MS-2.3-003 | Compartilhar resultados de teste pre-implantacao com autoridade de liberacao | — | fora | Processo organizacional |
| MS-2.3-004 | Usar ambiente de teste dedicado, como o NIST Dioptra | varias | fora | Ferramenta adicional; escopo fechado quanto a comparacao de ferramentas |
| MS-2.5-005 | Verificar procedencia dos dados de treinamento e de avaliacao | Information Integrity | fora | Atua sobre o ciclo de treinamento |
| MS-2.5-006 | Revisar periodicamente barreiras de seguranca em circunstancias novas | Information Security | fora | Processo longitudinal, incompativel com execucao unica |
| MS-2.6-001 | Avaliar presenca de violacao de privacidade e conteudo nocivo nos dados de treinamento | Data Privacy e outras | fora | Atua sobre dados de treinamento |
| MS-2.7-006 | Medir a taxa de implementacao de recomendacoes de seguranca | Information Security | fora | Metrica organizacional de processo |
| MS-2.7-009 | Verificar periodicamente que as medidas permanecem eficazes | Information Security | fora | Processo longitudinal |
| MS-4.2-005 | Documentar incorporacao de retorno publico estruturado nas decisoes | Information Security | fora | Processo organizacional |

Tres acoes adicionais do recorte (MS-2.2-001 e correlatas) foram absorvidas nas
linhas acima por tratarem do mesmo objeto.

---

## Sintese

| Origem | Controles extraidos | Avaliados | Parciais | Fora |
|---|---|---|---|---|
| OWASP LLM01 | 11 | 2 | 2 | 7 |
| OWASP LLM02 | 19 | 3 | 1 | 15 |
| OWASP LLM08 | 3 | 2 | 0 | 1 |
| NIST MEASURE | 21 | 3 | 3 | 15 |
| **Total** | **54** | **10** | **6** | **38** |

Dezesseis controles avaliados ou parciais, contra trinta e oito fora do alcance do
protocolo. A proporcao e o argumento quantitativo da afirmacao de cobertura
amostral ja presente na proposta: a maior parte dos controles do referencial e
arquitetural, organizacional ou atua no ciclo de treinamento, e nenhum experimento
local com modelo consumido como servico os alcanca.

Proximo passo: tarefa 1.6, conversao dos dezesseis em criterios numerados com
identificador, enunciado, origem normativa e metodo de verificacao, seguida da
conferencia cruzada da tarefa 1.7.
