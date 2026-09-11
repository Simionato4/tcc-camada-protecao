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
