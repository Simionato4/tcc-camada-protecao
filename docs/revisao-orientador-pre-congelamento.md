# Revisão do orientador antes do congelamento

Preparado em 31/10/2026 para o Prof. Me. Muriel Mazzetto, conforme combinado na
orientação de 21/10/2026: **os documentos são revisados antes de o conjunto de teste ser
congelado**. Depois do congelamento, conjunto, fórmulas e critérios não mudam mais
(constituição, princípio I).

Repositório: https://github.com/Simionato4/tcc-camada-protecao

---

## 1. Correções ao que relatei na reunião de 21/10

Ao conferir o repositório depois da reunião, percebi que descrevi alguns pontos de forma
imprecisa:

| O que eu disse | Como está de fato |
|---|---|
| "Cerca de 1.400 ataques" | O conjunto tem 1.519 casos, e nem todos são ataques: 939 perguntas nocivas (Do-Not-Answer), 355 textos com dados pessoais sintéticos, 115 injeções (75 BIPIA + 40 HackAPrompt), 10 de extração de contexto e 100 mensagens legítimas |
| "Dados sensíveis: CPF e nome" | São 7 tipos: CPF, CNPJ, PIS, cartão do SUS, título de eleitor, celular e e-mail. Nome não é tipo avaliado |
| "O sistema trata CPF formatado e não formatado" | A camada **ainda não tem regra nenhuma**: as regras só podem ser escritas depois do congelamento. O que existe é o **conjunto de teste** com CPF formatado, sem formatação e, depois da reunião, **parcialmente formatado** (seção 3) |
| "A verificação de injeção é só no fim do documento" | O fim do documento é a **posição do ataque nos cenários de teste**, e não um limite da verificação. Testar só essa posição fica declarado como limitação |
| "O hash verifica se o agente alterou o documento" | O hash usado é de **integridade do experimento**: prova que o conjunto de teste e a base de documentos não mudaram. Não é uma funcionalidade do gateway (seção 2.3) |
| "O Presidio vai detectar nomes brasileiros com regras e um dicionário" | Não foi feito, e a decisão foi a oposta: **adaptação mínima** do Presidio ao português, sem reconhecedores nossos (seção 3) |

---

## 2. Escopo do TCC1

### 2.1 Cenário e atores
Atendimento ao cliente de uma loja de comércio eletrônico fictícia (Aurora). O gateway
fica **no meio**, entre o assistente e o resto, e intercepta três pontos.

| Ator | Papel |
|---|---|
| Cliente | escreve no chat; pode ser legítimo ou mal-intencionado |
| Assistente | fluxo n8n que consulta a base e chama o modelo de linguagem |
| Base de conhecimento | 30 documentos de pedidos, com dados pessoais sintéticos dos clientes |
| Autor de documento contaminado | atacante que esconde instrução dentro de um documento da base (injeção indireta) |
| **Gateway (camada)** | intercepta a mensagem do cliente, o conteúdo recuperado e a resposta, e decide: encaminhar, bloquear, mascarar ou alertar |

```
Cliente -> [n8n] -> camada /entrada -> recuperador (Qdrant) -> camada /contexto
        -> modelo -> camada /saida -> Cliente
```

### 2.2 Funcionalidades: regra × modelo de linguagem
Pedido da orientação: separar o que é regra determinística do que passa por modelo. As
linhas da camada descrevem o **desenho previsto**: as regras só são escritas depois do
congelamento.

| Funcionalidade | Técnica | Usa LLM? |
|---|---|---|
| Normalização (caracteres invisíveis, variantes tipográficas, homóglifos) | regra (Unicode, NFKC) | não |
| Detecção de injeção de instrução | padrões e regras | não |
| Detecção de dado pessoal brasileiro | padrão de formato + dígito verificador | não |
| Mascaramento | regra | não |
| Decisão (encaminhar, bloquear, mascarar, alertar) | regra | não |
| Registro de operação (JSON Lines) | código | não |
| Resposta ao cliente | **modelo de linguagem** (Claude Haiku 4.5), só no assistente | **sim**, fora da camada |
| Comparador C (Presidio) | padrões + reconhecimento de entidade (spaCy) | não (modelo estatístico, não generativo) |
| Comparador D (moderação OpenAI) | classificador treinado, via API | serviço externo |

A camada é **inteiramente determinística**. É a tese do trabalho: o controle crítico
fica fora do modelo (OWASP LLM08:2026, controle #2).

### 2.3 Sobre o hash (pergunta da reunião)
No TCC1 o hash não é funcionalidade do gateway. Ele é **evidência do método**: o
conjunto de teste e a coleção do banco vetorial são conferidos por hash, e um hash
divergente torna o caso inválido. A verificação de integridade de documento num
pipeline (o exemplo do currículo processado por um agente) fica como **trabalho futuro**.

### 2.4 Fica para o TCC2
Verificação de injeção em qualquer posição do documento; pipeline de documento com
verificação de integridade; detecção de nomes de pessoa; ataques adaptativos; ataques
multimodais; outros idiomas. Integração por API ou MCP com o assistente de uma empresa.

---

## 3. O que mudou desde a reunião

| Decisão | Onde |
|---|---|
| **CPF parcialmente formatado** (sua observação): formato parcial nos cinco documentos e no celular; metade dos negativos de dígito inválido também parcial, para o formato não virar pista | ADR-0015, revisão de 28/10 |
| **Presidio com adaptação mínima para português**: modelo spaCy pt, idioma pt, só os reconhecedores que já vinham ativos e sem país; sem reconhecedor brasileiro e sem ajuste ao conjunto | ADR-0022 |
| **100 mensagens legítimas redigidas à mão**, em 5 blocos de 20 (ortografia ruim, corporativo, atendimento, vocabulário sensível, números do dia a dia), com guia escrito antes | ADR-0023, `docs/guia-mensagens-legitimas.md` |
| **Falso positivo, duas correções**: entidade fora dos 7 tipos não conta como erro (D8); mascarar dado pessoal da base de conhecimento numa mensagem legítima é acerto, não erro (D9) | ADR-0020, D8 e D9 |
| **Dados pessoais nos conjuntos públicos**: 1.064 casos varridos, nenhum dado pessoal real | ADR-0024 |
| **OWASP 2026**: as 9 citações da matriz conferidas página a página | ADR-0025 |

---

## 4. O que revisar, por prioridade

| # | Documento | O que olhar |
|---|---|---|
| 1 | `docs/protocolo.md`, seção 8 | as fórmulas: contenção, falso positivo, mascaramento, Wilson |
| 2 | `docs/matriz_criterios.md` | os 14 critérios e as restrições declaradas |
| 3 | `docs/decisoes/` (ADR-0014 a 0025) | as decisões desta etapa |
| 4 | `.specify/memory/constitution.md` | as regras que nenhuma etapa pode violar |
| 5 | `docs/plano-de-corte.md` | o que pode e o que não pode ser cortado se o prazo apertar |
| 6 | `docs/requisitos-herdados.md` | requisitos da revisão externa (o estado de cada um é atualizado no fechamento da etapa) |
| 7 | `docs/texto-limitacoes-e-trabalhos-futuros.md` | redação das limitações |

## 5. Perguntas para o senhor

1. A **adaptação mínima** do Presidio (ADR-0022) é um comparador justo?
2. As regras de **falso positivo** D8 e D9 (ADR-0020) estão corretas?
3. O **escopo do TCC1** e o que fica para o TCC2 (seção 2) estão adequados para a apresentação?
4. Posso **congelar** o conjunto depois dos seus ajustes? O congelamento é o que libera a escrita das regras para a demonstração com o gateway.
