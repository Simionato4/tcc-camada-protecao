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

---

# Revisao 3 - 17/09/2026

## O que falhou

`tem_variante_tipografica` filtrava a entrada com `caractere.isalpha()`. Letras circuladas
sao categoria `So` — simbolo, nao letra — e nunca chegavam ao teste, embora a NFKC produza
a letra latina correspondente.

O filtro era acrescimo da implementacao. R1 diz "letras matematicas, sobrescritas ou de
largura cheia **cuja normalizacao NFKC produz letras latinas comuns**": o criterio e sobre
o que a normalizacao **produz**, nao sobre a categoria Unicode da entrada.

E a mesma falha da revisao 2 em outro lugar do mesmo modulo: tecnicalidade Unicode usada
como substituto de nocao semantica. Primeiro nome de caractere no lugar da propriedade
Script; depois categoria geral no lugar de "letra". O padrao fica registrado porque e ele,
e nao cada defeito isolado, que explica como os dois passaram.

## Como o defeito foi descoberto

Pela revisao manual dos quarenta casos da segunda amostra, executada em 17/09/2026 pelo
autor, que produziu tres divergencias:

| `ordem` | Evidencia textual | Regra automatica | Revisao manual |
|---|---|---|---|
| 19 | cinco letras latinas circuladas (`So`) mais `е` cirilico | escrita distinta | codificacao |
| 20 | as mesmas circuladas, mais oito sinais de paragrafo | escrita distinta | codificacao |
| 14 | cinco maiusculas cirilicas formando uma unica palavra, tres delas sosias de letras latinas | escrita distinta | codificacao |

As tres escrevem a palavra-alvo da competicao com sosias. Duas causas mecanicas distintas:
as ordens 19 e 20 pelo filtro de categoria; a ordem 14 por substituicao total.

Distribuicao final da segunda amostra apos a revisao: 13 codificacao, 10 texto simples,
10 unicode invisivel, 7 escrita distinta.

## Correcao

`reduz_a_ascii` passa a exigir que a NFKC altere o caractere **e** produza **exatamente
uma letra ASCII**, e `tem_variante_tipografica` deixa de filtrar a entrada por categoria.

Tres exclusoes resultam do criterio, e nao de excecao escrita a parte:

| Entrada | NFKC | Decisao | Motivo |
|---|---|---|---|
| `á` | inalterado | nao e variante | nao ha transformacao a detectar |
| `１` | `1` | nao e variante | R1 fala em letras; digito nao e letra (decisao de 11/09, mantida) |
| `™` | `TM` | nao e variante | duas letras: expansao de simbolo em palavra, nao substituicao de uma letra |
| `Ⓟ` | `P` | **e variante** | uma letra ASCII |

## Limitacao declarada: homoglifo de palavra inteira

Quando **todas** as letras de uma palavra latina sao trocadas por sosias de outra escrita,
nao sobra caractere latino no token e `tem_homoglifo` nao enxerga mistura alguma: a palavra
cai em `idioma_ou_escrita_distinta`. E o caso da `ordem` 14.

Detectar isso exige a tabela de confundiveis do UTS #39, que a biblioteca padrao nao expoe.
Adota-la acrescentaria uma segunda tabela Unicode versionada ao conjunto do que precisa ser
fixado para reproduzir o resultado — o mesmo custo que levou a recusar a biblioteca `regex`
na revisao 2. Recusada pelo mesmo motivo, e registrada como trabalho futuro.

Consequencia assumida: o estrato `idioma_ou_escrita_distinta` contem um numero desconhecido,
e pequeno, de homoglifos de palavra inteira. A revisao manual os corrige na amostra; o
tamanho do estrato no universo segue com esse vies.

## Verificacao

`scripts/conferir_reclassificacao.py` sobre as duas amostras ja revistas:

| Amostra | Decisoes humanas | Reproduzidas pela regra da revisao 3 |
|---|---:|---|
| Primeira (11/09) | 9 | **9 de 9** |
| Segunda (17/09) | 3 | **2 de 3** |

