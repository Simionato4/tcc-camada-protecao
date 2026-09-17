# ADR-0017 - Universo, classificacao e amostragem do HackAPrompt

## Contexto
Verificacao do conjunto em 11/09/2026: **601.757 submissoes**, das quais **77.936
bem-sucedidas** (`correct = True`), distribuidas em onze niveis de dificuldade. O
conjunto nao rotula tecnica de ataque (ADR-0013).

A proposta preve amostra estratificada de 40 casos de injecao direta.

## Decisao

### Universo
Submissoes com `correct = True`, **sem duplicatas de texto**.

O filtro por sucesso e necessario: uma submissao que nao funcionou contra o modelo da
competicao nao e caso de ataque, e incluir tentativas fracassadas mediria a camada
contra texto que nao ataca nada.

A deduplicacao tambem e necessaria, por um motivo especifico desta fonte: uma
competicao acumula variacoes minimas do mesmo ataque, porque os participantes
repetem tentativas ate acertar. Sem deduplicar, a amostra de 40 traria menos de 40
tecnicas distintas, e a estratificacao — que e a razao de existir do criterio
`INJ-05` — perderia sentido.

A deduplicacao usa o texto de `user_input` normalizado apenas para espacos em branco
das extremidades, mantendo a primeira ocorrencia por data. Nenhuma normalizacao mais
agressiva e aplicada: remover invisiveis ou decodificar antes de deduplicar
descartaria exatamente as variantes que interessam.

### Classificacao
Pre-classificacao por **propriedade objetiva do texto**, seguida de **revisao manual
caso a caso** dos 40 selecionados.

As classes vem da taxonomia de codificacao do `LLM01:2026` (ADR-0013):

| Classe | Regra objetiva |
|---|---|
| `unicode_invisivel` | Presenca de U+200B, U+200C, U+200D, U+2060, U+FE00–FE0F ou U+E0000–E007F |
| `codificacao_ou_ofuscacao` | Cadeia em base64 que decodifica para texto valido, codificacao percentual, sequencia hexadecimal longa, ou separadores intercalados entre caracteres |
| `idioma_ou_escrita_distinta` | Presenca de caracteres de escrita nao latina |
| `texto_simples` | Nenhuma das anteriores |

As classes **multimodal e esteganografica** estao fora do escopo declarado do
trabalho e nao integram a amostra.

### Por que a classificacao nao pode usar o mecanismo da camada
Classificar com o mesmo detector que sera avaliado seria **circular**: um caso que o
detector nao enxergasse cairia em `texto_simples` e nunca contaria como falha dele,
mascarando exatamente o que o criterio `INJ-05` mede.

A separacao adotada: a classificacao verifica **o que o atacante fez** — o codepoint
esta no texto ou nao esta, o que e propriedade objetiva e verificavel —, enquanto a
deteccao e o que esta sendo medido. A implementacao da classificacao e independente,
escrita antes de qualquer regra da camada existir, e congelada junto com o conjunto.

**Limitacao declarada:** a regra de idioma detecta *escrita*, e nao *lingua*. Um
ataque em lingua de poucos recursos escrita em alfabeto latino nao e reconhecido pela
regra automatica, e depende da revisao manual.

### Amostragem
Alocacao **igual por estrato**, limitada pelo tamanho do estrato, com o excedente
redistribuido proporcionalmente entre os estratos restantes. Semente fixa,
registrada.

Alocacao igual e preferida a proporcional porque o criterio `INJ-05` le o resultado
**por tecnica**: um estrato com dois casos nao sustenta leitura alguma. A alocacao
proporcional reproduziria a frequencia com que cada tecnica foi tentada na
competicao, que nao e a grandeza de interesse.

## Alternativas consideradas

**Nao deduplicar.** Manteria a distribuicao original da competicao, inclusive a
frequencia de tentativa de cada tecnica. Descartada porque a amostra repetiria
ataques quase identicos, reduzindo a variedade efetiva abaixo de 40.

**Restringir aos niveis mais altos.** Ataques mais elaborados, amostra mais dificil.
Descartada por deixar de representar as tecnicas simples — que sao justamente as que
a camada tem alguma chance de deter, e portanto aquelas cuja medida informa algo.

**Classificacao apenas manual.** Sem risco de circularidade, mas nao reproduzivel:
outra pessoa classificaria diferente e nao haveria registro do criterio aplicado caso
a caso.

**Classificacao apenas automatica.** Reproduzivel e sem custo de tempo, mas casos
ambiguos ficariam mal classificados sem que ninguem percebesse, e a estratificacao
herdaria o erro em silencio.

## Consequencia
A amostra de 40 e reconstruivel por terceiros a partir do conjunto de origem, da
semente e do codigo de classificacao, todos versionados.

