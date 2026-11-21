# ADR-0031 - Decisoes da especificacao da Etapa 5 (executor e protocolo)

## Contexto
A especificacao da Etapa 5 (`specs/005-executor-e-protocolo/spec.md`, rascunho de
15/11/2026) deixou oito pontos marcados para decisao. Todos sao decididos antes de o
executor existir e antes de qualquer resposta a um caso do conjunto de teste.

## Decisoes (do autor, 21/11/2026: as oito recomendacoes da especificacao)

| # | Ponto | Escolha | Alternativa descartada | Motivo |
|---|---|---|---|---|
| P1 | Texto no registro bruto | Entrada e resposta inteiras, com o registro bruto **fora do Git**; versionam-se hashes e contagens | so resumo e tamanho | A rubrica e o julgamento manual precisam ler a resposta; texto de ataque nao se versiona (ADR-0016) |
| P2 | Quando escrever a rubrica | Nesta etapa, antes de o executor rodar qualquer caso do teste; preenche a secao 7 do protocolo | so na Etapa 6 | O RQ-09 exige a rubrica "escrita e congelada antes da execucao" |
| P3 | Grupo NOC (939 respostas por condicao) | Rubrica automatica por padroes de recusa, escritos antes, com validacao manual de amostra estratificada e concordancia medida; concordancia baixa leva o `NOC-01` para amostra, com a reducao declarada | julgamento manual integral | E o texto do RQ-09; o julgamento integral nao cabe no prazo |
| P4 | Erro de rede | Ate 3 tentativas com espera crescente para erro transitorio (tempo esgotado, 429, 5xx); erro permanente (401, 400) para a execucao; esgotadas as tentativas, `erro_tecnico`; ao fim, uma unica reexecucao dos casos com erro, em registros novos | sem nova tentativa | Os testes de 12/11/2026 mostraram o fluxo morrendo sem resposta quando a API falha |
| P5 | Ordem e parada | Por caso: as condicoes do mesmo caso em sequencia (A, B, D); BIPIA por cenario; corpus e latencia depois. Parada: teto de orcamento, erro permanente, hash divergente, 5 erros transitorios seguidos | uma condicao inteira por vez | Uma condicao por vez separaria A e B por horas; mudanca no servico do modelo no meio viraria diferenca entre condicoes |
| P6 | Registro da camada | Cada execucao com pasta e arquivo de registro proprios | arquivo unico com marcacao de linhas | Os testes automaticos gravam no mesmo arquivo da operacao (achado de 12/11, ADR-0029) |
| P7 | Mensagens do piloto | 20 mensagens escritas para o piloto (5 por grupo), nenhuma do conjunto de teste | 20 casos sorteados do conjunto de teste | Rodar casos do teste no piloto mostraria respostas antes da rubrica e da execucao valida |
| P8 | RQ-16 | Registrar o apelido devolvido, o identificador e o instante de cada chamada; rodar a condicao D numa janela continua; declarar que a versao efetiva nao e observavel | manter o requisito como esta | Verificado em 15/11/2026: o servico devolve `omni-moderation-latest`, o apelido; o requisito como escrito nao e cumprivel |

## Consequencia
A especificacao da Etapa 5 fica sem ponto em aberto e passa a aprovada. O RQ-16 e reescrito
no fechamento da Etapa 5, conforme P8. A secao 3 do protocolo (congelada) diz "20
mensagens, cobrindo os quatro grupos"; a P7 decide a origem delas, sem alterar o texto.

## Data
2026-11-21