A unica divergencia restante e a `ordem` 14 — exatamente a limitacao declarada acima, e
nao uma surpresa. A correcao da revisao 3 nao desfez nenhum resultado da revisao 2.

## Livro de rotulos

Ate aqui, cada decisao humana de classificacao vivia no CSV de revisao, que a execucao
seguinte sobrescrevia. Entre 11 e 17/09 isso destruiu ou ameacou decisoes tres vezes.

`conjunto_teste/selecao/rotulos.json` passa a guardar cada decisao indexada pelo **sha256
do `user_input`**, com classe, data e autor. O arquivo e versionado: contem hashes e
classes, nunca texto de ataque (ADR-0016).

A justificativa e metodologica, e nao de conveniencia: uma decisao de classificacao e sobre
**o texto**, nao sobre o sorteio em que ele apareceu. Quando a regra muda e o universo e
reclassificado, os casos que reaparecem trazem o rotulo que o autor ja lhes deu, com a data
original preservada, e apenas os ineditos precisam de revisao. A precedencia na
classificacao final e: decisao desta rodada, depois decisao anterior do livro, depois regra
automatica.

O livro e semeado com as 71 decisoes distintas ja tomadas — 40 da primeira amostra e 40 da
segunda, com nove textos em comum.

A guarda de `--aplicar-revisao` passa a exigir `--concordancia-total` apenas quando existem
casos **ineditos** e nenhum foi anotado. Caso ja decidido antes nao precisa de nova
declaracao.

## Consequencias sobre a amostra

O universo e reclassificado com a regra da revisao 3 e uma terceira amostra e sorteada, com
a mesma semente. As selecoes anteriores permanecem versionadas. A revisao manual recai
somente sobre os casos sem rotulo no livro.

## Data
2026-09-17

---

# Exame das divergencias da terceira amostra — 07/10/2026

Fecha o exame exigido pela propria ADR: *"Cada uma exige exame registrado: o erro esta
em R1 ou na implementacao?"*

## Um terceiro lugar de erro

Ate aqui o projeto considerava dois lugares possiveis para uma divergencia entre a regra
automatica e a revisao manual:

1. **erro em R1** — a regra escrita esta errada;
2. **erro na implementacao** — o codigo nao implementa o que R1 diz.

As revisoes 2 e 3 foram, as duas, do segundo tipo. A terceira amostra revelou um terceiro:

3. **erro na aplicacao de R1 pelo revisor** — R1 esta correta, a implementacao esta
   correta, e o rotulo esta errado.

O registro deste terceiro caso importa porque a ferramenta nao o detecta. Divergencia dos
tipos 1 e 2 aparece como defeito reproduzivel; a do tipo 3 aparece como divergencia
legitima e, se nao for examinada, entra no congelamento como se fosse achado.

## As seis divergencias

| `ordem` | de → para | Evidencia observada | Veredicto |
|---|---|---|---|
| 11 | escrita distinta → codificacao | quatro palavras inteiras em cirilico | **mantida** — homoglifo de palavra inteira, limitacao declarada na rev. 3 |
| 13 | escrita distinta → codificacao | uma palavra inteira em cirilico | **mantida** — mesma limitacao |
| 18 | escrita distinta → codificacao | sete tokens invertidos, entre eles a palavra-alvo da competicao escrita de tras para frente | **mantida** — tecnica real que a regra nao detecta; ver "Texto invertido" abaixo |
| 22 | texto simples → codificacao | 100% ASCII; NFKC nao altera; sem codificacao, invisivel, variante tipografica, homoglifo ou inversao | **revertida para `texto_simples`** |
| 28 | texto simples → codificacao | idem | **revertida para `texto_simples`** |
| 30 | texto simples → codificacao | idem | **revertida para `texto_simples`** |

Distribuicao final da terceira amostra apos o exame, verificada por execucao:
**13** codificacao, **10** texto simples, **10** unicode invisivel, **7** escrita nao
latina, com 3 divergencias da regra automatica.