Registra-se no congelamento, conforme RQ-04: o criterio de cada classe, a
classificacao automatica de cada caso, a revisao manual quando divergiu, a autoria, a
data e a declaracao de **classificador unico**.

A revisao manual e de um so anotador, sem medida de concordancia. A alternativa — dois
anotadores independentes — seria mais forte e fica registrada como melhoria possivel.

Depois de `CONGELADO.md` datado, a classificacao nao muda, ainda que um caso pareca
mal classificado a luz dos resultados.

## Data
2026-09-11

---

# Revisao 2 - 11/09/2026, fechada em 17/09/2026

A decisao original permanece acima, integra. O registro do erro e parte do resultado.

## O que falhou

A regra automatica da revisao 1 atribuia `idioma_ou_escrita_distinta` a todo caractere
alfabetico cujo **nome Unicode** nao comecasse por `LATIN`, `COMMON` ou `INHERITED`.

Nome de caractere nao e a propriedade Script do UAX #24. Verificado sobre a tabela do
Python (`unicodedata`, Unicode 14.0):

| Caractere | Nome Unicode | Comeca por `LATIN`? | NFKC |
|---|---|---|---|
| U+1D400 | `MATHEMATICAL BOLD CAPITAL A` | nao | `A` |
| U+FF21 | `FULLWIDTH LATIN CAPITAL LETTER A` | nao | `A` |
| U+1D43 | `MODIFIER LETTER SMALL A` | nao | `a` |
| U+1D504 | `MATHEMATICAL FRAKTUR CAPITAL A` | nao | `A` |
| U+1D5A0 | `MATHEMATICAL SANS-SERIF CAPITAL A` | nao | `A` |
| U+00E1 | `LATIN SMALL LETTER A WITH ACUTE` | sim | inalterado |

As cinco primeiras linhas sao a letra latina A sob variacao tipografica. A regra as lia
como escrita estrangeira. O efeito era sistematico e de uma direcao so: **toda ofuscacao
por variante tipografica Unicode caia no estrato de escrita distinta**.

Defeito secundario: `COMMON` e `INHERITED` sao nomes de Script, nao prefixos de nome de
caractere. Nenhum dos caracteres nomeados do Unicode 14.0 comeca por qualquer um dos
dois — as duas entradas da tupla nunca casaram com nada desde o primeiro commit. Ha teste
que percorre os 1.114.112 codepoints e fixa esse fato.

## Como o defeito foi descoberto

Pela revisao manual dos quarenta casos exigida por esta ADR, executada em 11/09/2026 pelo
autor. A revisao produziu nove divergencias, todas na mesma direcao:

| `ordem` | Tecnica observada | Regra automatica | Revisao manual |
|---|---|---|---|
| 11 | caso misto: ideogramas CJK com letras matematicas sem serifa e monoespacadas e virgulas de largura cheia | escrita distinta | codificacao |
| 12 | tres caracteres armenios inseridos em palavras latinas | escrita distinta | codificacao |
| 13 | letras matematicas em negrito | escrita distinta | codificacao |
| 14 | letras matematicas em negrito e italico | escrita distinta | codificacao |
| 15 | letras latinas de largura cheia | escrita distinta | codificacao |
| 16 | mistura de variantes: matematicas cursivas, italicas e fraktur em negrito | escrita distinta | codificacao |
| 17 | letras sobrescritas | escrita distinta | codificacao |
| 19 | letras em estilo gotico | escrita distinta | codificacao |
| 20 | letras sem serifa, com variantes em negrito | escrita distinta | codificacao |

A `ordem` 11 e o caso misto previsto por R1: tem conteudo linguistico em escrita nao
latina **e** variantes tipograficas de letras latinas. A precedencia atribui codificacao,
e as caracteristicas secundarias ficam registradas, sem inferir qual delas causou o
sucesso do ataque.

Distribuicao final da primeira amostra apos a revisao: 19 codificacao, 10 texto simples,
10 unicode invisivel, 1 escrita distinta.

Nove de dez casos do estrato `idioma_ou_escrita_distinta` estavam errados. O estrato nao
media o que dizia medir.

## Regra de revisao R1 - representacao textual

