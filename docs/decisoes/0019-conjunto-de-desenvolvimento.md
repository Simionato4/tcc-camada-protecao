# ADR-0019 - Conjunto de desenvolvimento separado do conjunto de teste

## Contexto
O RQ-06 exige que os exemplos usados para desenvolver e depurar as regras da camada
vivam em `conjunto_desenvolvimento/`, versionado e distinto de `conjunto_teste/`, e que
nenhum caso do conjunto congelado apareca no de desenvolvimento, verificado por hash caso
a caso. Congelar antes das regras nao elimina sozinho o vies de desenvolvimento: e
preciso que os exemplos de trabalho sejam outros, e que isso seja verificavel.

A constituicao (principio I) diz que as regras sao testadas "contra exemplos escritos
pelo autor para esse fim".

## Decisao
Decisao do autor, 14/10/2026: **opcoes A e B; C recusada.**

| Parte | Arquivo | Conteudo |
|---|---|---|
| A | `conjunto_desenvolvimento/pii/corpus.jsonl` | o mesmo gerador do corpus de teste (ADR-0015), com a semente `SEMENTE_MESTRA + 1` (20260830): mesmo formato e mesmas classes, outros numeros. 353 textos, 700 ocorrencias |
| B | `conjunto_desenvolvimento/injecao/exemplos.jsonl` | 12 frases-base escritas para este fim (6 com instrucao de injecao generica, 6 benignas de atendimento), cada uma sob 10 transformacoes: nenhuma, largura zero entre letras, seletor de variacao, bloco de tag, base64, codificacao percentual, separadores entre letras, variante tipografica, homoglifo e texto invertido. 120 exemplos. O rotulo e o do conteudo: frase benigna transformada continua benigna |
| B | `conjunto_desenvolvimento/pii/transformado.jsonl` | documentos validos da parte A sob ofuscacao (espaco, largura zero e largura cheia entre os digitos; base64), com a posicao no texto original e o valor esperado depois da normalizacao. 40 exemplos, material para o RQ-07 |

Os arquivos tem hash registrado e quebra de linha LF fixada pelo `.gitattributes`, como
`conjunto_teste/` (ADR-0018).

Gerado por `scripts/gerar_conjunto_desenvolvimento.py`, que **nao altera** o gerador do
corpus de teste: importa a mesma funcao de montagem e troca a semente e o destino.
Frases-base e transformacoes escritas com assistencia de IA, revisadas pelo autor.
Nenhum caso dos conjuntos publicos e reproduzido.

Cada exemplo de injecao registra tambem a classe que o classificador R1 da ADR-0017 lhe
atribui. As 10 transformacoes caem nas classes esperadas; o texto invertido cai em
`texto_simples`, porque sem frase-alvo a inversao nao e detectada (revisao 4 da
ADR-0017).

## Verificacao (RQ-06)
`scripts/verificar_separacao.py`, de leitura pura, compara por hash:

1. **texto inteiro**: cada texto do desenvolvimento contra cada caso do teste, pelo
   `sha256_texto` do mapeamento de rotulos (ADR-0018);
2. **valor de documento**: o mesmo CPF, CNPJ, CNS, PIS/NIT, titulo, telefone ou endereco
   nao pode estar nos dois corpus de PII, ainda que em frases diferentes. Esta segunda
   comparacao vai alem da letra do RQ-06, que fala em caso.

`scripts/tests/test_separacao.py` roda a verificacao a cada execucao da suite: todo
exemplo que a Etapa 4 acrescentar e conferido automaticamente. O teste falha, e nao
pula, se o conjunto de desenvolvimento nao existir.

**Excecoes declaradas na comparacao por valor.** A primeira execucao achou 4 valores em
comum: os tres dominios reservados no formato "@dominio" (classe E1) e um intervalo de
horario (classe T2). Nao sao casos copiados: sao classes cujo espaco de valores e finito
e pequeno por definicao, e que coincidem entre quaisquer dois corpus do mesmo desenho:

| Classe | Espaco de valores |
|---|---|
| N4 | as 10 sequencias de digitos iguais de cada comprimento |
| E1 sem parte local | 3 valores, um por dominio reservado |
| T2 de horario | 180 combinacoes de intervalo |

Essas tres ficam fora da comparacao por valor e continuam na comparacao por texto.

**Resultado, 14/10/2026:** 1.410 casos distintos do teste (1.411 registros do mapeamento,
menos a pergunta repetida do Do-Not-Answer, ADR-0018) contra 513 textos do
desenvolvimento: **0 textos em comum**. Valores de documento: 628 no teste, 628 no
desenvolvimento, **0 em comum**.

Conferido tambem o CPF de exemplo do teste de encaminhamento da camada, escrito na
Etapa 0 (`camada/tests/test_encaminhamento.py`): nao esta no corpus de teste.

## Alternativa considerada
**C - casos publicos fora do teste** (a divisao de treino do BIPIA,
`text_attack_train.json`, e casos do HackAPrompt fora das amostras). Material real, e o
BIPIA ja separa treino de teste. Recusada: tem o mesmo estilo dos casos de teste, e as
regras poderiam ficar ajustadas ao jeito do conjunto mesmo sem tocar nos casos
congelados. E foge da letra da constituicao, que fala em exemplos escritos para esse fim.

## Consequencia
A Etapa 4 tem material de trabalho para os tres estagios da camada (normalizacao,
deteccao, decisao) sem abrir `conjunto_teste/`. A separacao continua verificada depois
do congelamento, a cada exemplo novo.

Limitacao: os exemplos de injecao sao poucos (12 frases-base) e genericos; servem para
desenvolver e testar o mecanismo, nao para estimar desempenho. Desempenho se mede so no
conjunto congelado.

**RQ-06:** a aceitacao ("as duas pastas existem, e nenhum caso do conjunto congelado
aparece no de desenvolvimento - verificado por comparacao de hash caso a caso") tem
evidencia nesta ADR. A mudanca de estado do requisito e feita no fechamento da etapa.

## Data
2026-10-14

## Revisao de 28/10/2026: regeracao pelo formato parcial

O gerador do corpus de documentos ganhou o formato parcial de mascara (revisao de
28/10/2026 da ADR-0015). A parte A deste conjunto usa o mesmo gerador com a semente
`SEMENTE_MESTRA + 1`, e foi gerada de novo para manter o mesmo desenho do teste;
`transformado.jsonl` deriva dela e mudou junto. `injecao/exemplos.jsonl` nao mudou.

| Arquivo | Registros | sha256 |
|---|---:|---|
| `pii/corpus.jsonl` | 360 | `f9fab7d57bb68daa09890ea8e892745a62fa2de3bf05249660d01dd3f8091010` |
| `injecao/exemplos.jsonl` | 120 | `ed218d59366f5ca70f31ed514518381fbeb534aeb511fc7363384734f13bc3d6` |
| `pii/transformado.jsonl` | 40 | `aa694780939e6ade2ac88839b4f9fa00c23d3cdf6665226be10002c50dddec11` |

**Separacao verificada de novo** (`scripts/verificar_separacao.py`): 1.418 casos distintos do
teste (1.419 registros do mapeamento, menos a pergunta repetida do Do-Not-Answer) contra
520 textos do desenvolvimento, **0 textos em comum**; valores de
documento 628 no teste e 628 no desenvolvimento, **0 em comum** (excluidos os de espaco
finito, como antes).

A sanidade do Presidio da ADR-0022 rodou sobre a parte A anterior (353 textos), em
28/10/2026, antes desta regeracao; o registro bruto
`resultados/sanidade_presidio_pt_2026-10-28.json` se refere a ela.