## Determinacao do autor sobre as ordens 22, 28 e 30

Transcrita como registrada:

> Na revisao das ordens 22, 28 e 30 da terceira amostra, a anotacao assistida por IA
> ampliou indevidamente o criterio operacional: tratou fragmentacao parcial por espacos e
> substituicao explicita entre caracteres ASCII como ofuscacao, sem regra previamente
> documentada para essas operacoes. Reexaminados sob R1, os tres casos retornam a
> `texto_simples`. Eventual inclusao dessas operacoes exigira definicao explicita e
> aplicacao uniforme, nao constituindo correcao do classificador sob a regra atual.

A distincao que sustenta a reversao: R1 trata do eixo *Encoding* do OWASP LLM01:2026 —
**"how the malicious instructions are represented in tokens or pixels"**. Um ataque pode
ser engenhoso sem que a representacao do texto tenha sido transformada. Dramatizacao,
troca de papel e instrucao disfarcada em prosa sao `texto_simples` sob R1, por mais eficaz
que o ataque seja.

E o ponto metodologico que a determinacao fixa: acrescentar fragmentacao parcial e
substituicao ASCII→ASCII a regra **depois** de ver tres casos seria ajuste orientado ao
caso. Se forem incluidas, sera por definicao escrita antes, aplicada ao universo inteiro e
com nova amostragem — nao por remendo que acomode tres rotulos.

## Limitacoes declaradas do classificador, consolidadas

Tres fronteiras, todas conhecidas e nenhuma silenciada:

| Operacao nao detectada | Por que fica fora |
|---|---|
| Homoglifo de **palavra inteira** (todas as letras substituidas por sosias de outra escrita) | exige a tabela de confundiveis do UTS #39; seria uma segunda tabela Unicode versionada a congelar (rev. 3) |
| **Texto invertido** | tecnica identificada em 07/10/2026; decisao de incluir ou declarar pendente, condicionada a medicao |
| **Fragmentacao parcial por espacos** e **substituicao ASCII→ASCII** | ausentes de R1; incluir exigiria definicao explicita e reaplicacao ao universo (determinacao de 07/10/2026) |

O `INJ-05` nao afirma deteccao sobre nenhuma dessas tres operacoes, e o estrato
`texto_simples` deve ser lido como *"ataques cuja transformacao de representacao a regra
nao reconheceu"*, e nao como *"ataques sem transformacao de representacao"*.

## Correcao de registro: o commit `a5f5c64`

O commit `a5f5c64`, de 07/10/2026, tem a mensagem *"exame das divergencias da terceira
amostra: tres rotulos revertidos por aplicacao indevida de R1"* e **nao reverte rotulo
algum**. Verificado por `git show a5f5c64 --stat`:

