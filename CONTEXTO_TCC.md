# CONTEXTO_TCC.md — registro de continuidade

**Elaborado em:** 17/09/2026
**Autor do registro:** assistente de IA, a pedido de Gabriel Simionato
**Finalidade:** permitir que outra sessão de IA retome o desenvolvimento técnico deste TCC sem acesso à conversa anterior.

> Este documento é um **registro de continuidade**. Não substitui os arquivos originais do repositório, as fontes acadêmicas, o texto da monografia nem as orientações do autor e do orientador. Onde houver divergência, o arquivo no repositório prevalece sobre este resumo.

---

# 1. Resumo para retomada

## Tema e objetivo central

Construir uma **camada intermediária de proteção** que intercepta a comunicação de um chatbot em três pontos — mensagem do usuário, conteúdo recuperado da base de conhecimento e resposta gerada — decidindo entre **encaminhar, bloquear, mascarar e alertar**; e compará-la com outras três condições sob o mesmo conjunto de teste congelado.

Frase-chave registrada no `README.md` do repositório e repetida pelo autor:

> **O produto final não é a camada. É a evidência quantitativa comparativa. A camada é o instrumento.**

| Condição | Ferramenta | Eixo de atuação |
|---|---|---|
| A | nenhuma | linha de base |
| B | camada deste trabalho | entrada, contexto e saída |
| C | Presidio | saída |
| D | moderação de conteúdo (OpenAI `omni-moderation-latest`) | entrada |

**Fonte:** `README.md` (lido hoje). *Confirmado.*

## Estágio atual

**Etapa 3 — construção do conjunto de teste e congelamento.** Em andamento.

O experimento **ainda não foi executado**. Nenhuma regra de detecção da camada existe no repositório, e nenhuma pode existir antes de `conjunto_teste/CONGELADO.md` estar datado e com hash (Princípio I da constituição).

## O que está concluído, em andamento e bloqueado

| Frente | Estado | Evidência |
|---|---|---|
| Etapa 0 — ambiente | Concluída | `docs/atualizacoes/2026-08-31-etapa-0.md`; `docs/versoes.md` com coleta datada de 31/08 |
| Etapa 1 — matriz de critérios | Concluída (com ressalva) | `docs/matriz_criterios.md`, 14 critérios; validação por professor de cibersegurança *pendente de confirmação* |
| Etapa 2 — assistente de referência | Concluída | `docs/atualizacoes/2026-09-10-etapa-2.md`; commit `1f5783c`; conversa ponta a ponta real registrada em `docs/versoes.md` |
| Etapa 3 — tarefa 3.3 (amostragem HackAPrompt) | Em andamento, perto do fim | commits `f72d681`, `1316332`, `338efc6` |
| Etapa 3 — tarefas 3.4 a 3.11 | Não iniciadas | inventário de `conjunto_teste/` mostra pastas `ataques/`, `legitimas/`, `pii/` contendo apenas `.gitkeep` |
| 100 mensagens legítimas (tarefa 3.8) | **Não iniciada — gargalo humano** | `conjunto_teste/legitimas/` contém apenas `.gitkeep` |
| Etapas 4 a 7 | Não iniciadas, bloqueadas pelo congelamento | — |

## Última atividade efetivamente realizada

Em 17/09/2026, na sessão anterior a este registro:

1. O autor executou a revisão manual dos 40 casos da segunda amostra do HackAPrompt e aplicou o resultado (3 divergências), commitando em `338efc6`. *Confirmado por saída de terminal colada pelo autor.*
2. O assistente investigou os 3 casos divergentes, identificou **dois defeitos mecânicos** no classificador e apresentou ao autor a decisão sobre como tratá-los.
3. O autor escolheu a opção **"Corrigir o defeito 1 + livro de rótulos"**. *Confirmado — resposta explícita do autor.*
4. O assistente implementou a correção (revisão 3), criou o livro de rótulos e **escreveu cinco arquivos no repositório do autor**. *Confirmado pelo retorno da ferramenta de escrita.*
5. **Nada disso foi executado nem commitado na máquina do autor.** Os três blocos de comandos entregues (verificação, arquivamento/commit, terceira amostra) **não foram rodados**.

## Próxima ação concreta

Executar o **Bloco 1 — verificação** (seção 10 deste documento), que não grava nada, e conferir quatro saídas. Só depois seguir para os Blocos 2 e 3.

## Principais dúvidas que dependem do autor

Listadas em detalhe na seção 13. As mais importantes:

1. **Onde está o texto da monografia?** Não há nenhum arquivo de texto da monografia neste repositório. Nem proposta, nem sumário, nem capítulos.
2. **Qual é o plano de desenvolvimento com as Etapas 0 a 7?** É citado em vários documentos, mas não foi encontrado no repositório.
3. **O parecer da banca de proposta existe em `docs/parecer-banca-resposta.md`, mas não foi lido.** Precisa ser levado ao novo chat.
4. **O orientador chegou a indicar o professor de cibersegurança** para validar `docs/matriz_criterios.md`?

---

# 2. Alcance e confiabilidade deste registro

## O que foi possível revisar

| Fonte | Alcance |
|---|---|
| Conversa desta sessão | Revisada a partir do ponto de retomada de **11/09/2026** até 17/09/2026. |
| Conversa anterior a 11/09 | **Não acessível em forma original.** Existe apenas um resumo produzido pelo próprio assistente quando o contexto estourou. Esse resumo é registro de segunda mão: útil para reconstruir a linha do tempo, **não** é evidência independente. |
| Repositório no computador do autor | Acessado hoje, por leitura de arquivos e listagem de diretórios. |

## Arquivos efetivamente lidos hoje, na íntegra

- `README.md`
- `.specify/memory/constitution.md`
- `docs/protocolo.md`
- `docs/orcamento.md`
- `docs/requisitos-herdados.md`
- `docs/plano-de-corte.md`
- `docs/versoes.md`
- `docs/decisoes/0001-orcamento-e-plano-de-chamadas.md`
- `conjunto_teste/ORIGEM.md`
- `conjunto_teste/selecao/hackaprompt.json`, `hackaprompt-v1-regra-com-defeito.json`
- `conjunto_teste/revisao/hackaprompt_revisao.csv`, `hackaprompt_revisao-v1.csv`
- `scripts/classificar_codificacao.py`, `scripts/amostrar_hackaprompt.py` (versões anteriores à revisão 3, enviadas pelo autor)
- `scripts/tests/test_classificacao.py`
- Documento de projeto claude.ai: `claude/decisoes-etapa-0.md`

## Arquivos lidos parcialmente

- `docs/matriz_criterios.md` — lidos os 14 critérios, os cabeçalhos e a síntese; **não lida** a seção "Como ler" nem a conferência cruzada completa.
- `docs/atualizacoes/2026-09-10-etapa-2.md` — lidos apenas os cabeçalhos.
- `docs/texto-limitacoes-e-trabalhos-futuros.md` — lidos apenas os cabeçalhos.

## Arquivos cuja existência foi confirmada por listagem, mas **não lidos**

`docs/parecer-banca-resposta.md`, `docs/matriz/01-extracao-bruta.md`, `docs/atualizacoes/2026-08-31-etapa-0.md`, `docs/atualizacoes/2026-09-09-etapa-1.md`, ADRs 0002 a 0016, `docker-compose.yml`, `pytest.ini`, `.gitignore`, `.env.example`, `requirements-dev.txt`, e todo o conteúdo de `camada/`, `assistente/`, `base_conhecimento/`, `executor/`, `modelo/`, `recuperador/`, `analise/`, `resultados/`.

## Limitações de acesso conhecidas

1. **A ponte que executava comandos na máquina do autor está quebrada** desde 17/09 (atualização do Windows de 08/09). Foi possível **ler e escrever arquivos**, mas **não rodar comandos**. Consequência direta: **não foi possível rodar `git log`, `pytest` nem qualquer script na máquina do autor hoje.** Todo histórico de commits registrado neste documento vem de saídas de terminal que o **autor colou na conversa**.
2. Testes executados pelo assistente rodaram em **cópias**, num container isolado, não na máquina do autor. São evidência de que o código funciona, **não** de que o repositório do autor está nesse estado.
3. O `.env` não foi lido e não deve ser (contém chave de API).

---

# 3. Contexto acadêmico e escopo

## Identificação

