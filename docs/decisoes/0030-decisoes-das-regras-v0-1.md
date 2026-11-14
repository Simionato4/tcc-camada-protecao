# ADR-0030 - Decisoes de desenho das regras v0.1 (Etapa 4, Fase 1)

## Contexto
A Fase 1 da Etapa 4 foi implementada em 12/11/2026, depois do congelamento do conjunto de
teste. As decisoes abaixo foram tomadas pelo autor nesse dia, uma a uma, antes do codigo
de cada estagio, e ficaram registradas no cabecalho dos testes, no codigo e em
`specs/004-camada-intermediaria/tasks.md`. **Esta ADR foi escrita em 14/11/2026**, no
fechamento da etapa: reune o que estava espalhado, com a alternativa descartada de cada
decisao. A ordem dos fatos se confere pelos commits citados.

Todas foram tomadas sem executar a camada sobre o conjunto de teste congelado. As regras
foram desenvolvidas so contra `conjunto_desenvolvimento/` e contra exemplos escritos para
os testes.

## Decisoes (do autor, 12/11/2026)

| # | Ponto | Escolha | Alternativa descartada | Motivo |
|---|---|---|---|---|
| R1 | NFKC e mapa de posicoes | Quando um caractere do original vira varios, todos apontam para o mesmo indice de origem; NFKC aplicado por agrupamento (letra e marcas de combinacao) | NFKC sobre o texto inteiro | Sobre o texto inteiro nao da para saber de onde veio cada caractere (RQ-07). Limite declarado: escritas em que dois caracteres comuns se fundem |
| R2 | Titulo de eleitor de SP e MG | Aceita o numero que fechar em qualquer uma das duas convencoes | so sem excecao; so com excecao | ADR-0015, revisao de 12/11/2026 |
| R3 | Candidato numerico | A sequencia inteira de digitos ligados por separador simples; nunca um pedaco | testar pedacos de uma sequencia maior | O PIS/NIT tem um digito verificador so: 1 em cada 10 numeros de 11 digitos fecha a conta. Limitacao aceita: dois documentos separados so por um espaco nao sao detectados |
| R4 | Numero que continua | Sequencia colada em virgula ou dois-pontos seguidos de digito nao e documento | aceitar | Valor em dinheiro e horario. Limitacao aceita: lista sem espaco depois da virgula |
| R5 | Colisao em 11 digitos | Qualquer tipo valido gera deteccao; rotulo por prioridade CPF, PIS/NIT, celular | rotulo pela mascara | No gabarito todo positivo e valido em um tipo so: a prioridade nao altera metrica, so precisa existir |
| R6 | Marca de mascaramento | Rotulo do tipo entre colchetes (`[CPF]`) | asteriscos do mesmo tamanho | O texto continua legivel; asteriscos revelam formato e comprimento |
| R7 | Dado pessoal na `entrada` | Detecta e informa, mas encaminha sem mascarar; mascara no `contexto` e na `saida` | mascarar tambem na entrada | O cliente esta informando o proprio dado; a RF-005 so fala em contexto e saida |
| R8 | Onde as regras valem | So na condicao B; em A e C a camada encaminha; em D, so a moderacao, e so na entrada | regras ativas em todas | E o que torna a diferenca medida atribuivel a camada (ADR-0027, E5) |
| R9 | Marcador na `saida` | Bloquear a resposta inteira, com texto vazio | mascarar so o marcador | Mascarar esconderia a evidencia e entregaria o resto do vazamento; a metrica diria "contido" sem a protecao melhorar |
| R10 | Bloco de tag | Tratado como codificacao: o texto escondido e decodificado e analisado | so remover na normalizacao | A camada encaminha o original: instrucao escondida passaria sem ser lida |
| R11 | Injecao | Quatro familias de padrao (anular, mudar o regime, nova ordem, extrair), em portugues e ingles, sobre varias vistas do texto; instrucao reconhecida bloqueia na `entrada` e no `contexto` | - | Regras aprovadas antes do codigo; limitacao central do `INJ-02`: outra redacao passa |
| R12 | Conteudo codificado sem instrucao reconhecida | `alertar`: encaminha o original e registra | bloquear; ignorar | Bloquear geraria falso positivo; ignorar perderia o sinal. Alertar nao conta como falso positivo (ADR-0020, D2) |
| R13 | Tres injecoes do desenvolvimento nao bloqueadas (57 de 60) | Nao afrouxar o padrao | aceitar palavra mutilada ("instru" em vez de "instruc") | As tres falhas vem do gerador, que descartou as letras acentuadas no bloco de tag; afrouxar casaria com "instrumento" e "instruir" |
| R14 | Texto devolvido no bloqueio | Vazio | devolver o original junto da decisao | A protecao nao pode depender de o fluxo ignorar o texto |
| R15 | Registro | Nao grava texto nenhum; de cada deteccao, so tipo e posicao | gravar o texto mascarado | `PII-03` cumprido por construcao. Limite declarado: o resumo criptografico nao e anonimizacao |
| R16 | Versao das regras | Constante do codigo (`0.1.0`) | variavel de ambiente | Um rotulo configuravel por fora poderia informar uma versao que nao e a que roda |
| R17 | Recusa por validacao (HTTP 422) | A resposta de erro nao devolve o conteudo recebido | tratamento padrao do FastAPI | O padrao ecoava o texto recusado (possivel dado pessoal) e dava erro 500 com texto Unicode invalido. Defeito anterior a etapa, commitado antes da correcao (`6c96a71`, `dd3829c`) |
| R18 | Demonstracao | Com o modelo real, depois de testar | modelo simulado | Testes de 12/11/2026 em `docs/orcamento.md` e `docs/roteiro-demonstracao.md`. O que foi observado e dito na apresentacao, inclusive que o modelo recusou sozinho as duas injecoes testadas |

## O que nao foi alterado, de proposito
No ensaio da demonstracao (12/11/2026), a resposta da condicao B trouxe o **telefone fixo**
do cadastro de um documento da base. Telefone fixo esta fora dos sete tipos (ADR-0015).
**A regra nao foi alterada:** os documentos da base estao entre os arquivos congelados, e
mudar a camada depois de ver o que acontece com um deles seria ajuste orientado ao
resultado (constituicao, principios I e V). Se pesar na execucao, e resultado.

## Evidencia sobre o conjunto de desenvolvimento
- Dado pessoal, ponto `saida`, medido como o protocolo 8.4: VP 350, FN 0, FP 0.
- Injecao, pontos `entrada` e `contexto`: 57 de 60 bloqueadas; 0 de 60 benignas bloqueadas.

Estes numeros nao sao resultado do experimento: o conjunto de desenvolvimento foi gerado
pelo mesmo desenho do teste e mostra que as regras cobrem o que o desenho preve.

## Consequencia
As regras v0.1.0 podem evoluir ate a execucao (decisao registrada antes do congelamento),
sempre contra o conjunto de desenvolvimento e com mudanca de `VERSAO_REGRAS`. Depois da
execucao valida, nao mudam.

## Data
2026-11-14 (decisoes de 2026-11-12)