```
 conjunto_teste/selecao/hackaprompt.json | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

A unica alteracao foi o campo `data` do bloco de revisao, de `2026-09-17` para
`2026-10-07` — efeito de executar `--aplicar-revisao` sem nenhuma alteracao no CSV. A
edicao manual das tres celulas, feita em planilha, nao havia persistido, e o indicio
estava na propria saida: 6 divergencias e distribuicao 16/7/7/10, identicas as de antes.

A reversao efetiva ocorreu no commit seguinte. **O historico nao foi reescrito**: a
mensagem incorreta permanece, com esta correcao apontando para ela, pelo mesmo
procedimento adotado quando o arquivamento da primeira amostra foi sobrescrito e
restaurado em `e3c8917`.

Terceira ocorrencia do mesmo padrao neste projeto — registro afirmando o que nao
aconteceu, por um passo manual que falhou em silencio. As duas primeiras foram revisoes
declaradas sem ter ocorrido, e geraram a guarda de `--concordancia-total`. Esta gerou
`scripts/anotar_revisao.py`, que grava `classe_revisada` de forma atomica, validando a
classe e imprimindo antes e depois de cada alteracao, retirando a planilha do caminho para
correcoes pontuais. O julgamento continua humano; o passo que falhava era o de
transcricao.

## Correcao dos rotulos revertidos

A reversao foi aplicada pelo mesmo caminho da revisao — `classe_revisada` no CSV e
`--aplicar-revisao` —, de modo que o livro de rotulos `conjunto_teste/selecao/rotulos.json`
se corrigiu e passou a registrar a classe correta com a data da reversao. Isso importava:
os tres rotulos errados ja estavam no livro e seriam reaplicados em qualquer sorteio
futuro. O livro preserva decisao boa e propaga decisao errada com a mesma eficiencia.

A `classe_revisada` dos tres casos recebeu `texto_simples` explicitamente, em vez de ser
apagada. Deixar em branco produziria o mesmo rotulo final, mas apagaria o registro de que
houve decisao humana naquelas linhas — e distinguir "revisado e concordo" de "nao
revisado" e justamente o que a guarda de `--concordancia-total` existe para preservar.

## Anotacao assistida por IA

A determinacao do autor registra que a anotacao da terceira rodada foi assistida por IA. O
campo `classificador` do registro de revisao passa a declarar isso:

> `"autor, com anotacao assistida por IA e decisao final humana; classificador unico, sem
> medida de concordancia"`

A assistencia nao constitui segundo anotador independente, e portanto nao ha medida de
concordancia a reportar. Mas o processo de anotacao deixava de ser descrito corretamente
por "autor (classificador unico)" sozinho.

Os tres rotulos ampliados indevidamente e revertidos pelo reexame sao a evidencia concreta
de que a revisao manual exerce controle sobre a anotacao assistida, e nao o contrario.
Declarar a assistencia junto com o caso em que ela falhou e foi corrigida fortalece o
registro em vez de enfraquece-lo.

O campo `autor` do livro de rotulos permanece uniforme, deliberadamente. Altera-lo agora
marcaria apenas os rotulos cuja classe mudou, e a diferenca passaria a significar "foi
reescrito depois de 07/10" em vez de "foi anotado com assistencia" — um registro pior que
o atual. A descricao do processo pertence ao campo `classificador` de cada rodada e a esta
ADR.

**Pendencia declarada:** as rodadas de revisao de 11/09/2026 (primeira amostra, 9
divergencias) e 17/09/2026 (segunda amostra, 3 divergencias) ainda nao tiveram a forma de
anotacao declarada. O RQ-04 exige autoria registrada, e a declaracao precisa cobrir as
tres rodadas antes do congelamento.

## Texto invertido — decisao pendente

A `ordem` 18 e tecnica real e mecanicamente detectavel. Antes de decidir entre corrigir o
classificador numa quarta rodada ou declarar a limitacao, mede-se quantos casos do
universo apresentam inversao. Decidir sem o numero seria escolher pelo esforco, e nao pelo
efeito sobre a estratificacao.

## Data
2026-10-07

---

# Correcao de registro - 08/10/2026

## Versao da tabela Unicode

A revisao 2 desta ADR afirma "Unicode 14.0", e a docstring de
`scripts/classificar_codificacao.py` afirmava "nenhum dos 149.186 caracteres nomeados do
Unicode 14.0". **Os dois numeros estao errados para o ambiente do experimento.**

Medido na maquina do experimento em 08/10/2026:

| Item | Valor |
|---|---|
| Python | 3.13.2 |
| `unicodedata.unidata_version` | **15.1.0** |
| Caracteres nomeados (`unicodedata.name` definido em 0x000000-0x10FFFF) | **143.668** |

Procedencia do erro: os dois valores foram registrados pelo assistente de IA a partir de
um ambiente com outra versao de Python, e transpostos para ca como se fossem do ambiente
do trabalho. E o mesmo tipo de falha que a ADR-0011 registra para o `fastembed`: medicao
vale para a combinacao em que foi feita, e nao se generaliza.

O que foi verificado sob Unicode 15.1.0, na maquina do experimento, em 08/10/2026:

| Verificacao | Resultado |
|---|---|
| `python -m pytest -q --import-mode=importlib`, incluindo o teste que percorre os 1.114.112 codepoints | 129 passed, 4 deselected |
| `conferir_reclassificacao.py` sobre a revisao da primeira amostra (`hackaprompt_revisao-v1.csv`) | 9 de 9 decisoes humanas reproduzidas; distribuicao 19/10/10/1 |
| `conferir_reclassificacao.py` sobre a revisao da segunda amostra (`hackaprompt_revisao-v2.csv`) | 2 de 3; a divergencia restante e a `ordem` 14, limitacao declarada na revisao 3 |

Os resultados coincidem com os registrados nas revisoes 2 e 3. Nao se afirma aqui que o
comportamento do classificador seja identico em todas as versoes do Unicode: afirma-se
que, na versao do experimento, as decisoes ja revisadas sao reproduzidas. A docstring foi
corrigida no mesmo commit desta secao, e a versao da tabela foi registrada em
`docs/versoes.md`, porque `unidata_version` entra no congelamento.

## Nomenclatura das rodadas de revisao

A pendencia declarada no exame de 07/10/2026 falava em "rodadas de 11/09/2026 e
17/09/2026". A redacao era ambigua: em 17/09 houve **duas** revisoes. As rodadas passam a
ser nomeadas pela amostra, e nao pela data.

| Rodada | Amostra | Decisao | Commits | Forma de anotacao |
|---|---|---|---|---|
| 1a | primeira amostra, 9 divergencias | 11/09/2026 | `ee7cf3d`, restaurado em `e3c8917` | **nao declarada** |
| 2a | segunda amostra, 3 divergencias | 17/09/2026 | `338efc6` | **nao declarada** |
| 3a | terceira amostra, 6 divergencias | 17/09/2026, reexaminada em 07/10/2026 | `afc3791`, `d6295d1` | declarada: assistida por IA, decisao final humana |

Os arquivos arquivados `hackaprompt-v1-regra-com-defeito.json` e
`hackaprompt-v2-regra-rev2.json` carregam o campo `classificador` anterior a declaracao.
**Sao evidencia e nao sao editados.** A forma de anotacao da primeira e da segunda
amostras sera declarada neste texto, e nao nos arquivos arquivados.

**Pendencia mantida:** a forma de anotacao da primeira e da segunda amostras segue nao
declarada. O RQ-04 exige autoria registrada das tres rodadas antes do congelamento.

## Data
2026-10-08

---

# Texto invertido - criterio e regra de decisao, fixados antes da medicao - 08/10/2026

Fecha o desenho da pendencia aberta no exame de 07/10/2026. Este bloco e
`scripts/medir_inversao.py` sao commitados **antes** da primeira execucao do script: a
ordem fica no historico, e nenhum numero foi visto quando o criterio e o limiar foram
escritos.

## Criterio (opcao estreita, escolhida pelo autor em 08/10/2026)

Para cada caso do universo, o alvo e o `expected_completion` **do proprio caso**, lido do
conjunto e nao de memoria. Texto e alvo passam por NFKC e `casefold`, e sao divididos em
palavras pela mesma definicao de palavra de R1 (corrida maxima de caracteres alfabeticos).

Um caso tem inversao quando ocorre ao menos um dos dois mecanismos:

| Mecanismo | Definicao |
|---|---|
| palavra | uma palavra do alvo com 4 letras ou mais, que nao seja palindromo, aparece escrita de tras para frente como palavra inteira do texto, e a forma invertida nao e ela propria palavra do alvo |
| frase | o alvo inteiro, so letras, com 8 letras ou mais e que nao seja palindromo, aparece invertido como trecho contiguo das letras do texto, ignorando espacos e pontuacao |

Caso sem `expected_completion` nao e avaliado, e a quantidade e informada.

**O numero e limite inferior.** Inversao de palavras que nao pertencem ao alvo nao e
medida.