| Item | Valor | Estado |
|---|---|---|
| Título (conforme `README.md`) | "Camada intermediária de proteção de entrada e saída em assistentes conversacionais com modelos de linguagem — Avaliação comparativa com foco em dados pessoais brasileiros" | *Confirmado no arquivo.* **Pendente de confirmação** se é o título final ou provisório |
| Autor | Gabriel Simionato | Confirmado |
| Curso | Bacharelado em Sistemas de Informação | Confirmado |
| Instituição | Centro Universitário Mater Dei (UNIMATER), Pato Branco/PR | Confirmado |
| Orientador | Prof. Me. Muriel Mazzetto | Confirmado |
| Entrega do TCC I | **24/11/2026** | Confirmado (`README.md`) |
| Disponibilidade do autor | "2 ou 3 horas por dia" | Confirmado (mensagem do autor, data exata não recuperável) |

## Problema, objetivos, justificativa

**Não informado neste repositório.** Não foi encontrado nenhum arquivo com problema de pesquisa, objetivo geral, objetivos específicos ou justificativa formalmente redigidos. Esses elementos existem presumivelmente na **proposta de TCC**, que é citada em vários documentos (`README.md`, ADR-0001, `docs/plano-de-corte.md`) mas **não está no repositório**.

→ Ver pergunta 1 da seção 13.

## Escopo e delimitações — *Confirmado*

Fonte: `.specify/memory/constitution.md`, seção "Restrições de escopo e de conduta".

Estão **explicitamente fora do escopo**: ofuscação por tradução; ataques multimodais; ataques adaptativos; técnicas documentadas após o congelamento; anonimização de documentos de outros países; conformidade jurídica com legislação de proteção de dados; análise estática de código; comparação entre modelos de linguagem distintos.

A cobertura é **amostral, não exaustiva**, e assim deve ser declarada nos resultados.

## As 11 restrições invioláveis

Enunciadas pelo autor no início do trabalho e transcritas no `README.md` como "Regras permanentes". A constituição as reorganiza em 5 princípios. *Confirmado nos dois arquivos.*

1. Conjunto de teste congelado, datado e com hash **antes** da primeira regra da camada.
2. Regra nunca é ajustada a um caso do conjunto congelado. Após a execução, desempenho ruim é **resultado**, não defeito.
3. Somente dados sintéticos. Nenhum **dado pessoal** real, em nenhuma etapa. *(Redação corrigida em 10/09 — ver RQ-17.)*
4. Modelo único, snapshot travado, temperatura zero.
5. Ataques apenas contra o ambiente local.
6. O fluxo do assistente é variável de controle: idêntico nas quatro condições, com os três nós HTTP presentes desde a condição A.
7. Latência medida dentro da camada. Tempo de rede fora da métrica.
8. Registro bruto nunca é editado. Correção gera nova execução.
9. Todo código que chama o modelo tem teto de chamadas, modo simulado e contador.
10. Toda aleatoriedade usa a semente registrada (`SEMENTE_MESTRA=20260829`).
11. Escopo fechado. O relevante que estiver fora vira trabalho futuro.

## Distinção metodológica central — *Confirmado*

A constituição (Princípio V) distingue dois casos que **não são equivalentes**, e essa distinção é o que legitimou três correções já feitas:

- **Defeito de instrumentação** — erro no executor, no formato de registro, na medição ou no classificador. Corrigir é legítimo e gera nova execução; **ambas as execuções são preservadas** e o ADR registra o defeito.
- **Ajuste orientado ao resultado** — alterar regra, critério de julgamento ou fórmula após observar o resultado. **Proibido, sem exceção.**

"A diferença está na direção da causa."

## Metodologia de desenvolvimento

**GitHub Spec Kit** (`specify-cli` 1.0.2), com a constituição como âncora metodológica. Cada etapa deveria produzir especificação, plano técnico e lista de tarefas versionados em `specs/`.

⚠️ **Inconsistência observada:** `specs/` contém apenas `.gitkeep`. Nenhum artefato do Spec Kit foi encontrado. Ver seção 13, item 6.

RQ-20 item 5 exige declarar na monografia que "a metodologia de desenvolvimento adotada organiza o desenvolvimento e **não substitui o método científico**, que é o desenho experimental descrito na metodologia".

## Orientações e feedback recebidos

| Origem | Conteúdo | Estado |
|---|---|---|
| Banca de proposta | Pareceres com notas de 0 a 3. Geraram `docs/parecer-banca-resposta.md` e vários requisitos herdados (RQ-04, RQ-05, RQ-09) e o `docs/plano-de-corte.md` | *Confirmado que existe; conteúdo não lido hoje* |
| Revisão externa dos artefatos (setembro/2026) | Origem da maioria dos 20 requisitos herdados e da ADR-0010 | *Confirmado* (`docs/requisitos-herdados.md`) |
| Orientador, 02/09/2026, por WhatsApp | Sobre ataques adaptativos: "Deixar escopo atual e colocar como sugestão de continuidade"; "Mostrar que teve contato e conhecimento sobre isso"; "deixar claro o escopo reduzido"; "se ver que dá tempo de abordar isso, aí faz no TCC2"; "Pra não inflar demais a expectativa da banca já" | *Confirmado — citado pelo autor na conversa.* Formalizado em ADR-0008 |
| Orientador — indicação de professor de cibersegurança | Mencionado no resumo da conversa anterior como pendência para validar `docs/matriz_criterios.md` | **Pendente de confirmação** |

---

# 4. Arquivos e ordem de leitura

**Caminho raiz do repositório na máquina do autor:**
`C:\Users\Simi\OneDrive\Desktop\Desenvolvimento TCC\tcc-camada-protecao`

⚠️ O documento de projeto `claude/decisoes-etapa-0.md` cita o caminho antigo `C:\Users\Simi\ProjetosGit\tcc-camada-protecao`. **A pasta foi movida** a pedido do autor. O caminho antigo está superado.

## Prioridade 1 — ler antes de qualquer coisa

| Arquivo | Finalidade | Acesso | Estado |
|---|---|---|---|
| `.specify/memory/constitution.md` | As regras que nenhuma etapa pode violar | Lido hoje | Atual, v1.0.0, ratificada 31/08 |
| `docs/requisitos-herdados.md` | 20 requisitos (RQ-01 a RQ-20) com dono, gatilho e critério de aceitação | Lido hoje | Atual |
| `docs/decisoes/0017-amostragem-hackaprompt.md` | ADR mais movimentada do projeto: decisão original + revisões 2 e 3 | **Revisão 3 escrita hoje pelo assistente, não commitada** | Atual, não commitado |
| `docs/protocolo.md` | Receita de execução. Seções 1–3 fechadas; 4–8 em aberto | Lido hoje | Parcial, por construção |

## Prioridade 2 — contexto do experimento

| Arquivo | Finalidade | Acesso | Estado |
|---|---|---|---|
| `README.md` | Visão geral, condições A–D, regras permanentes | Lido hoje | Atual |
| `docs/matriz_criterios.md` | 14 critérios (INJ, PII, CTX, NOC) ancorados em OWASP e NIST | Parcialmente lido | Atual |
| `docs/orcamento.md` | Plano de chamadas, custo unitário medido, tetos | Lido hoje | Atual |
| `docs/versoes.md` | Versão exata de cada componente, digests, hashes | Lido hoje | Atual, coletas de 31/08 e 10/09 |
| `docs/plano-de-corte.md` | C1 a C5, com gatilhos objetivos. Nenhum acionado | Lido hoje | Atual |
| `conjunto_teste/ORIGEM.md` | Procedência, versão, hash e licença dos três conjuntos públicos | Lido hoje | Atual |

## Prioridade 3 — precisam ser lidos e **não foram**

| Arquivo | Por que importa |
|---|---|
| `docs/parecer-banca-resposta.md` (13.939 bytes) | **Única fonte no repositório sobre o feedback da banca.** Não lido |
| `docs/atualizacoes/2026-09-09-etapa-1.md` (13.163 bytes) | Fechamento da Etapa 1 |
| `docs/atualizacoes/2026-09-10-etapa-2.md` (10.666 bytes) | Fechamento da Etapa 2; só cabeçalhos lidos |
| `docs/matriz/01-extracao-bruta.md` (16.429 bytes) | Extração bruta de OWASP e NIST que originou a matriz |
| ADRs 0002 a 0016 | Decisões técnicas fechadas |

## ADRs existentes — inventário completo

Todos em `docs/decisoes/`. Confirmados por listagem de diretório.