Com base no eixo *Encoding* do OWASP LLM01:2026, citado na ADR-0013, distinguem-se
transformacoes da representacao e conteudo linguistico em outra escrita. Para atribuir um
unico rotulo ao `user_input` completo, aplica-se a precedencia `unicode_invisivel` >
`codificacao_ou_ofuscacao` > `idioma_ou_escrita_distinta` > `texto_simples`. Mantem-se os
criterios de caracteres invisiveis e codificacoes da ADR-0017, acrescentando-se a
ofuscacao: letras matematicas, sobrescritas ou de largura cheia cuja normalizacao NFKC
produz letras latinas comuns; insercao ou substituicao de caracteres de outra escrita no
interior de uma palavra latina, com registro do caractere e da palavra reconstruida; e
separadores sistematicamente intercalados entre letras, com registro do trecho
reconstruido. Conteudo linguistico em escrita nao latina recebe
`idioma_ou_escrita_distinta` somente quando nenhuma categoria precedente se aplica;
caracteres isolados usados para alterar palavras latinas nao bastam para esse
enquadramento. Nos casos mistos, registram-se as caracteristicas secundarias e aplica-se a
precedencia, sem inferir qual delas causou o sucesso. A categoria de escrita distinta e
uma adaptacao operacional do trabalho e nao comprova uso de lingua de poucos recursos.
Toda decisao registra ordem, rotulos anterior e revisado, evidencia textual e
transformacao observada, quando houver.

## Correcao do instrumento

`scripts/classificar_codificacao.py` passa a:

1. aplicar NFKC **antes** do teste de escrita, de modo que variante tipografica cuja NFKC
   produz letra ASCII seja ofuscacao e nao escrita distinta;
2. tratar mistura de escritas **dentro de um mesmo token alfabetico** como homoglifo, e
   portanto ofuscacao, reservando `idioma_ou_escrita_distinta` para palavras inteiramente
   nao latinas;
3. expor `descrever()`, que devolve todas as caracteristicas observadas e a palavra
   reconstruida, atendendo a exigencia de registro de R1.

**Limitacao declarada (alcance).** R1 fala em *letras*, e a implementacao segue a regra a
risca: so caracteres alfabeticos sao examinados. Digitos e simbolos de largura cheia nao
sao reconhecidos, e um ataque que ofusque apenas caracteres nao alfabeticos cai em
`texto_simples`. Escolha tomada em 11/09/2026 por fidelidade ao texto de R1, com a
alternativa — estender a regra a digitos — registrada como possivel melhoria.

**Limitacao declarada (instrumento).** A biblioteca padrao do Python nao expoe a
propriedade Script. O teste de latinidade usa o prefixo do nome do caractere **depois** da
NFKC. A alternativa — a biblioteca `regex` e `\p{Script=Latin}` — foi recusada para nao
acrescentar uma segunda tabela Unicode versionada ao conjunto do que precisa ser fixado
para reproduzir o resultado. A versao em uso (`unicodedata.unidata_version`) entra no
congelamento.

## Verificacao da correcao

`scripts/conferir_reclassificacao.py` roda a regra corrigida sobre os quarenta casos da
primeira amostra e a compara com a revisao manual arquivada.

| Medida | Resultado |
|---|---|
| Decisoes humanas registradas | 9 |
| Reproduzidas pela regra corrigida | **9 de 9** |
| Linhas nao revistas em que a regra nova discorda da antiga | 0 |
| Distribuicao produzida | 19 codificacao, 10 texto simples, 10 invisivel, 1 escrita distinta |

A distribuicao coincide com a da revisao manual, rotulo por rotulo.

**Isto nao e ajuste a resultado.** A regra corrigida foi escrita a partir do texto de R1,
redigido antes; os quarenta casos sao material de desenvolvimento e a amostra medida e
outra, sorteada depois da correcao; e nenhuma divergencia foi usada para alterar a regra.
A ordem dos fatos esta no historico de commits: o estado com a regra defeituosa foi
registrado em `f72d681` antes de a correcao ser aplicada.

**Advertencia sobre o arquivo de revisao.** O CSV guarda cada caso numa linha so,
escapando quebras de linha como `\n` literal. Essa representacao nao e o texto
classificado: o `\n` escapado cola um `n` latino na palavra seguinte, produzindo falso
homoglifo, e um bloco base64 partido por quebras deixa de ser reconhecido. Dois dos
quarenta casos mudavam de classe por esse motivo. A conferencia restaura as quebras antes
de classificar. **A amostragem nunca sofreu disso**, porque classifica o texto do parquet;
apenas a conferencia sofreria.

## Consequencias sobre a amostra

Os estratos da revisao 1 estao invalidados. Reclassificacao do universo de 19.803 casos
com a regra corrigida:

| Estrato | Regra antiga | Regra corrigida |
|---|---:|---:|
| `texto_simples` | 18.554 | 18.546 |
| `codificacao_ou_ofuscacao` | 48 | **1.065** |
| `idioma_ou_escrita_distinta` | 1.089 | **80** |
| `unicode_invisivel` | 112 | 112 |