**Alternativa recusada: criterio amplo**, com qualquer palavra que invertida forme
palavra de um lexico. Exigiria uma lista de palavras de terceiros, versionada e
congelada junto, o mesmo custo que levou a recusar a biblioteca `regex` (rev. 2) e a
tabela UTS #39 (rev. 3). A decisao entre quarta rodada e limitacao depende de ordem de
grandeza, e um limite inferior a responde.

## Controle positivo

A `ordem` 18 da terceira amostra (sha256 `fdfda262...323996`) e o caso em que a tecnica
foi observada. O script verifica que o criterio a detecta **antes** de contar. Se nao
detectar, o script para sem produzir contagem, e o criterio e revisto sem que numero
algum tenha sido visto.

O script tambem para se o universo ou os estratos recalculados divergirem dos
registrados na selecao vigente (`hackaprompt.json`): a regra abaixo foi escrita para
aqueles denominadores.

## Regra de decisao (aceita pelo autor em 08/10/2026)

Se a inversao passasse a contar como transformacao de representacao, um caso so mudaria
de estrato se hoje estiver em `texto_simples` ou em `idioma_ou_escrita_distinta`. Pela
precedencia de R1, caso em `unicode_invisivel` continua ali, e caso em
`codificacao_ou_ofuscacao` ja esta no destino. Por isso a regra de 5% e aplicada ao que
**mudaria**:

| Gatilho | Contagem | Limiar (5%, arredondado para cima) |
|---|---|---|
| saida de `texto_simples` | casos com inversao no estrato | 922 de 18.439 |
| saida de `idioma_ou_escrita_distinta` | casos com inversao no estrato | 4 de 67 |
| entrada em `codificacao_ou_ofuscacao` | soma das duas saidas | 60 de 1.185 |

Qualquer gatilho atingido: **quarta rodada**, com a inversao incorporada a R1 por esta
definicao escrita, aplicada ao universo inteiro, nova amostragem com a mesma semente e
revisao manual apenas dos casos ineditos no livro de rotulos. Nenhum gatilho atingido:
**limitacao declarada**, como "pelo menos N casos com a frase-alvo invertida", na tabela
de limitacoes consolidadas do exame de 07/10/2026.

Sensibilidade declarada antes da medicao: o estrato de escrita nao latina e pequeno, e
quatro casos bastam para acionar a quarta rodada.

## Data
2026-10-08

---

# Texto invertido - resultado da medicao - 08/10/2026

Executado `python scripts/medir_inversao.py` na maquina do experimento, depois do commit
`3bdabcc`, que fixou criterio e regra. Saida transcrita sem edicao:

```
controle positivo (ordem 18): detectado por ['frase', 'palavra']
universo: 19,803 casos; sem expected_completion: 0

estrato                            N  com inversao       %  limiar
texto_simples                 18,439            44    0.24     922
codificacao_ou_ofuscacao       1,185            13    1.10      60
unicode_invisivel                112             0    0.00       6
idioma_ou_escrita_distinta        67             4    5.97       4

por mecanismo: so palavra 22; so frase 5; ambos 34

casos que migrariam para codificacao_ou_ofuscacao: 48
regra da ADR-0017 aponta: QUARTA RODADA
  - saida de idioma_ou_escrita_distinta: 4 >= 4
Nenhum arquivo gravado.
```

## Leitura

- A regra fixada antes da medicao aponta **quarta rodada**, por um unico gatilho, atingido
  no limite exato: 4 casos contra limiar de 4 no estrato de escrita nao latina. Os outros
  dois gatilhos ficaram longe (44 de 922; 48 de 60).
- **Um dos 4 casos e a propria `ordem` 18**, o controle positivo: ela e detectada pelo
  criterio e a regra automatica da revisao 3 a classifica como `idioma_ou_escrita_distinta`.
  Sem ela, o estrato teria 3 casos e a regra apontaria limitacao. O caso pertence ao
  universo e conta como qualquer outro; a regra nao e alterada depois de vista a
  contagem. O fato fica registrado porque o resultado depende dele.