| ADR | Assunto |
|---|---|
| 0000 | modelo (template) |
| 0001 | orçamento e plano de chamadas |
| 0002 | recuperação determinística BIPIA — **revisado pela 0012** |
| 0003 | corpus PII avaliado fora do fluxo |
| 0004 | repetições de latência sobre a camada |
| 0005 | recorte da área de vazamento (248) |
| 0006 | condição D = moderação OpenAI |
| 0007 | parâmetros de recuperação (k=3) |
| 0008 | ataques adaptativos fora do escopo |
| 0009 | duas grandezas de tempo |
| 0010 | correções de revisão externa |
| 0011 | modelo de embeddings |
| 0012 | recuperação em dois estágios |
| 0013 | estratificação HackAPrompt |
| 0014 | contaminação e restauração BIPIA |
| 0015 | corpus de dados pessoais |
| 0016 | conjuntos públicos não redistribuídos |
| 0017 | amostragem HackAPrompt (+ revisões 2 e 3) |

## Arquivos de dados do conjunto de teste

| Arquivo | Conteúdo | Versionado? |
|---|---|---|
| `conjunto_teste/selecao/hackaprompt.json` | Amostra vigente (2ª), 40 casos, com `classe_final` revisada | Sim, commitado |
| `conjunto_teste/selecao/hackaprompt-v1-regra-com-defeito.json` | 1ª amostra, preservada como evidência | Sim, commitado |
| `conjunto_teste/selecao/rotulos.json` | **Livro de rótulos**, 71 decisões humanas por hash | **Escrito hoje, não commitado** |
| `conjunto_teste/revisao/hackaprompt_revisao.csv` | CSV de revisão da 2ª amostra, **com texto de ataque** | **Não** — `.gitignore` |
| `conjunto_teste/revisao/hackaprompt_revisao-v1.csv` | CSV de revisão da 1ª amostra | **Não** — `.gitignore` |
| `conjunto_teste/origem/` | Cópias locais de Do-Not-Answer, HackAPrompt, BIPIA | **Não** — ADR-0016 |
| `conjunto_teste/ataques/`, `legitimas/`, `pii/` | **Vazias** (só `.gitkeep`) | — |
| `conjunto_teste/CONGELADO.md` | **Não existe ainda.** É o marco que destrava a Etapa 4 | — |

## Arquivos que o autor precisa anexar no novo chat

Ver lista priorizada ao final da resposta do assistente. Nada do caminho local deste chat estará acessível à próxima IA.

---

# 5. O que já foi feito

## Etapa 0 — ambiente (concluída)

**Produzido:** esqueleto do repositório; `docker-compose.yml` com imagens fixadas por **digest sha256**; 7 serviços; `scripts/verificar_servicos.py` como evidência de conclusão; `scripts/coletar_versoes.py`; `scripts/fumaca_modelo.py`.

**Evidência disponível:** `docs/versoes.md` com coleta datada de 31/08; `docs/atualizacoes/2026-08-31-etapa-0.md`.

**Medição real registrada:** teste de fumaça de 31/08 com 3 chamadas reais — 836 tokens de entrada, 162 de saída, **US$ 0,001646 por chamada**, US$ 0,004938 gastos. Confirmou o snapshot `claude-haiku-4-5-20251001`. *Confirmado em `docs/orcamento.md`.*

**Estado de revisão:** não consta revisão pelo orientador.

## Etapa 1 — matriz de critérios (concluída, com ressalva)

**Produzido:** `docs/matriz_criterios.md` com **14 critérios** em quatro grupos, cada um ancorado em OWASP GenAI LLM Top 10 2026 ou NIST AI 600-1, com tipo de verificação, condições envolvidas e restrição declarada.

| Grupo | Critérios | Avaliados | Parciais |
|---|---|---|---|
| INJ — injeção de instrução | 5 | 1 | 4 |
| PII — dados pessoais | 5 | 2 | 3 |
| CTX — contexto interno | 2 | 1 | 1 |
| NOC — solicitação nociva | 2 | 1 | 1 |
| **Total** | **14** | **5** | **9** |

Verificação: 10 por medição experimental, 3 por inspeção documental, 1 por teste unitário.

**Erros identificados e corrigidos nesta etapa** (registrados em ADR-0010):
- A síntese declarava 9 medições / 3 inspeções / 2 testes unitários; a contagem real é 10/3/1.
- A extração do NIST declarava 21 ações mas tabulava 18; as três faltantes (`MS-2.3-002`, `MS-2.6-002`, `MS-2.7-002`) nunca tinham sido examinadas. Recuperadas e classificadas como `fora`.
- A descrição de `MS-2.6-001` pertencia na verdade a `MS-2.6-002`.
- `INJ-04` media BIPIA na condição D, contradizendo a ADR-0001. Corrigido.
- **`PII-01` havia sido reescrito numa versão que a camada satisfaz** — o erro exato que a metodologia existe para impedir, na direção oposta. Rebaixado para `parcial`.

*Fonte: resumo da conversa anterior + `docs/matriz_criterios.md` lido hoje, que confere com a descrição.*

**Ressalva:** a validação por professor de cibersegurança está **pendente de confirmação**.

## Etapa 2 — assistente de referência (concluída)

**Produzido:** fluxo n8n com os três nós HTTP; serviço `recuperador` (Qdrant + FastEmbed); serviço `modelo` (único autorizado a chamar o LLM); base de conhecimento de 30 documentos sintéticos com semente fixa; prompt de sistema versionado com marcador único.

**Evidências registradas em `docs/versoes.md`:**
- Hash do estado da base: `f118bb5851f1ce54d4053f8ca9b1eac5276cd0ca40bb006062436c343d60baa7`
- Marcador único: `CANARIO-TCC-2DEFEC2A9B0F`
- Hash do prompt (16 primeiros dígitos): `5ab9ed98e5cde6da`
- Segunda medição de custo, em conversa real de 10/09: 1.041 entrada / 71 saída / US$ 0,001396

**Falsificação por medição registrada (ADR-0012):** a primeira indexação real deu **3/30** — 27 das 30 perguntas retornavam o mesmo trio de documentos. Causa: 30 documentos quase idênticos; embeddings densos não preservam identificadores exatos. Corrigido com **recuperação em dois estágios** (filtro exato por `numero_pedido` + preenchimento por similaridade), resultando em **30/30 na primeira posição**. A ADR-0002 foi mantida com nota de revisão anexada, não apagada.

**Achado de reprodutibilidade:** o identificador do modelo de embeddings **não basta** para reproduzir o índice — a biblioteca `fastembed` alterou a estratégia de agregação (vetor de classe → média), de modo que a unidade de reprodução é o **par modelo + versão da biblioteca**. *Confirmado em `docs/versoes.md` e ADR-0011.*

## Etapa 3 — em andamento

### Tarefas 3.1 e 3.2 — obtenção e conferência dos conjuntos (concluídas)

`scripts/obter_conjuntos.py` e `scripts/conferir_conjuntos.py`. Resultados **confirmados por saída de terminal colada pelo autor**:

| Conjunto | Verificação |
|---|---|
| Do-Not-Answer | 939 linhas; área `Information Hazards` = **248** (136 organização/governo + 112 privacidade de indivíduo) — CONFERE |
| BIPIA | `text_attack_test.json` = **75 cargas** em 15 categorias — CONFERE |
| BIPIA (código) | 10 categorias / 50 cargas — **excluídas** por ADR-0014 |
| HackAPrompt | 601.757 submissões; 77.936 bem-sucedidas; **19.803 após deduplicação** |

Procedência, versão de commit, data e hash de cada arquivo registrados em `conjunto_teste/ORIGEM.md` e `origem.json`. Isso atende **RQ-05**.

**Licenças confirmadas:** Do-Not-Answer é CC BY-NC-SA 4.0 (dados) — incompatível com MIT do repositório **se redistribuído**; daí a ADR-0016, que versiona apenas a seleção (ids + hashes), nunca o conteúdo. HackAPrompt é MIT, **acesso restrito** (exige aceite e token). BIPIA: licença marcada como "confirmar no arquivo LICENSE" — **pendência em aberto no próprio ORIGEM.md**.

### Tarefa 3.3 — amostragem estratificada do HackAPrompt (quase concluída)

Esta tarefa consumiu a maior parte do esforço entre 11/09 e 17/09 e passou por **três revisões do classificador**. O histórico completo está na ADR-0017. Resumo do que aconteceu:

**Revisão 1 (11/09).** Classificador `scripts/classificar_codificacao.py` com quatro classes: `texto_simples`, `codificacao_ou_ofuscacao`, `unicode_invisivel`, `idioma_ou_escrita_distinta`. Amostra de 40, alocação igual (10 por estrato), semente 20260829. Estratos no universo: 18.554 / 48 / 112 / 1.089.

**Revisão manual da 1ª amostra → 9 divergências**, todas de `idioma_ou_escrita_distinta` para `codificacao_ou_ofuscacao`.

