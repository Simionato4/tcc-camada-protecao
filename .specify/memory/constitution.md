# Constituicao do projeto — Camada intermediaria de protecao

Trabalho de Conclusao de Curso — Gabriel Simionato — Sistemas de Informacao, UNIMATER.

Este documento reune as regras que nenhuma etapa do desenvolvimento pode violar.
Ele nao descreve preferencias de estilo: descreve as condicoes sob as quais o
experimento produz evidencia valida. Violar qualquer principio abaixo nao gera um
defeito a corrigir — invalida o resultado.

## Core Principles

### I. Congelamento antes das regras (NAO NEGOCIAVEL)

O conjunto de teste e fechado, datado e registrado com hash de cada arquivo em
`conjunto_teste/CONGELADO.md` **antes** de a primeira regra da camada ser escrita.
Enquanto esse arquivo nao existir, os modulos `normalizacao.py`, `deteccao.py` e
`decisao.py` nao podem existir no repositorio.

Durante o desenvolvimento, as regras sao testadas contra exemplos escritos pelo
autor para esse fim. E proibido rodar o conjunto congelado, observar quais casos
falharam e ajustar a regra para acerta-los. Depois da execucao, desempenho ruim e
resultado a reportar, nao defeito a corrigir.

Verificacao: a data de `CONGELADO.md` precede o primeiro commit que introduz
qualquer regra; o campo `versao_regras`, presente em toda resposta da camada e em
todo registro bruto, permite reconstruir qual configuracao gerou cada medida.

### II. Nenhum dado pessoal real (NAO NEGOCIAVEL)

Nenhum dado pessoal real entra em qualquer etapa, em qualquer arquivo, em
qualquer registro. O corpus de documentos brasileiros e integralmente sintetico,
gerado com semente fixa.

Precisao necessaria: os conjuntos de ataque publicados sao **prompts reais**,
publicados em artigos revisados por pares, e nao texto sintetico. O que a regra
proibe e dado pessoal real, nao texto de origem real. O conteudo e a licenca de
cada conjunto sao verificados quanto a presenca de dados pessoais antes do
congelamento.

Os ataques sao executados exclusivamente contra o ambiente local construido para
a pesquisa, nunca contra servicos de terceiros.

A camada mascara dados pessoais nos proprios registros. Ate a Etapa 4 implementar
o mascaramento, o registro grava apenas tamanho e resumo criptografico do texto.

### III. Variaveis de controle permanecem fixas

Sao identicas nas quatro condicoes comparadas: o fluxo do assistente, o texto do
prompt de sistema, a base de conhecimento, o modelo de linguagem e sua versao, os
parametros de inferencia, o conjunto de teste, o equipamento e a ausencia de
historico entre requisicoes.

Consequencias operacionais:

- O modelo e um snapshot com identificador travado, com temperatura zero.
  Comparar modelos diferentes esta fora do escopo.
- Os tres pontos de chamada da camada existem no fluxo desde a condicao A,
  apontando para um endpoint que apenas encaminha. Adicionar nos ao fluxo entre
  condicoes alteraria a variavel de controle.
- A latencia e medida dentro da camada, isoladamente. Tempo de rede nao entra na
  metrica. Onde isso for impossivel — condicoes que dependem de servico externo —
  a limitacao e declarada antes da execucao, nunca depois de ver o resultado.

### IV. Custo e aleatoriedade sob controle de codigo

O credito de API e finito e um laco mal fechado inviabiliza o trabalho. Nenhum
modulo chama o modelo de linguagem fora de `executor/cliente_modelo.py`. Toda
chamada passa antes pelo `GuardaOrcamento`, que aplica teto de chamadas e teto em
dolares e persiste o consumo acumulado em disco. O modo simulado, sem chamada
real, e o padrao: gastar credito exige gesto explicito.

Toda aleatoriedade — amostragem, geracao de dados sinteticos, qualquer sorteio —
usa semente fixa, registrada em `.env` e documentada.

### V. Registro bruto imutavel e rastreavel

Registros de execucao nunca sao editados. Correcao gera nova execucao completa.

Distincao necessaria entre dois casos que nao sao equivalentes:

- **Defeito de instrumentacao** — erro no executor, no formato de registro, na
  medicao de tempo ou no tratamento de erro de API. Corrigir e legitimo e gera
  nova execucao. **Ambas as execucoes sao preservadas**, e o ADR correspondente
  registra o defeito, a correcao e por que a execucao anterior foi descartada.
- **Ajuste orientado ao resultado** — alterar regra da camada, criterio de
  julgamento ou formula de indicador apos observar o resultado. Proibido, sem
  excecao, e nenhuma justificativa de prazo o autoriza.

A diferenca esta na direcao da causa: no primeiro caso a correcao decorre de um
defeito identificavel independentemente do resultado; no segundo, decorre do
resultado.
Cada requisicao produz um registro com identificador, condicao, conjunto de
origem, categoria de risco, entrada, decisao, resposta final, tempo interno,
tempo total, numero da repeticao e versao das regras vigente.

O ambiente inteiro e reproduzivel por um comando, com imagens de conteiner
fixadas por digest e versao de cada componente registrada em `docs/versoes.md` no
momento da instalacao, obtida por comando e nao de memoria.

## Restricoes de escopo e de conduta

O escopo esta fechado. Nao se ampliam categorias de risco, nao se acrescentam
conjuntos de teste, nao se comparam mais ferramentas. O que for identificado como
relevante e estiver fora do escopo e registrado como trabalho futuro, nunca
incorporado.

Estao explicitamente fora: ofuscacao por traducao, ataques multimodais, ataques
adaptativos, tecnicas documentadas apos o congelamento, anonimizacao de documentos
de outros paises, conformidade juridica com a legislacao de protecao de dados,
analise estatica de codigo e comparacao entre modelos de linguagem distintos. A
cobertura e amostral, e nao exaustiva, e assim e declarada nos resultados.

Os conjuntos de ataque sao material publicado em artigos revisados por pares para
avaliacao de seguranca. Sao tratados como objeto de pesquisa: processados,
classificados e medidos, referidos por identificador e categoria, sem reproducao
de conteudo nocivo alem do necessario para a tarefa tecnica.

## Fluxo de desenvolvimento

1. Cada etapa produz especificacao, plano tecnico e lista de tarefas em markdown,
   versionados no repositorio publico antes da implementacao.
2. Toda decisao tecnica relevante vira um ADR curto em `docs/decisoes/` no mesmo
   dia, com a alternativa considerada e o motivo do descarte.
3. Cada estagio da camada e testavel isoladamente, com testes unitarios que
   passam antes de o estagio seguinte comecar.
4. Configuracao por variavel de ambiente. Nenhum segredo no repositorio. `.env`
   fora do Git desde o primeiro commit.
5. Registro estruturado, um evento JSON por linha, legivel por maquina.
6. Codigo legivel acima de codigo esperto: o autor precisa conseguir explicar cada
   linha a uma banca. Nomes em portugues no dominio, em ingles nas convencoes da
   linguagem.
7. Atualizacao semanal ao orientador, com o que foi feito, decisao tomada,
   evidencia, dificuldade e proximo passo.
8. Se uma etapa consumir a folga do cronograma, aplica-se o plano de corte
   previsto no plano de desenvolvimento, em vez de reduzir rigor.

## Governance

Esta constituicao prevalece sobre qualquer outra pratica adotada no projeto,
inclusive sobre sugestoes de ferramentas de assistencia por IA. Toda especificacao
e todo plano tecnico produzidos pelo Spec Kit sao verificados contra ela antes de
gerar tarefas.

Emendas exigem um ADR proprio, com justificativa, e incremento de versao deste
documento. Um principio marcado como NAO NEGOCIAVEL nao pode ser relaxado apos a
data de congelamento do conjunto de teste, sob nenhuma justificativa de prazo:
relaxa-lo depois dessa data significa ajustar o metodo ao resultado.

Conveniencia de prazo nunca e justificativa de emenda. Quando prazo e rigor
entrarem em conflito, corta-se escopo pelo plano de corte previsto, e a reducao e
declarada nos resultados.

**Version**: 1.0.0 | **Ratified**: 2026-08-31 | **Last Amended**: 2026-08-31