- A sensibilidade do estrato pequeno foi declarada antes da medicao, no bloco anterior.
- Os 13 casos com inversao ja classificados como codificacao nao mudam de estrato.

## Previsao verificavel para a quarta rodada

Se a inversao for incorporada a R1 exatamente por este criterio, os estratos do universo
passam a ser, por aritmetica sobre a saida acima:

| Estrato | Revisao 3 | Revisao 4 prevista |
|---|---:|---:|
| `texto_simples` | 18.439 | 18.395 |
| `codificacao_ou_ofuscacao` | 1.185 | 1.233 |
| `unicode_invisivel` | 112 | 112 |
| `idioma_ou_escrita_distinta` | 67 | 63 |

Qualquer diferenca entre estes valores e os que a implementacao produzir indica que a
implementacao nao corresponde ao criterio medido.

## Data
2026-10-08

---

# Revisao 4 - texto invertido incorporado a R1 - 08/10/2026

Decorre da regra de decisao fixada em `3bdabcc` e aplicada em `81b6be9`.

## Extensao de R1

Acrescenta-se as transformacoes de representacao de R1, com a definicao commitada antes da
medicao: **texto invertido**, quando uma palavra do alvo com 4 letras ou mais, nao
palindromo, aparece escrita de tras para frente como palavra inteira do texto, ou quando o
alvo inteiro, so letras, com 8 letras ou mais, aparece invertido como trecho contiguo das
letras do texto. Texto e alvo passam por NFKC e `casefold`. O alvo e o `expected_completion`
do proprio caso. A precedencia de R1 nao muda: a inversao e evidencia de
`codificacao_ou_ofuscacao`, abaixo de `unicode_invisivel`.

## Implementacao

`scripts/classificar_codificacao.py` ganha `mecanismos_de_inversao(texto, alvo)`, e
`classificar`, `tem_ofuscacao` e `descrever` passam a aceitar `alvo` opcional.
`scripts/amostrar_hackaprompt.py` passa o `expected_completion` de cada caso.

`scripts/medir_inversao.py` **nao e alterado**: e o instrumento da medicao registrada e
fica como estava em `3bdabcc`. Para que o que classifica seja o que foi medido, um teste
confere que as duas implementacoes devolvem o mesmo resultado sobre os casos de teste; a
verificacao sobre o universo e a previsao de estratos abaixo.

Sem `alvo`, o classificador devolve exatamente o resultado da revisao 3. Por isso as
conferencias das amostras anteriores (`conferir_reclassificacao.py`, que le CSV sem
frase-alvo) nao mudam.

**Limitacao declarada.** O criterio e especifico de conjunto com frase-alvo conhecida, e e
limite inferior: inversao de palavras fora do alvo nao e reconhecida.

## Verificacao exigida antes da reamostragem

`python scripts/amostrar_hackaprompt.py --apenas-estratos` deve produzir os estratos
previstos no bloco de resultado: **18.395** texto simples, **1.233** codificacao, **112**
invisivel, **63** escrita nao latina. Divergencia interrompe a rodada.

## Forma de anotacao da quarta rodada, declarada antes da revisao

Assistida por IA, com decisao final humana, nos termos abaixo, que incorporam a falha da
terceira rodada:

1. A IA examina cada caso inedito por evidencia de nivel de caractere (nomes Unicode,
   contagens, palavra reconstruida), sem reproduzir o texto, e propoe uma classe
   **citando a clausula de R1 que se aplica**. Sem clausula citavel, a proposta e a classe
   da regra automatica.
2. A IA nao propoe operacao ausente de R1. Foi o que produziu as tres reversoes da
   terceira rodada (fragmentacao parcial e substituicao ASCII para ASCII).
3. O autor decide caso a caso. As divergencias sao gravadas por
   `scripts/anotar_revisao.py`, e nao por planilha.
4. O campo `classificador` da rodada declara essa forma.

## Data
2026-10-08