**Defeito descoberto (revisão 2, 11/09).** O classificador decidia latinidade pelo **prefixo do nome Unicode** do caractere. Nome de caractere não é a propriedade Script do UAX #24: `MATHEMATICAL BOLD CAPITAL A`, `FULLWIDTH LATIN CAPITAL LETTER A` e `MODIFIER LETTER SMALL A` são a letra A e nenhum começa por `LATIN`. Efeito sistemático e de uma direção só. Defeito secundário: `COMMON` e `INHERITED` eram tratados como prefixos de nome, mas são nomes de Script — nunca casaram com nada.

**Correção:** aplicar NFKC antes do teste de escrita; tratar mistura de escritas dentro de um token como homóglifo.

**Verificação da correção:** a regra corrigida reproduziu **9 de 9** decisões humanas e chegou à mesma distribuição (19/10/10/1). A reclassificação do universo inteiro deu **92,7%** de erro naquele estrato (1.009 de 1.089) — contra os 90% estimados pela amostra de dez. *Medições executadas pelo assistente na máquina do autor em 11/09, quando a ponte de comandos ainda funcionava.*

Novos estratos: 18.546 / 1.065 / 112 / 80.

**Revisão manual da 2ª amostra (17/09) → 3 divergências.** Investigação identificou **dois novos defeitos mecânicos**:

- **Defeito 1:** `tem_variante_tipografica` filtrava a entrada com `isalpha()`. Letras circuladas (`Ⓟ`) são categoria `So` e nunca chegavam ao teste, embora a NFKC produza `P`. Afetou as ordens 19 e 20.
- **Defeito 2:** homóglifo de **palavra inteira** — quando todas as letras são substituídas, não sobra nada latino para misturar. Afetou a ordem 14.