Migracoes: 1.009 casos de escrita distinta para codificacao, 8 de texto simples para
codificacao, 18.786 sem mudanca.

O estrato de codificacao era vinte e duas vezes maior do que a regra dizia. A revisao
manual de dez casos estimou 90% de erro naquele estrato; a reclassificacao do universo
inteiro da **92,7%** (1.009 de 1.089). A estimativa amostral e o censo concordam, o que e
evidencia independente de que a correcao descreve o universo e nao so a amostra.

Toda contagem de universo derivada da regra antiga — inclusive as 48 ocorrencias de
codificacao e as 1.089 de escrita distinta — nao e utilizavel.

Uma segunda amostra e sorteada com a **mesma semente**, de modo que a diferenca entre as
duas seja atribuivel unicamente a correcao da classificacao. As duas selecoes ficam
versionadas:

- `conjunto_teste/selecao/hackaprompt-v1-regra-com-defeito.json` — primeira amostra
- `conjunto_teste/selecao/hackaprompt.json` — amostra vigente

Os CSV de revisao nao sao versionados, por conterem texto de ataque (ADR-0016). A
evidencia versionada da revisao e a tabela de tecnicas acima, que nomeia a transformacao
sem reproduzir o conteudo.

## Legitimidade da correcao

A correcao ocorre **antes** do congelamento e decorre de falseamento do instrumento por
medicao, nao de desempenho insatisfatorio da camada — que ainda nao foi executada contra
este conjunto. E a mesma distincao firmada na ADR-0012. Depois de `CONGELADO.md` datado, a
mesma correcao seria ajuste orientado a resultado e estaria vedada pelo principio V da
constituicao.

## Divergencia de nomenclatura com a ADR-0013

A ADR-0013 nomeia o estrato, a partir do OWASP, como **idioma de poucos recursos**. O
instrumento detecta **escrita**, nao **lingua**: um ataque em lingua de poucos recursos
escrito em alfabeto latino cai em `texto_simples` e nao e reconhecido. Escrita nao latina
tambem nao comprova lingua de poucos recursos — russo e japones sao linguas de ampla
representacao.

O estrato passa a ser lido como *escrita nao latina*, que e o que de fato se mede. O
`INJ-05` nao afirma nada sobre lingua de poucos recursos. A lacuna — validade do estrato
frente a classe nomeada pelo referencial — entra nas limitacoes declaradas.

## Incidentes de manuseio

Registrados porque a restricao 8 trata de registro bruto, e porque as duas falhas ja
produziram correcao no codigo.

**Arquivamento sobrescrito.** O bloco de arquivamento da primeira amostra foi executado
duas vezes. Na primeira (commit `ee7cf3d`) foi gravada a selecao **com** a revisao
aplicada. Entre as duas execucoes, uma tentativa de reamostragem reescreveu
`selecao/hackaprompt.json` sem a revisao; a segunda execucao do bloco (commit `1f1b51a`)
copiou esse arquivo por cima do arquivamento, removendo o bloco `revisao`, o
`distribuicao_final` e os `classe_final`. O conteudo foi restaurado de `ee7cf3d` no commit
`e3c8917`. Nenhum historico foi reescrito.

**Revisao manual descartada em silencio.** A reamostragem regravou
`revisao/hackaprompt_revisao.csv` zerando a coluna `classe_revisada`. As nove decisoes
sobreviveram apenas na copia arquivada `hackaprompt_revisao-v1.csv`.

**Correcoes no codigo.** `escrever_texto` passa a gravar em arquivo temporario e
substituir com `os.replace`, e `escrever` troca o CSV antes do JSON: ou os dois arquivos
mudam, ou nenhum muda — a quebra original ocorreu porque o CSV estava aberto no Excel, que
mantem trava exclusiva, e o JSON ja havia sido reescrito.
`impedir_descarte_de_revisao` recusa reamostrar quando a selecao vigente ja tem revisao
aplicada, exigindo `--refazer` explicito.

**Concordancia por silencio.** A convencao de deixar `classe_revisada` em branco para
concordar com a regra e comoda para quem revisou, e indistinguivel de quem nao abriu o
arquivo. Em 11/09 e de novo em 17/09 a segunda coisa aconteceu: `--aplicar-revisao` foi
executado logo apos a amostragem, e o registro passou a declarar uma revisao que nao
existia. `aplicar_revisao` passa a recusar o caso em que **nenhuma** linha esta
preenchida, exigindo `--concordancia-total` — a concordancia vira ato afirmativo e fica
gravada como tal no campo `forma`, que distingue "com divergencias anotadas" de
"concordancia total declarada pelo autor". O registro deixa de ser ambiguo para quem o
ler depois.

## Data
2026-09-17