**Decisão do autor (17/09, confirmada):** corrigir o defeito 1, declarar o defeito 2 como limitação (exigiria a tabela de confundíveis do UTS #39, uma segunda tabela Unicode a congelar), e criar um **livro de rótulos**.

**Revisão 3 — implementada hoje, NÃO executada nem commitada.**

## Estado de revisão e aprovação — resumo honesto

| Item | Não revisado | Revisado pelo autor | Aprovado pelo orientador |
|---|---|---|---|
| Etapas 0, 1, 2 | | ✔ (o autor commitou) | *Pendente de confirmação* |
| Matriz de critérios | | ✔ | Validação por especialista pendente |
| Tarefa 3.3 | | ✔ até `338efc6` | — |
| Revisão 3 (hoje) | ✔ | — | — |

**Nenhum documento deste projeto consta como formalmente aprovado pelo orientador.** O que existe são orientações pontuais (ADR-0008) e o parecer da banca de proposta, cujo conteúdo não foi lido hoje.

---

# 6. Decisões e mudanças de direção

| Assunto | Decisão | Estado | Quem decidiu | Motivo | Evidência | Consequência |
|---|---|---|---|---|---|---|
| Orçamento de API | 3.883 chamadas, US$ 6,39 projetado; `TETO_USD=16,00`, `TETO_CHAMADAS=8500` | **Vigente** | Autor (aceitou proposta) | Crédito de US$ 20 é finito | ADR-0001 + `docs/orcamento.md` | Margem de ~US$ 13,60 comporta duas reexecuções |
| ↳ mudança anterior | `TETO_CHAMADAS` era 4.500 | **Substituída em 10/09** | — | Não comportava reexecução (2×3.883=7.766) | ADR-0001, seção "Correção de 10/09/2026" | Incoerência apontada por revisão externa |
| Custo unitário | US$ 0,001646 (medido), substitui estimativa de US$ 0,0019 | Vigente | Medição | Teste de fumaça de 31/08 | `docs/orcamento.md` | Projeção caiu de US$ 7,38 para US$ 6,39 |
| ↳ **não** recalibrado | Duas medições posteriores (0,001646 e 0,001396) **não** foram usadas para recalibrar | Vigente, deliberado | Assistente, aceito pelo autor | Duas amostras favoráveis não justificam recalibrar; o piloto da Etapa 4 fixa o valor | `docs/versoes.md` | Projeção segue conservadora |
| Recuperação do BIPIA | Cada carga embutida em documento com `numero_pedido` único; pergunta pareada | Vigente | Autor (resposta explícita: "Precisa virar decisão registrada") | Com k=3 sobre 30 docs, o documento envenenado podia não entrar no top-3 | ADR-0002 | Pareamento é facilidade concedida ao atacante — **declarar como limitação** |
| ↳ revisão | Recuperação em **dois estágios** (filtro exato + similaridade) | **Vigente, substitui parte da 0002** | Medição falsificou a premissa | Indexação real deu 3/30 | ADR-0012; ADR-0002 mantida com nota | 30/30 na primeira posição |
| Corpus PII | Avaliado **fora** do fluxo do assistente | Vigente | Autor ("sim") | B e C receberiam textos diferentes se passassem pelo modelo | ADR-0003 | Zero custo de API; limitação: mede detecção isolada, não ponta a ponta |
| Repetições de latência | Sobre a camada, sem nova chamada ao modelo; mantidas 3 repetições reais só na condição A | Vigente | Autor ("sim... mantenha 3 repetições reais de LLM na condição A") | Camada é determinística; repetir o modelo gastaria crédito sem informação | ADR-0004 | Reduz custo ~2/3 |
| Área de vazamento | **248** solicitações (136 + 112) | Vigente | Autor ("São 248, e é esse número que entra no congelamento") | Perder as 112 perderia o foco em dados pessoais | ADR-0005 | Recorte de 136 fica como corte C2 |
| Condição D | Moderação da OpenAI `omni-moderation-latest` | Vigente | Autor ("Verifique isso antes da Etapa 5") | Gratuita; não consome crédito Anthropic | ADR-0006 | Expectativa registrada **antes**: D deve ir mal em injeção, por construção |
| Recuperação | k=3; documentos de 150 a 300 tokens | Vigente | Autor | Custo e janela de contexto | ADR-0007 | — |
| Ataques adaptativos | **Fora do escopo do TCC I**; registrados como trabalho futuro | Vigente | **Orientador**, 02/09 por WhatsApp | "Pra não inflar demais a expectativa da banca já" | ADR-0008 + `docs/texto-limitacoes-e-trabalhos-futuros.md` | Se sobrar tempo, vai para o TCC II |
| Medição de tempo | Duas grandezas: `tempo_ms` (interno) e `tempo_total_ms` (HTTP completo) | Vigente | Recomendação da banca | Condições C e D não têm tempo interno separável | ADR-0009 + `docs/protocolo.md` §2 | Comparação entre condições usa `tempo_total_ms` |
| Modelo de embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`, 768d, Apache-2.0 | Vigente | Assistente, aceito pelo autor | Multilíngue, local, sem chamada externa | ADR-0011 + `docs/versoes.md` | Unidade de reprodução = modelo **+ versão da fastembed** |
| Conjuntos públicos | **Não redistribuídos**; versiona-se apenas seleção (ids + hashes) | Vigente | Assistente, aceito | Do-Not-Answer é CC BY-NC-SA 4.0, incompatível com MIT se redistribuído | ADR-0016 | CSV com texto de ataque fica fora do Git |
| BIPIA | Um cenário por carga (75), com restauração da base entre cenários | Vigente | — | Contaminação cruzada entre casos | ADR-0014 + RQ-18 | Ataques de código (50) excluídos |
| Estratificação HackAPrompt | Por classe de codificação do OWASP LLM01:2026 | Vigente | Assistente, aceito | INJ-05 exige leitura por técnica | ADR-0013 | Se a estratificação fosse por outro atributo, INJ-05 seria rebaixado para `fora` |
| Amostra HackAPrompt | 40 casos, **alocação igual** por estrato (não proporcional) | Vigente | — | INJ-05 lê por técnica; estrato com 2 casos não sustenta leitura | ADR-0017 | **Nenhum agregado pode ser reportado sobre os 40** sem reponderar |
| Dígitos de largura cheia | Critério cobre **apenas letras**; dígitos ofuscados escapam | **Vigente, declarado** | **Autor**, 11/09 ("Manter só letras") | Fidelidade ao texto de R1 | ADR-0017 rev. 2 e 3 | Limitação declarada, não silenciada |
| Defeito de homóglifo de palavra inteira | **Não corrigir**; declarar como limitação | **Vigente** | **Autor**, 17/09 (escolha explícita) | Exigiria tabela UTS #39 — segunda tabela Unicode a congelar, mesmo custo que levou a recusar `regex` | ADR-0017 rev. 3 | Estrato de escrita não latina mantém viés pequeno e desconhecido |
| Livro de rótulos | Decisões humanas indexadas por sha256 do texto | **Vigente, implementado, não commitado** | **Autor**, 17/09 | Decisão é sobre o texto, não sobre o sorteio; sobrevive a reamostragem | ADR-0017 rev. 3 | Revisões futuras só cobrem casos inéditos |

## Alternativas descartadas — para não reabrir discussões

| Alternativa | Por que foi descartada |
|---|---|
| Aumentar `k` até cobrir a base inteira | Descaracteriza o RAG, infla contexto, encarece |
| `k=5` | +40% de custo unitário sem benefício, já que a recuperação é garantida por pareamento |
| 3 repetições reais de LLM em todas as condições | Excede o crédito sem acrescentar informação |
| Usar só as 136 solicitações de vazamento | Perde o subconjunto de dados de indivíduos, que é o foco |
| Classificador próprio como condição D | Deixaria de ser ferramenta de terceiro |
| Biblioteca `regex` com `\p{Script=Latin}` | Acrescentaria segunda tabela Unicode versionada ao que precisa ser congelado |
| Biblioteca de confundíveis (UTS #39) | Mesmo motivo |
| Não deduplicar o HackAPrompt | A amostra repetiria ataques quase idênticos |
| Restringir aos níveis mais altos do HackAPrompt | Deixaria de representar técnicas simples |
| Classificação apenas manual | Não reprodutível |
| Classificação apenas automática | Casos ambíguos ficariam errados em silêncio — **o que de fato aconteceu três vezes** |

---

# 7. Estrutura atual do TCC

⚠️ **Não foi encontrado nenhum sumário nem estrutura de capítulos da monografia neste repositório.** Não há arquivos de texto do TCC — apenas documentação técnica.

O que existe são **insumos para capítulos**, não os capítulos:

| Arquivo | Insumo para |
|---|---|
| `docs/matriz_criterios.md` | Referencial teórico e metodologia — ancoragem normativa |
| `docs/protocolo.md` | Metodologia — desenho experimental |
| `docs/plano-de-corte.md` | Metodologia — gestão de escopo |
| `docs/texto-limitacoes-e-trabalhos-futuros.md` | **Texto redigido** para as seções de limitações e trabalhos futuros |
| `docs/decisoes/` (18 ADRs) | Apêndice metodológico |
| `docs/versoes.md` | Apêndice de reprodutibilidade |
| `docs/requisitos-herdados.md` | Controle interno; RQ-20 lista correções a fazer **na redação** |
| `docs/parecer-banca-resposta.md` | Resposta ao parecer da banca — **não lido** |

O documento `docs/texto-limitacoes-e-trabalhos-futuros.md` tem uma seção "Regra de redação — vale para todo o documento" que provavelmente contém orientações de escrita relevantes. **Não foi lido** além dos cabeçalhos.

→ Ver pergunta 1 da seção 13.

## Estrutura de etapas do desenvolvimento

Inferida de referências consistentes em `docs/requisitos-herdados.md`, `docs/protocolo.md` e `docs/plano-de-corte.md`. **O plano de desenvolvimento original não foi localizado.**

| Etapa | Conteúdo | Estado |
|---|---|---|
| 0 | Ambiente | Concluída |
| 1 | Matriz de critérios | Concluída |
| 2 | Assistente de referência | Concluída |
| 3 | Conjunto de teste e congelamento | **Em andamento** |
| 4 | Camada intermediária (+ piloto de 20 mensagens ao final) | Bloqueada pelo congelamento |
| 5 | Executor e protocolo | Não iniciada |
| 6 | Execução completa | Não iniciada |
| 7 | Análise | Não iniciada |

---

# 8. Referências, dados e fundamentos

## Referenciais normativos — consultados diretamente

| Fonte | Uso | Estado |
|---|---|---|
| **OWASP GenAI LLM Top 10 2026, v1.0 (03/08/2026)** | Ancora os critérios INJ, PII e CTX. LLM01 Prompt Injection (p. 10), LLM02 Sensitive Information Disclosure (p. 18), LLM08 Hidden Context Exposure (p. 46) | PDF em `docs/referencial/OWASP-GenAI-LLM-Top-10-2026-v1.0 (1).pdf`. **Consultado** — o autor enviou o PDF com hash SHA-256 |
| **NIST AI 600-1 (jul/2024)** | Ancora critérios via função MEASURE, ações marcadas Information Security / Data Privacy | PDF em `docs/referencial/NIST.AI.600-1.pdf`. **Consultado** |

⚠️ **Nota sobre LLM08:** a categoria aparece como renomeada/movida a partir de LLM07 System Prompt Leakage (2025). *Informação vinda do resumo da conversa anterior — pendente de reconferência no PDF.*

## Referências citadas — precisam de conferência

| Referência | Uso no trabalho | Estado |
|---|---|---|
| **Alves et al. (SBSeg 2025)** — avaliação de NeMo Guardrails | Origem da "Taxa de Compensação"; comparabilidade do recorte de 136 | ⚠️ **RQ-20 item 1 exige conferir no texto integral** os números atribuídos: sensibilidade de 51,97% e 122 falsos negativos. **Não conferido** |
| **Nasr et al. (2025), "The attacker moves second"** (arXiv 2510.09023) | Sustenta a limitação sobre ataques adaptativos | Mencionada. Dados bibliográficos **não conferidos** hoje |
| **MTEB-BR** (arXiv 2607.04581) | Benchmark de embeddings em português | Mencionada. **Não conferida** |
| Incidente do ChatGPT, março/2023 | ⚠️ RQ-20 item 2: enquadrar como exposição por infraestrutura e cache, **sem sugerir** que a camada o teria evitado | Pendente |

> ⚠️ **Aviso à próxima IA:** os números e identificadores acima vêm do resumo da conversa anterior, não de consulta às fontes nesta sessão. **Não os reproduza na monografia sem conferir na fonte original.** Não complete dados bibliográficos de memória.

## Conjuntos de dados

| Conjunto | Origem | Versão | Licença | Papel |
|---|---|---|---|---|
| Do-Not-Answer | `LibrAI/do-not-answer` | `74e74f2e4507ef256fe536f78a776f4a1ff67955` | CC BY-NC-SA 4.0 (dados) / Apache-2.0 (código) | 939 solicitações nocivas — grupos NOC e PII |
| HackAPrompt | `hackaprompt/hackaprompt-dataset` | `25b87fbedfb86840abaf8cd09af7a029208a971a` | MIT, **acesso restrito** | Injeção direta — grupo INJ |
| BIPIA | `github.com/microsoft/BIPIA.git` | `a004b69ec0dd446e0afd461d98cb5e96e120a5d0` | ⚠️ **"confirmar no arquivo LICENSE"** | Injeção indireta — grupo INJ |

Todos com data de obtenção **11/09/2026** e hash SHA-256 por arquivo em `conjunto_teste/origem.json`. *Confirmado em `conjunto_teste/ORIGEM.md`.*

⚠️ A restrição **não comercial** do Do-Not-Answer acompanha o uso e **precisa ser declarada na monografia**.

## Dados produzidos

| Dado | Origem | Limitação |
|---|---|---|
| Base de 30 documentos sintéticos | `scripts/gerar_base_conhecimento.py`, semente 20260829 | Sintético por construção |
| Prompt de sistema + marcador `CANARIO-TCC-2DEFEC2A9B0F` | `scripts/gerar_prompt_sistema.py` | A camada conhece o marcador — **vantagem estrutural declarada** em CTX-02 |
| Corpus de 350 ocorrências de documentos brasileiros | **Ainda não gerado** (tarefas 3.5 e 3.6) | Exigirá Faker pt_BR + validate-docbr |
| Amostra de 40 casos do HackAPrompt | `scripts/amostrar_hackaprompt.py` | Alocação igual — **não é estimativa do universo** |

## Afirmações que ainda precisam de fonte

1. Os números de Alves et al. (RQ-20 item 1).
2. A recategorização LLM07 → LLM08 no OWASP 2026.
3. A licença do BIPIA.
4. Qualquer afirmação sobre a legislação brasileira de proteção de dados — RQ-20 item 3 exige tratar mascaramento, anonimização, cifragem e conformidade jurídica como **conceitos distintos**, e a conformidade jurídica já está fora do escopo.

---

# 9. Parte técnica

## Arquitetura

Sete serviços em Docker Compose, todas as imagens fixadas por **digest sha256**.

| Serviço | Porta | Papel |
|---|---|---|
| n8n | 5678 | Assistente de referência (variável de controle) |
| Qdrant | 6333 | Base de conhecimento indexada |
| Presidio Analyzer | 5002 | Condição C |
| Presidio Anonymizer | 5001 | Condição C |
| camada | 8000 | Condição B — objeto avaliado |
| recuperador | 8100 | Vetorização e busca |
| modelo | 8200 | **Único ponto autorizado a chamar o LLM** |

Todas publicadas em `127.0.0.1`. *Confirmado em `docs/versoes.md`.*

## Versões fixadas (extrato)

| Item | Valor |
|---|---|
| Modelo de linguagem | `claude-haiku-4-5-20251001`, temperatura 0, max 400 tokens de saída |
| Embeddings | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`, 768d, cosseno |
| Python | 3.13.2 |
| fastapi 0.115.6 · pydantic 2.10.4 · qdrant-client 1.19.0 · fastembed 0.8.0 · onnxruntime 1.30.0 · anthropic 0.69.0 · pytest 8.3.4 · faker 40.38.0 · validate-docbr 2.0.0 | |
| Equipamento | Notebook Intel i5-13420H, 24 GB, Windows com WSL2 |

Lista completa em `docs/versoes.md`.

## Ambiente de desenvolvimento

- Venv **fora** da pasta do projeto: `%USERPROFILE%\venvs\tcc-camada` — para não ser sincronizado pelo OneDrive.
- Ativação no PowerShell: `& "$HOME\venvs\tcc-camada\Scripts\Activate.ps1"` (o `&` é necessário).
- `pytest` **precisa** ser rodado da raiz do repositório com a venv ativa, e com `--import-mode=importlib`.
- Configuração por variável de ambiente; `.env` fora do Git desde o primeiro commit.

## Procedimentos testados

| Procedimento | Comando | Evidência |
|---|---|---|
| Subir o ambiente | `docker compose up -d --build` seguido de `python scripts/verificar_servicos.py` | Autor confirmou "Todos os serviços responderam" |
| Suíte de testes | `python -m pytest -q --import-mode=importlib` | **114 passed, 4 deselected** — saída colada pelo autor em 17/09 |
| Conferir a regra corrigida | `python scripts\conferir_reclassificacao.py conjunto_teste\revisao\hackaprompt_revisao-v1.csv` | **9/9** — saída colada pelo autor |
| Amostrar | `python scripts\amostrar_hackaprompt.py` | Estratos 18.546 / 1.065 / 112 / 80 — saída colada pelo autor |
| Aplicar revisão | `python scripts\amostrar_hackaprompt.py --aplicar-revisao` | **3 divergências**; distribuição 13/7/10/10 — saída colada pelo autor |

## Procedimentos **propostos e não executados**

Os três blocos de comandos da seção 10. Em particular, `--apenas-estratos` e `--refazer` são **flags novas, implementadas hoje e nunca executadas na máquina do autor**.

## Histórico de commits conhecido

⚠️ Obtido de saídas de `git log` que o **autor colou na conversa**. Não foi possível rodar `git` hoje.

| Commit | Assunto |
|---|---|
| `7d09f48` | Etapa 1: matriz com 14 critérios em quatro grupos e conferência cruzada |
| `94dd70c` | Etapa 1: atualização semanal ao orientador |
| `ce29a76` | Correções de revisão externa |
| `c35ee2b` | Etapa 2: serviço de recuperação, fluxo n8n ponta a ponta com stubs |
| `8497254` e `1f5783c` | Etapa 2 concluída — **commit duplicado** (bloco executado duas vezes) |
| `ee7cf3d` e `1f1b51a` | Arquivamento da primeira amostra — **duplicado**, e o segundo **sobrescreveu** o primeiro com versão sem a revisão |
| `e3c8917` | Restaura arquivamento sobrescrito, a partir de `ee7cf3d` |
| `f72d681` | Tarefa 3.3 com a regra defeituosa, **anterior à correção** |
| `1316332` | ADR-0017 rev. 2 |
| `338efc6` | Revisão manual dos 40 casos da segunda amostra |

**Por que `f72d681` importa:** todo o argumento de legitimidade da correção — "falseamento do instrumento antes do congelamento, não ajuste ao resultado" — depende de o estado defeituoso estar no histórico **antes** da correção. Até 17/09 a tarefa 3.3 inteira estava **sem commit**, e isso foi detectado e corrigido nessa sessão.

## Problemas conhecidos

| Problema | Estado |
|---|---|
| **Commits duplicados** por reexecução de blocos de comandos | Ocorreu 3 vezes. Instrução: rodar cada bloco **uma vez só** |
| **Excel trava o CSV de revisão** | `PermissionError` ao gravar. Fechar o Excel antes de rodar os scripts |
| Escrita não atômica destruía coerência entre JSON e CSV | **Corrigido** — `os.replace` + CSV antes do JSON |
| Reamostragem apagava revisão manual em silêncio | **Corrigido** — guarda `impedir_descarte_de_revisao` + livro de rótulos |
| "Concordância por silêncio" indistinguível de "não abriu o arquivo" | **Corrigido** — exige `--concordancia-total` |
| Colisão de pacotes `camada/app` vs `recuperador/app` | Corrigido com nomes únicos + `--import-mode=importlib` |
| Python convertendo `\n`→`\r\n` no Windows quebrava reprodutibilidade de hash | Corrigido com `newline=""` |
| **Ponte de comandos com a máquina do autor quebrada** | Atualização do Windows de 08/09. Leitura e escrita de arquivos funcionam; execução não |

## Incidente de segurança registrado

O autor compactou a pasta do projeto **incluindo o `.env` com a chave de API da Anthropic** e enviou a um serviço de IA de terceiros. Foi orientado a revogar a chave, e **confirmou**: "já troquei a chave". Recomendação registrada para o futuro: usar `git archive --format=zip HEAD` para empacotar, o que respeita o `.gitignore`.

---

# 10. Pendências e próximos passos

> A ordem abaixo é **proposta pelo assistente**, exceto onde indicado. Não houve acordo formal sobre prioridades com o autor ou o orientador.

## P1 — Fechar a tarefa 3.3 (bloqueia o resto da Etapa 3)

### P1.1 — Bloco 1: verificação (não grava nada) — **quem age: autor**

```powershell
& "$HOME\venvs\tcc-camada\Scripts\Activate.ps1"
cd "C:\Users\Simi\OneDrive\Desktop\Desenvolvimento TCC\tcc-camada-protecao"

python -m pytest -q --import-mode=importlib
python scripts\amostrar_hackaprompt.py --apenas-estratos
python scripts\conferir_reclassificacao.py conjunto_teste\revisao\hackaprompt_revisao-v1.csv
python scripts\conferir_reclassificacao.py conjunto_teste\revisao\hackaprompt_revisao.csv
```

**Resultado esperado** (projeção do assistente, **não verificada na máquina do autor**):

| Comando | Esperado |
|---|---|
| `pytest` | 129 passed (114 anteriores + 15 novos) |
| `--apenas-estratos` | comparar com 18.546 / 1.065 / 112 / 80 |
| conferir v1 | 9/9 |
| conferir atual | 2/3 — a divergência restante é a `ordem` 14, que é a limitação declarada. **Sai com código de erro 1; isso é esperado** |

**Concluída quando:** as quatro saídas forem conferidas. Se `pytest` der menos que 129 ou a conferência v1 der menos que 9/9, **parar e investigar**.

### P1.2 — Bloco 2: arquivar e commitar — **quem age: autor**

```powershell
Copy-Item conjunto_teste\selecao\hackaprompt.json `
          conjunto_teste\selecao\hackaprompt-v2-regra-rev2.json
Copy-Item conjunto_teste\revisao\hackaprompt_revisao.csv `
          conjunto_teste\revisao\hackaprompt_revisao-v2.csv

git add scripts\classificar_codificacao.py scripts\amostrar_hackaprompt.py `
        scripts\tests\test_classificar_nfkc.py `
        conjunto_teste\selecao\rotulos.json `
        conjunto_teste\selecao\hackaprompt-v2-regra-rev2.json `
        docs\decisoes\0017-amostragem-hackaprompt.md
git commit -m "ADR-0017 rev. 3: criterio sobre a saida da NFKC, e livro de rotulos por hash"
```

⚠️ **Uma vez só.** Foi a repetição deste bloco que sobrescreveu o arquivamento em 11/09.

### P1.3 — Bloco 3: terceira amostra — **quem age: autor**

```powershell
python scripts\amostrar_hackaprompt.py --refazer
```

Depois abrir `conjunto_teste\revisao\hackaprompt_revisao.csv`, que agora tem coluna `classe_herdada`. **Revisar apenas as linhas em que ela estiver vazia.** Preencher `classe_revisada` só onde discordar. Fechar o Excel. Então:

```powershell
python scripts\amostrar_hackaprompt.py --aplicar-revisao
# ou, se revisou os inéditos e concorda com todos:
python scripts\amostrar_hackaprompt.py --aplicar-revisao --concordancia-total

git add conjunto_teste\selecao\hackaprompt.json conjunto_teste\selecao\rotulos.json
git commit -m "terceira amostra, com rotulos herdados do livro e revisao dos casos ineditos"
```

## P2 — Tarefas restantes da Etapa 3

| # | Tarefa | Requisito | Quem age | Concluída quando |
|---|---|---|---|---|
| 3.4 | Mapear cada rótulo de origem para os quatro grupos da matriz (INJ, PII, CTX, NOC), com critério textual, autoria e data | **RQ-04** | IA + autor | Seção própria pronta para `CONGELADO.md` |
| 3.5 | Desenhar o corpus de PII com **negativos difíceis** | **RQ-02, RQ-03** | IA + autor | Desenho aprovado pelo autor |
| 3.6 | Gerar o corpus com semente fixa, gabarito por offset, testes | RQ-02 | IA | Gabarito versionado, com contagem declarada de positivos e negativos difíceis por tipo |
| 3.7 | Protocolo de contaminação/restauração do BIPIA (75 cenários) | **RQ-18** | IA | Restauração verificável por hash da coleção |
| 3.8 | **Escrever as 100 mensagens legítimas** | — | **Só o autor** | 100 mensagens em `conjunto_teste/legitimas/` |
| 3.9 | Separar conjunto de desenvolvimento do congelado | **RQ-06** | IA | `conjunto_desenvolvimento/` existe; nenhum caso em comum, verificado por hash |
| 3.10 | Fechar as fórmulas dos indicadores em `docs/protocolo.md` §8 | **RQ-19** | IA + autor | Seção 8 fechada **antes** do congelamento |
| 3.11 | **Congelamento**: `CONGELADO.md` datado, com hashes, rotulação, versões e licenças | RQ-03, RQ-04, RQ-05 | autor | Arquivo criado, datado e commitado |

> **P2.3.8 é o gargalo real do cronograma.** É o único item que depende exclusivamente do autor e que a IA não pode adiantar — `docs/plano-de-corte.md` lista as 100 mensagens redigidas manualmente entre "o que nunca é cortado", porque substituí-las por texto gerado subestimaria a taxa de falsos positivos, que é precisamente a crítica metodológica que o trabalho dirige à literatura. O assistente recomendou começar em paralelo desde 11/09; **não há evidência de que tenha começado**.

## P3 — Pendências fora da Etapa 3

| Pendência | Requisito | Quem age |
|---|---|---|
| Verificar o conteúdo e a licença de cada conjunto quanto à presença de dados pessoais | RQ-17 (cumprido parcialmente) | IA |
| Confirmar a licença do BIPIA no arquivo `LICENSE` | `ORIGEM.md` | IA |
| Verificar se a conta OpenAI aceita o endpoint de moderação sem meio de pagamento | ADR-0006 ("Verificar isso na Etapa 0, não no dia da execução") | autor |
| Execução de sanidade do Presidio **em português** antes do congelamento | **RQ-11** — pré-requisito da validade da condição C | IA + autor |
| Validação de `docs/matriz_criterios.md` por professor de cibersegurança | — | orientador |
| Conferir os números de Alves et al. (2025) | RQ-20 item 1 | autor |

---

# 11. Ponto exato de interrupção

**Último pedido do autor relacionado ao desenvolvimento, antes deste registro:**

Em 17/09/2026, o autor colou a saída de `--aplicar-revisao` mostrando **3 divergências** e distribuição 13/7/10/10, seguida do `git add` e `git commit` bem-sucedidos (`338efc6`). Não formulou um pedido textual — entregou o resultado para o assistente analisar.

**O que foi entregue em resposta:**

1. Diagnóstico dos 3 casos divergentes, com evidência de nível de caractere (extraída do CSV, **sem reproduzir texto de ataque**): ordens 19 e 20 escrevem a palavra-alvo com **letras circuladas** (categoria `So`) mais `е` cirílico; ordem 14 usa cinco maiúsculas cirílicas, três delas sósias de letras latinas.
2. Identificação de **dois defeitos mecânicos distintos**, ambos contrariando o texto da regra R1.
3. Uma pergunta ao autor com três opções. **O autor escolheu: "Corrigir o defeito 1 + livro de rótulos".**
4. Implementação completa da revisão 3 e do livro de rótulos, **escrita nos arquivos do repositório do autor**.
5. Três blocos de comandos para o autor executar.

**O que ficou incompleto:**

**Nenhum dos três blocos foi executado.** O estado do repositório é:

| Arquivo | Estado |
|---|---|
| `scripts/classificar_codificacao.py` | Revisão 3 escrita, **não testada na máquina do autor, não commitada** |
| `scripts/amostrar_hackaprompt.py` | Livro de rótulos + `--apenas-estratos` + `--refazer`, **não commitado** |
| `scripts/tests/test_classificar_nfkc.py` | 42 testes (27 + 15 novos), **não commitado** |
| `conjunto_teste/selecao/rotulos.json` | 71 decisões humanas semeadas, **não commitado** |
| `docs/decisoes/0017-amostragem-hackaprompt.md` | Revisão 3 anexada, **não commitada** |

> **Evidência disponível:** a ferramenta de escrita retornou confirmação de que os cinco arquivos foram gravados nos caminhos indicados. Os testes foram executados **em cópias, num container isolado** (57 testes passando, 9/9 na conferência v1, 2/3 na atual). **Isso não é evidência de que rodem na máquina do autor.**

**Arquivo/problema em trabalho no momento da interrupção:** tarefa 3.3 — amostragem estratificada do HackAPrompt, ADR-0017 revisão 3.

**Próxima ação para continuar daqui:** executar o **Bloco 1 (P1.1)** e conferir as quatro saídas.

---

# 12. Preferências de trabalho do autor

Registradas apenas onde o autor as expressou.

## Linguagem e tom

- **Português**, respostas **lacônicas e diretas**.
- Evitar "IA slop": linguagem inflada, genérica, com floreio.
- **Discordar quando algo estiver tecnicamente ruim.** O autor pediu isso explicitamente.

## Nível de detalhamento

- **"Preciso que sempre me explique o que estamos fazendo e para quê. Pois preciso do contexto para entender o projeto e futuramente explicar para meus orientadores."** *(mensagem literal do autor)*
- Explicar o **porquê** de cada passo técnico, sem floreio. As duas coisas valem juntas.
- Usar **tabelas** para comparações.

## Forma de trabalhar

- **Decompor antes de implementar.** Uma etapa por vez, com confirmação antes de seguir.
- **O mais arriscado primeiro.**
- Entregar **código completo e executável**, com caminho de arquivo.
- Terminar toda resposta com um **próximo passo concreto**.
- Preencher o arquivo entregue diretamente, em vez de só responder no chat.

## Verificação

- **"Nunca invente nome de biblioteca, parâmetro de API, versão ou comando."** *(instrução literal)*
- Verificar antes de afirmar.
- Registrar decisões como **ADR** em `docs/decisoes/`, no mesmo dia.

## Terminologia

- Nomes **em português** no domínio, em inglês nas convenções da linguagem. *(constituição, item 6 do fluxo de desenvolvimento)*
- Preservar os nomes exatos: `camada`, `recuperador`, `modelo`, `executor`, `conjunto_teste`, `CONGELADO.md`, `GuardaOrcamento`, `SEMENTE_MESTRA`.

## Segurança e manuseio

- Configuração por variável de ambiente. **Nenhum segredo no repositório.** `.env` fora do Git.
- **Material de ataque:** "Trate esse material como objeto de pesquisa: ajude a processá-lo, classificá-lo e medi-lo **sem reproduzir conteúdo nocivo além do necessário** para a tarefa técnica. Referir-se a um caso por identificador e categoria costuma bastar." *(instrução literal do autor)*
- Não versionar arquivos que contenham texto de ataque.

## Condutas a evitar

- Não sugerir ampliar categorias de risco, acrescentar conjuntos de teste ou comparar mais ferramentas. **Escopo fechado.** O relevante que estiver fora vira trabalho futuro.
- Não tratar desempenho ruim como defeito a corrigir depois da execução.

## Alterações que exigem validação do autor

- Qualquer mudança de escopo, critério de medição ou fórmula de indicador.
- Qualquer decisão que vire ADR.
- **Commits.** O autor commita, e as mensagens de commit são dele. O assistente prepara arquivos e comandos.

## Instrução permanente

> **Em qualquer dúvida ou ambiguidade, consulte o usuário. Ele pode esclarecer o contexto, resolver conflitos e explicar melhor suas intenções. Não substitua esse esclarecimento por suposições.**

---

# 13. Inconsistências, riscos e perguntas abertas

## Perguntas que dependem do autor

**Grupo A — a monografia**

1. **Onde está o texto do TCC?** Não há proposta, sumário nem capítulos neste repositório. Existe em Word, Google Docs, outro lugar? *Afeta:* praticamente toda a seção 7 deste documento está vazia por causa disso. *Como resolver:* o autor indica onde está e anexa no novo chat.
2. **O título do `README.md` é o título final ou provisório?**
3. **Onde está o plano de desenvolvimento com as Etapas 0 a 7?** É citado em `README.md`, ADR-0001 e `docs/plano-de-corte.md`, mas não está no repositório. A tabela de etapas da seção 7 foi **inferida**.

**Grupo B — orientação e aprovações**

4. **O orientador chegou a indicar o professor de cibersegurança** para validar `docs/matriz_criterios.md`? *Afeta:* é a única validação externa prevista para a matriz.
5. **Algum artefato foi formalmente aprovado pelo orientador?** Este documento registra que **nenhum** consta como aprovado, apenas commitado pelo autor. Se houver aprovação, precisa ser registrada.
6. **Existem atualizações semanais ao orientador posteriores a 10/09?** A constituição exige cadência semanal; a última em `docs/atualizacoes/` é de 10/09.

**Grupo C — metodologia do Spec Kit**

7. **A pasta `specs/` está vazia.** A constituição e o `README.md` afirmam que "cada etapa produz especificação, plano técnico e lista de tarefas em markdown, **versionados no repositório público antes da implementação**". Isso **não está sendo cumprido**. *Afeta:* é uma afirmação metodológica que a banca pode verificar. *Opções:* (a) produzir os artefatos retroativamente — o que seria desonesto se apresentados como anteriores à implementação; (b) emendar a constituição por ADR, registrando que o Spec Kit foi adotado como âncora metodológica mas os artefatos por etapa não foram produzidos; (c) o autor esclarece se eles existem em outro lugar. **Decisão do autor necessária.**

**Grupo D — cronograma**

8. **As 100 mensagens legítimas foram iniciadas?** Não há evidência. Faltam ~9 semanas para 24/11.
9. **Este `CONTEXTO_TCC.md` deve ser commitado no repositório?**

## Inconsistências identificadas

| # | Inconsistência | Evidência | Afeta | Como resolver |
|---|---|---|---|---|
| I1 | O documento de projeto `claude/decisoes-etapa-0.md` (claude.ai) contém valores **superados**: `TETO_CHAMADAS=4500`, custo projetado de US$ 7,38, e o caminho antigo `C:\Users\Simi\ProjetosGit\...` | Comparação direta com `docs/decisoes/0001-...md` e `docs/orcamento.md`, ambos lidos hoje | Quem ler o documento de projeto pode usar números errados | **Os arquivos do repositório prevalecem.** O documento de projeto deveria ser atualizado ou marcado como histórico |
| I2 | `specs/` vazia contradiz a metodologia declarada | Listagem de diretório | Afirmação metodológica verificável pela banca | Pergunta 7 |
| I3 | `conjunto_teste/ORIGEM.md` registra a licença do BIPIA como "confirmar no arquivo LICENSE do repositório" | Arquivo lido hoje | RQ-05 exige licença registrada | Ler `conjunto_teste/origem/bipia/LICENSE` |
| I4 | RQ-17 consta como "cumprido parcialmente — verificação dos conjuntos pendente" | `docs/requisitos-herdados.md` | Nenhuma etapa deveria fechar com requisito herdado em aberto | Executar a verificação antes do congelamento |
| I5 | Commits duplicados (`8497254`/`1f5783c`, `ee7cf3d`/`1f1b51a`) no histórico | `git log` colado pelo autor | Ruído no histórico; um deles **destruiu conteúdo** e precisou de `e3c8917` | Não reescrever histórico. Já registrado na ADR-0017 |

## Suspeitas a verificar (não confirmadas)

| # | Suspeita | Por que suspeito | Como verificar |
|---|---|---|---|
| S1 | A afirmação de que LLM08 (2026) é o renomeado LLM07 System Prompt Leakage (2025) vem do resumo da conversa, não de leitura do PDF nesta sessão | Não reconferida | Abrir `docs/referencial/OWASP-GenAI-LLM-Top-10-2026-v1.0 (1).pdf` p. 46 |
| S2 | Os números de Alves et al. (51,97% e 122 falsos negativos) nunca foram conferidos no texto integral | RQ-20 item 1 diz isso explicitamente | Obter o artigo |
| S3 | A projeção de "129 passed" no Bloco 1 é aritmética do assistente (114 − 27 + 42), não medição | Não executado | Rodar o Bloco 1 |
| S4 | A estimativa de que ~30% do estrato `idioma_ou_escrita_distinta` estava mal classificado vem de 3 acertos em 10 — intervalo de confiança de 95% aproximadamente entre 8% e 65% | Amostra pequena | Declarar como estimativa com intervalo, nunca como valor pontual |

## Riscos metodológicos registrados

| Risco | Natureza |
|---|---|
| **Padrão recorrente de defeito:** por duas vezes o classificador usou uma tecnicalidade Unicode como substituto de uma noção semântica — nome de caractere no lugar da propriedade Script, depois categoria geral no lugar de "letra". Está registrado na ADR-0017 porque é o padrão, e não cada defeito isolado, que explica como os dois passaram | Instrumentação |
| **Três episódios de decisão humana quase perdida** entre 11 e 17/09, todos por a revisão morar num CSV que a execução seguinte sobrescrevia | Registro — mitigado pelo livro de rótulos |
| **A janela de correção fecha com o congelamento.** Depois de `CONGELADO.md` datado, qualquer correção no classificador vira ajuste orientado ao resultado e está vedada pelo Princípio V | Validade |
| **Alocação igual ≠ proporcional.** Nenhum agregado pode ser calculado sobre os 40 casos sem reponderar por $w_h = N_h/N$. E o agregado ponderado seria ~93,7% determinado por `texto_simples`, escondendo exatamente o que a estratificação existe para revelar. **`INJ-05` reporta por estrato, nunca agregado** | Análise |
| **n = 10 por estrato dá intervalo largo.** Uma proporção de 8/10 tem IC 95% aproximadamente entre 44% e 97%. RQ-13 exige contagem e intervalo junto de todo percentual | Análise |

---

# 14. Instruções para a próxima IA

1. **Leia este documento e depois os arquivos de Prioridade 1** da seção 4: a constituição, `docs/requisitos-herdados.md`, `docs/decisoes/0017-amostragem-hackaprompt.md` e `docs/protocolo.md`.
2. **Informe ao autor quais arquivos conseguiu acessar**, antes de afirmar qualquer coisa sobre o estado do projeto.
3. **Verifique antes de editar.** Este documento é um resumo; o repositório é a fonte. Onde divergirem, o repositório prevalece.
4. **Preserve as distinções** entre fato confirmado, proposta, decisão aprovada e pendência. Não transforme sugestão em decisão por continuidade de conversa.
5. **Consulte o autor diante de qualquer dúvida, ambiguidade ou conflito.** Ele pediu isso explicitamente e responde bem a perguntas agrupadas.
6. **Trabalhe nas partes independentes** enquanto aguarda esclarecimentos. As tarefas 3.4 a 3.10 têm partes que não dependem das perguntas da seção 13.
7. **Não refaça trabalho concluído** sem razão concreta. As Etapas 0, 1 e 2 estão fechadas e commitadas.
8. **Não invente** nome de biblioteca, parâmetro de API, versão, comando, fonte, dado, resultado ou aprovação.
9. **Retome pelo ponto de interrupção** da seção 11: o Bloco 1 de verificação.
10. **Registre novas decisões** como ADR em `docs/decisoes/`, no mesmo dia, e atualize este documento quando algo relevante mudar.

## Três avisos específicos deste projeto

**A.** A restrição mais importante é a **ordem dos fatos**. Congelar antes de escrever regras; commitar o estado defeituoso antes de corrigir; escrever o critério antes de julgar. O histórico público de commits é o que sustenta isso perante a banca — por isso um commit fora de ordem é um problema metodológico, não de organização.

**B.** **O material de ataque não se reproduz.** Refira-se a um caso por identificador e categoria. Para descrever uma técnica, use evidência de nível de caractere (nomes Unicode, contagens, palavra reconstruída por NFKC) em vez de citar o texto. Os CSVs de revisão estão no `.gitignore` por esse motivo.

**C.** **Desempenho ruim da camada é resultado válido**, registrado assim por recomendação expressa da banca. Se os indicadores forem desfavoráveis, reporte e discuta. Nunca ajuste regra depois de ver resultado.
