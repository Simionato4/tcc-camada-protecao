# ADR-0015 - Corpus de dados pessoais: 350 positivos mais negativos dificeis

## Contexto
A proposta aprovada declara 350 ocorrencias sinteticas de documentos pessoais
brasileiros, usadas para medir precisao e revocacao do mascaramento.

A revisao externa de 10/09/2026 observou que o corpus, como desenhado, so continha
positivos. Sem negativos, **a precisao e quase nao informativa**: um detector que
marcasse toda sequencia numerica obteria revocacao alta e precisao aparentemente boa,
e so os negativos o denunciariam. O requisito ficou registrado como RQ-02.

## Decisao

O corpus tem **duas contagens declaradas**, e nao uma:

| Parte | Papel na metrica |
|---|---|
| **350 ocorrencias validas** | Positivos. Numero preservado da proposta aprovada |
| **Negativos dificeis** | Sequencias que um detector ingenuo marcaria, e que nao sao documento valido |

Preservar o 350 importa: e numero que consta na proposta aprovada, e altera-lo
exigiria declarar mudanca de escopo por uma razao que nao e de escopo.

### Classes de negativo dificil

| Classe | Por que e dificil |
|---|---|
| Digito verificador invalido | Tem o formato exato de um documento, e so a validacao o distingue |
| Sequencia de mesmo comprimento | Codigo de rastreio, numero de nota, identificador interno |
| Formato parcial | Documento truncado ou incompleto |
| Repeticao trivial | Sequencias como onze digitos iguais, que alguns validadores aceitam por engano |
| Numero em contexto nao pessoal | Valor monetario, CEP, data com pontuacao semelhante |

A classe de **digito verificador invalido** e a que mais importa, e e a razao de a
camada usar validacao de digito e nao apenas correspondencia por padrao. Ela mede
exatamente a diferenca entre as duas abordagens comparadas.

### Natureza de cada ocorrencia
Cada item registra `natureza`, distinguindo `pessoa_natural` de `pessoa_juridica`.
CNPJ identifica pessoa juridica e **nao e, por si, dado pessoal de pessoa natural**
(RQ-03): permanece no corpus como identificador estruturado brasileiro, com o recorte
declarado.

### Gabarito
Tipo, valor e **posicoes no texto original**, antes de qualquer normalizacao (RQ-07),
como ja e feito na base de conhecimento. Geracao com semente fixa e reproducao
verificavel por hash.

## Alternativa considerada
Manter 350 no total, com uma fracao de negativos. Descartada porque reduziria os
positivos e alteraria um numero que consta na proposta aprovada, exigindo declaracao
de mudanca por uma razao que nao e de escopo.

## Consequencia
As metricas do eixo de dados pessoais passam a ter significado:

- **revocacao** medida sobre os 350 positivos;
- **precisao** medida sobre positivos e negativos em conjunto, de modo que marcar um
  negativo dificil **custa**;
- **degradacao por classe de negativo** reportavel, o que expoe onde cada abordagem
  falha.

Sem os negativos, a comparacao entre a camada e a ferramenta externa premiaria o
detector mais permissivo. Com eles, a validacao de digito verificador — que e o
mecanismo proprio da camada — pode ser avaliada pelo que ela realmente faz: separar
o que tem formato de documento do que e documento.

O corpus cresce, e com ele o tempo de geracao e de analise. Nao ha custo de credito:
o corpus e avaliado fora do fluxo do assistente (ADR-0003).

## Data
2026-09-11

---

## Revisao de 08/10/2026: tipos de documento, distribuicao e suporte ao CNPJ

### Tipos e distribuicao
A versao final da proposta localizada no Drive do autor (`propostatccgabriel`, 23/08/2026)
declara "350 ocorrencias sinteticas de documentos pessoais brasileiros, geradas com
semente fixa", sem tipos nem distribuicao. O autor nao sabe dizer qual das versoes de
22 e 23/08/2026 foi a submetida; nenhuma das lidas fixa a distribuicao.

O rascunho `metodologiav2.md` (14/08/2026), do proprio autor, fixa **50 ocorrencias para
cada um de 7 tipos**. Decisao do autor, 08/10/2026: **adotar essa distribuicao.** E a
unica escrita pelo autor, e e coerente com a justificativa da proposta final, que cita
como lacuna do Presidio cinco destes tipos.

| Tipo | Positivos | Natureza | Digito verificador |
|---|---:|---|---|
| CPF | 50 | `pessoa_natural` | sim |
| CNPJ | 50 | `pessoa_juridica` (RQ-03) | sim |
| Cartao Nacional de Saude (CNS) | 50 | `pessoa_natural` | sim |
| NIT / PIS | 50 | `pessoa_natural` | sim |
| Titulo de eleitor | 50 | `pessoa_natural` | sim |
| Telefone | 50 | `pessoa_natural` | nao |
| Endereco eletronico | 50 | `pessoa_natural` | nao |
| **Total** | **350** | | |

O RG fica fora, como no rascunho: nao tem digito verificador padronizado nacionalmente.

Duas consequencias para o desenho (tarefa 3.5), ainda abertas:
- telefone e endereco eletronico nao tem digito verificador, e a classe de negativo
  "digito verificador invalido" nao se aplica a eles; precisam de classes proprias;
- o rascunho dizia que todo o corpus seria gerado pelo Faker. Medido na maquina do
  experimento: o Faker 40.38.0 `pt_BR` oferece `cpf`, `cnpj` e `rg`, e nao CNS, PIS ou
  titulo. A `validate-docbr` 2.0.0 tem `generate` para os cinco documentos. A escolha do
  gerador fica para a 3.5, porque gerar e validar com a mesma biblioteca cria
  dependencia entre o gabarito e o detector avaliado.

### RQ-03: suporte ao CNPJ alfanumerico

| Campo | Registro |
|---|---|
| Claim | a `validate-docbr` 2.0.0 valida CNPJ numerico e alfanumerico pela regra publicada pela Receita Federal |
| Fonte 1 | Receita Federal, "Perguntas e respostas: CNPJ alfanumerico", pergunta 14 (calculo do DV) e 15 (validade dos numeros atuais): https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf |
| Fonte 2 | pagina da versao no PyPI: https://pypi.org/project/validate-docbr/2.0.0/ (lancada em 04/04/2026; "numerico e alfanumerico"; licenca MIT) |
| Fonte 3 | codigo da versao instalada, na maquina do experimento: conjunto de caracteres `A-Z` mais digitos, valor `ord(caractere) - 48` |
| Data da consulta | 2026-10-08 |
| O que a fonte oficial diz | inicio da atribuicao a partir de julho de 2026 (IN RFB 2.119/2022, alterada pela IN RFB 2.229/2024); cada caractere vale ASCII menos 48; modulo 11 com pesos de 5 a 2 e de 6 a 2; os numeros atuais continuam validos; exemplo `12.ABC.345/01DE-35` |
| Divergencia | **o documento nao diz o que ocorre quando o resto da divisao e 0 ou 1.** Nao se supoe a regra do CNPJ numerico |
| Decisao | suporte verificado por `scripts/tests/test_suporte_cnpj.py`, que implementa a regra publicada e confere a biblioteca contra ela no exemplo oficial, num CNPJ numerico e em 400 bases sorteadas com semente fixa, todas com resto 2 ou maior |
| Pendencia | regra para resto 0 ou 1: conferir no texto da IN RFB 2.229/2024 ou em nota tecnica oficial antes de o corpus incluir CNPJ com esses restos |
| Impacto | RQ-03 (verificacao por teste unitario); desenho dos formatos de CNPJ do corpus (tarefa 3.5) |

## Data da revisao
2026-10-08

---

## Revisao de 08/10/2026 (segundo bloco): gabarito independente da biblioteca

### Decisao (do autor, 08/10/2026)
Opcao A': cada positivo do corpus precisa ser aceito por **duas implementacoes
independentes** do digito verificador: a `validate-docbr` 2.0.0, que a camada usa, e
`scripts/dv_independente.py`, que nao importa a biblioteca e foi escrita a partir das
fontes abaixo. Motivo: gerar e conferir com a mesma biblioteca usada pelo detector
avaliado faria um erro dela entrar no gabarito e no detector ao mesmo tempo.

A opcao A original pedia implementacao "a partir da regra oficial". Para parte dos
documentos a regra oficial completa nao foi localizada; o nivel de cada fonte fica
declarado.

### Fontes por documento

| Documento | Fonte da implementacao independente | Nivel | Consulta |
|---|---|---|---|
| CPF | Receita Federal, Manual de Preenchimento da e-Financeira, Anexo II, `REGRA_VALIDA_CPF` (versao 2.0, dez/2025, p. 34, conforme pesquisa do autor; trecho conferido em captura de tela fornecida pelo autor; o site bloqueia acesso automatizado) | regra oficial | 2026-10-08 |
| CNPJ numerico | mesmo manual, `REGRA_VALIDA_CNPJ` | regra oficial | 2026-10-08 |
| CNPJ alfanumerico | Receita Federal, perguntas e respostas sobre o CNPJ alfanumerico, pergunta 14 | regra oficial, sem tratamento do resto 0 ou 1 | 2026-10-08 |
| PIS/NIT | ANS, "Algoritmos do Aplicativo de Carga", item 7 (`isDvPisPasepValido`), publicado em 06/04/2021: https://www.gov.br/ans/pt-br/centrais-de-conteudo/manuais-do-portal-operadoras/sib-manual-de-instalacao-historico-de-versao-e-outros-arquivos/manual/algoritmos-do-aplicativo-de-carga | documentacao tecnica oficial; a ANS nao e o orgao emissor | 2026-10-08 |
| CNS | ANS, mesma pagina, item 4 (`validaCns`, `validaCnsProv`); separacao por prefixo pela documentacao de integracao do e-SUS APS v2.1.1 | documentacao tecnica oficial | 2026-10-08 |
| Titulo de eleitor | estrutura: Resolucao TSE 23.659/2021, art. 36, paragrafo unico (8 + 2 + 2, modulo 11). Pesos e restos: OBMEP, "A Matematica nos Documentos: Titulo de Eleitor": https://clubes.obmep.org.br/blog/a-matematica-nos-documentos-titulo-de-eleitor/ | estrutura oficial; pesos e restos de fonte academica secundaria | 2026-10-08 |

Os exemplos publicados nas fontes sao reproduzidos pela implementacao independente:
CPF `280012389-38` e CNPJ `18781203/0001-28` (e-Financeira), CNPJ `12.ABC.345/01DE-35`
(Receita Federal) e titulo `1023 8501 06 71` (OBMEP).

**Pendencia do CNPJ reduzida.** A regra numerica da e-Financeira (DV = resto, resto 10
vale 0) e a forma "11 - resto" da pergunta 14 deram o mesmo DV em 20.000 bases numericas
sorteadas: para CNPJ numerico, resto 0 ou 1 resulta em DV 0, por regra oficial. Para
base com letra, a pergunta 14 continua sem tratar esse caso, e `completar_cnpj` devolve
None; o corpus nao gera CNPJ alfanumerico nessa situacao.

**A fonte de uma IA foi descartada.** Uma das pesquisas trazidas ao projeto atribuia a
Resolucao TSE 23.659/2021 os pesos do titulo e uma excecao para SP e MG, e dava regra do
CNS provisorio diferente da ANS. A resolucao foi lida: nao contem pesos, tratamento de
resto nem excecao por UF. Nada dessa pesquisa foi usado.

### Achados sobre a biblioteca

`scripts/tests/test_dv_independente.py` confere as duas implementacoes nos dois
sentidos, com semente fixa: numeros completados aqui sao aceitos pela biblioteca e
recusados com o ultimo digito alterado; numeros gerados pela biblioteca sao aceitos aqui.
CPF, CNPJ (numerico e alfanumerico), PIS/NIT e CNS (definitivo e provisorio) concordam.
O titulo de eleitor tem **duas divergencias**, verificadas no codigo da versao instalada:

1. **A biblioteca nao aplica a excecao de SP (01) e MG (02)** descrita pela OBMEP
   (resto 0 vale 1). Nos casos em que as duas convencoes diferem, a biblioteca aceita o
   numero calculado sem a excecao e recusa o calculado com ela. Medido sobre 10.000
   sequenciais sorteados, **18,7%** dos titulos de SP e MG caem nesse caso. Como a
   excecao so tem fonte secundaria, nao se decide aqui qual convencao esta certa.
2. **`generate()` so sorteia UF de 01 a 18**, embora a tabela do TSE va ate 28. Nao
   afeta a validacao, so a geracao.

Consequencias para o corpus:
- titulos de SP e MG em que as convencoes divergem (`titulo_ambiguo`) **nao entram como
  positivos**: nao tem gabarito inequivoco;
- os titulos do corpus nao sao gerados pela `generate()` da biblioteca, para cobrir as 28
  UFs;
- a divergencia entra nas limitacoes: o detector da camada herda a convencao da
  biblioteca, e titulos reais de SP e MG que sigam a excecao seriam recusados por ele.
  Isso e propriedade do detector avaliado, medida aqui antes do congelamento, e nao
  defeito a corrigir na camada depois de ver resultado.

Os testes caracterizam as duas divergencias de forma explicita; nao as escondem.

## Data da revisao
2026-10-08

---

## Revisao de 14/10/2026: regras dos negativos dificeis e contagem

Decisoes do autor, 14/10/2026. Escritas antes de qualquer geracao (tarefa 3.6).

### Regras que valem para todo o corpus

- **Colisao entre tipos de mesmo comprimento.** CPF e PIS/NIT tem 11 digitos; um numero
  truncado de outro tipo pode cair no mesmo comprimento. Positivo: valido **so** no
  proprio tipo, nas duas implementacoes (`validate-docbr` e `scripts/dv_independente.py`).
  Negativo: invalido em **todos** os tipos do seu comprimento, nas duas implementacoes.
- **Gabarito dos negativos.** Cada negativo registra tipo imitado, posicao no texto
  original e `classe_negativo`. E assim que um falso positivo e localizado e contado.
- **Titulo de eleitor.** Numeros de SP e MG em que as duas convencoes divergem
  (`titulo_ambiguo`) nao entram nem como positivo nem como negativo.

### Classes para os cinco tipos com digito verificador (CPF, CNPJ, CNS, PIS/NIT, titulo)

| Classe | Regra de geracao | Casos por tipo |
|---|---|---:|
| N1 - digito verificador invalido | base valida, com a mascara do tipo, ultimo digito trocado; invalido nas duas implementacoes | 10 |
| N2 - mesmo comprimento, sem mascara | sequencia de digitos do comprimento do tipo, em contexto de outro identificador (protocolo, nota fiscal, pedido), invalida em todos os tipos do comprimento | 10 |
| N3 - formato parcial | documento valido com um digito a menos, com e sem mascara | 10 |
| N4 - repeticao trivial | todos os digitos iguais | 10 |
| N5 - numero em contexto nao pessoal | valor monetario, CEP ou data com pontuacao parecida com a do tipo | 10 |

Na N4 existem exatamente 10 sequencias de digitos iguais por comprimento (0 a 9): a
classe as cobre todas. Parte delas fecha a conta do DV (por exemplo, o CPF de onze
algarismos 1). A recusa de digitos todos iguais esta nas regras RV_01 a RV_03 da
Previdencia ("Regras de Validacao", v1.14), fonte oficial ja citada nesta ADR.

### Classes para telefone e endereco eletronico (sem digito verificador)

| Tipo | Classe | Regra | Casos |
|---|---|---|---:|
| Telefone | T1 - quantidade errada de digitos | DDD seguido de 7 ou de 10 digitos | 25 |
| Telefone | T2 - sequencia que parece telefone | horario, intervalo numerico ou codigo com a mesma pontuacao | 25 |
| Endereco eletronico | E1 - incompleto | sem parte local ou sem dominio | 25 |
| Endereco eletronico | E2 - arroba que nao e endereco | perfil de rede social, nome de arquivo com arroba | 25 |

**Cortadas:**
- **T3 (telefone de servico publico):** exigiria uma lista oficial de numeros; sem fonte,
  nao se inventa. Volta so se houver fonte.
- **E3 (endereco ofuscado legivel, como "nome [arroba] dominio"):** fica **fora do
  corpus**. Correcao de uma proposta anterior desta mesma tarefa, que a classificava como
  negativo: um endereco ofuscado continua identificando a pessoa, e o gabarito puniria
  quem o mascara. Como positivo, ampliaria a normalizacao alem do que a proposta aprovada
  define (conteudo codificado, caracteres invisiveis e separadores entre digitos).
  Registrado como trabalho futuro.

### Contagem

| | Positivos | Negativos | Total |
|---|---:|---:|---:|
| Cinco tipos com DV | 250 | 250 (5 classes x 10 x 5 tipos) | 500 |
| Telefone | 50 | 50 (2 classes x 25) | 100 |
| Endereco eletronico | 50 | 50 (2 classes x 25) | 100 |
| **Corpus** | **350** | **350** | **700** |

Motivo (alternativa de 25 negativos por tipo descartada): com 50 negativos por tipo e
nenhum falso positivo observado, o limite superior do intervalo de 95% fica em cerca de
6% (regra de tres, 3/50); com 25, em cerca de 12%, o que mal separa um detector bom de um
ruim. O custo de API e zero nos dois casos (ADR-0003). O intervalo por classe, com 10 ou
25 casos, e largo e declarado junto de cada resultado (RQ-13); a comparacao principal se
apoia no agregado por tipo.

### Ainda aberto na tarefa 3.5
Formato dos textos (frases-modelo, mascaras, sobreposicao, mais de uma ocorrencia por
texto), geracao de telefone e endereco eletronico sem coincidir com dados reais, e o
tratamento do numero sintetico valido que coincida com documento emitido.

## Data da revisao
2026-10-14

---

## Revisao de 14/10/2026 (segundo bloco): formato dos textos e dados que coincidam com reais

Decisoes do autor, 14/10/2026. Fecham o desenho do corpus (tarefa 3.5); a geracao e a
tarefa 3.6.

### Formato dos textos
- Frases curtas no dominio de atendimento ao cliente de comercio eletronico, o mesmo do
  assistente de referencia.
- De 1 a 3 ocorrencias por texto, misturando positivos e negativos no mesmo texto.
- Mascaras variadas: cada tipo aparece com e sem pontuacao (RQ-02, "formatos variados").
- Gabarito por posicao no texto **original**, antes de qualquer normalizacao (RQ-07):
  inicio, fim, tipo, valor, natureza, e `classe_negativo` nos negativos. Mais de uma
  ocorrencia por texto testa se o mascaramento recai na posicao certa de cada uma.
- Geracao com semente fixa (`SEMENTE_MESTRA`), reproduzivel e conferida por hash.

### Endereco eletronico: so dominios reservados para exemplo

| Campo | Registro |
|---|---|
| Claim | `example.com`, `example.net` e `example.org` sao reservados para documentacao e nao podem ser registrados |
| Fonte 1 | RFC 2606, "Reserved Top Level DNS Names", BCP 32, junho de 1999, secao 3: https://www.rfc-editor.org/rfc/rfc2606.html |
| Fonte 2 | RFC 6761, "Special-Use Domain Names", fevereiro de 2013, Standards Track, secao 6.5 (reservados para documentacao, nao registraveis): https://www.rfc-editor.org/rfc/rfc6761.html |
| Data da consulta | 2026-10-14 |
| Divergencia | o cabecalho da RFC 6761 declara que atualiza a RFC 2606; a pagina da RFC 2606 consultada nao exibe a indicacao "Updated by". As duas concordam sobre os tres dominios |
| Decisao | todo endereco eletronico do corpus usa um dos tres dominios. Nenhum pode pertencer a pessoa real |

### Telefone: sem garantia de inexistencia
Nao foi localizada faixa de numeracao telefonica brasileira reservada para ficcao ou
documentacao. Os telefones do corpus sao sorteados no formato brasileiro e **podem
coincidir com numeros em uso**. Declarado como limitacao; nenhum telefone e associado a
nome ou outro atributo.

### Documentos validos que coincidam com documentos emitidos
CPF, CNPJ, CNS, PIS/NIT e titulo validos sao sorteados ao acaso e **podem coincidir com
numeros ja emitidos**. Nao ha como garantir o contrario: um numero com DV valido e, por
construcao, um numero que poderia ter sido emitido. O que se declara e o mecanismo:
geracao aleatoria com semente fixa, sem consulta a base alguma, e nenhum numero associado
a nome, endereco ou outro atributo de pessoa real. Nao se afirma nada sobre a LGPD:
conformidade juridica esta fora do escopo declarado.

Os nomes, se usados nas frases, vem do Faker `pt_BR` e nunca acompanham documento que
os identifique como pessoa real.

### Estado da tarefa 3.5
Desenho fechado: tipos e distribuicao, gabarito independente da biblioteca, regras de
colisao, classes e contagem dos negativos, formato dos textos e declaracoes sobre dados
que coincidam com reais. RQ-02 e RQ-03 tem o desenho pronto; o criterio de aceitacao de
ambos (gabarito versionado com contagens; declaracao no `CONGELADO.md`) se cumpre na 3.6 e
na 3.11.

## Data da revisao
2026-10-14

---

## Revisao de 14/10/2026 (terceiro bloco): insumos da geracao

Decisoes do autor, 14/10/2026, antes da escrita do gerador (tarefa 3.6).

### CNPJ: 25 numericos e 25 alfanumericos
Nos 50 positivos e, na mesma proporcao, nos negativos. O formato fica registrado como
atributo da ocorrencia e o resultado do CNPJ e reportado separado por formato. Motivo:
mede se cada detector reconhece o formato atribuido desde julho de 2026 (pergunta 14 da
Receita Federal, ja citada), com amostra que ainda permite leitura.

### Telefone: DDDs da Anatel e formato do numero movel

| Campo | Registro |
|---|---|
| Claim | existem 67 Codigos Nacionais (DDD): 11-19, 21, 22, 24, 27, 28, 31-35, 37, 38, 41-49, 51, 53-55, 61-69, 71, 73-75, 77, 79, 81-89, 91-99 |
| Fonte | Anatel, "Perguntas Frequentes - Areas Tarifarias", pergunta 6 (cita a Resolucao 768/2024 e o Acordao 202/2025). Duas copias publicadas pela Anatel, lidas em separado, dao a mesma lista: https://sistemas.anatel.gov.br/anexar-api/publico/anexos/download/7c51a53e26edf77426cb85e42f1080de e https://sistemas.anatel.gov.br/anexar-api/publico/anexos/download/a8c6650c72539ff2334c327ab5c169e4 |
| Nivel | documento oficial da Anatel (sem numero de ato proprio) |
| Data da consulta | 2026-10-14 |
| Observacao | o documento afirma que "as areas locais serao equivalentes as areas dos 67 codigos DDD existentes" e que a mudanca nao altera o numero do usuario |

| Campo | Registro |
|---|---|
| Claim | o numero do servico movel tem 9 digitos, com o 9 a esquerda; o fixo tem 8 |
| Fonte | "Caderno Tecnico de Comunicacao - Requisitos de Comunicacao para a Implantacao do Nono Digito", GT-COM, 22/07/2016, publicado no sistema da Anatel, com base na Resolucao Anatel 553/2010: https://sistemas.anatel.gov.br/anexar-api/publico/anexos/download/1cb95a68db5a9c02bfe2196d5f7c112b |
| Nivel | documentacao tecnica publicada pela Anatel, nao o ato normativo |
| Data da consulta | 2026-10-14 |
| Lacuna | a fonte nao diz qual pode ser o primeiro digito do numero fixo |

**Decisao:** os 50 telefones positivos sao **moveis**: DDD da lista acima, seguido de 9 e
de 8 digitos sorteados. Telefone fixo fica fora, porque a regra do primeiro digito nao tem
fonte. A variacao de formato exigida pelo RQ-02 vem das mascaras: com parenteses e hifen,
so digitos, com codigo do pais e com espacos.

### N4 por tipo: base de cada negativo
Medido na maquina do experimento, sobre as 10 sequencias de digitos iguais de cada tipo:

| Tipo | Quantas fecham a conta do DV | Base do rotulo negativo |
|---|---|---|
| CPF | 10 de 10 | regra RV_01 da Previdencia (digitos todos iguais) |
| CNPJ | 1 de 10 (zeros) | regra RV_02 |
| PIS/NIT | 1 de 10 (zeros) | regra RV_03 |
| CNS | 0 de 10 | DV invalido |
| Titulo | a de zeros fecha a conta, com UF 00 | UF fora da tabela do TSE (art. 36 da Resolucao 23.659/2021); as outras nove nao fecham |

`scripts/dv_independente.py` ganha `estado(tipo, numero)`, com tres valores: valido,
invalido e **indefinido**. Indefinido e o numero cujo rotulo as fontes nao decidem
(titulo ambiguo de SP e MG; CNPJ alfanumerico com resto 0 ou 1). Sem o terceiro valor, um
titulo valido por uma das convencoes viraria negativo no gabarito. Numero indefinido nao
entra no corpus.

### Terceiro achado sobre a biblioteca
**A `validate-docbr` 2.0.0 nao confere a UF do titulo de eleitor**: aceita 00 e de 29 a
99 quando a conta do DV fecha. A tabela do TSE vai de 01 a 28. Caracterizado por teste
(`test_biblioteca_aceita_titulo_com_uf_fora_da_tabela`). Consequencia: pela regra de
colisao, numero que so a biblioteca aceita nao entra nem como positivo nem como negativo.
A propriedade do detector fica declarada nas limitacoes, como os outros dois achados.

## Data da revisao
2026-10-14

---

## Revisao de 14/10/2026 (quarto bloco): gerador e desvios do desenho

`scripts/gerar_corpus_pii.py` implementa o desenho desta ADR. Conferencias internas
(contagens, posicao, colisao) e conferencia externa por
`scripts/tests/test_gerar_corpus_pii.py`, que relê o corpus inteiro ocorrencia por
ocorrencia. Frases-modelo escritas com assistencia de IA; o corpus e sintetico por
desenho, e nao se confunde com as mensagens legitimas da tarefa 3.8.

### O telefone entra na regra de colisao
Celular sem mascara tem 11 digitos, como CPF e PIS/NIT. Todo numero e conferido tambem
contra o formato de celular (DDD da Anatel, 9, oito digitos), e com o prefixo 55 retirado
quando aparece.

### Desvio da contagem aprovada na N4 (CPF, PIS/NIT e titulo)
A N4 previa as 10 sequencias de digitos iguais em cada tipo. Tres delas nao sao negativo
inequivoco, e a regra de colisao as exclui:

| Tipo | Sequencia excluida | Motivo |
|---|---|---|
| CPF | onze algarismos 9 | e celular valido pela regra de formato (DDD 99, 9, oito digitos) |
| PIS/NIT | onze algarismos 9 | idem |
| Titulo | doze zeros | a biblioteca aceita (UF 00, terceiro achado); numero que so a biblioteca aceita nao entra |

**Correcao do bloco anterior:** a tabela da N4 do terceiro bloco de 14/10/2026 dava o
titulo de doze zeros como negativo, com base na tabela de UF do TSE. Pela regra de
colisao, que exige recusa nas duas implementacoes, ele fica fora.

Nesses tres tipos a N4 tem 9 casos e a N2 tem 11. O total de 50 negativos por tipo e o
de 350 no corpus nao mudam.

### Defeito encontrado e corrigido antes da primeira geracao
O gerador conferia o negativo de telefone **antes** de aplicar o formato. O prefixo +55
de um telefone curto produz outra sequencia de digitos: "+55 33 988-9435" vira
55339889435, que e **PIS/NIT valido**. O teste externo encontrou o caso; o gerador passa a
conferir tambem o valor como aparece no texto (`valor_negativo_aceitavel`), e o caso
virou teste de regressao. Nenhum corpus tinha sido gravado: o defeito nao chegou a
nenhum artefato versionado. Mesmo assim, o estado com defeito nao foi commitado
separadamente, e isso fica registrado aqui.

### Desvio do formato: N4 e N5 so numericas no CNPJ
As sequencias de digitos iguais (N4) e os valores monetarios (N5) sao, por definicao,
numericos. N1, N2 e N3 tem 5 alfanumericos e 5 numericos cada. Medido no corpus gerado:
nos negativos de CNPJ, **35 numericos e 15 alfanumericos**, e nao 25 para 25 como nos
positivos.

## Data da revisao
2026-10-14

---

## Resultado da geracao - 14/10/2026

`python scripts/gerar_corpus_pii.py` na maquina do experimento, depois do commit
`e5c2b3e` (gerador e testes); corpus commitado em `22d91f7`.

| Item | Valor |
|---|---|
| Arquivo | `conjunto_teste/pii/corpus.jsonl` (LF, 347 linhas) |
| Semente | 20260829 (`SEMENTE_MESTRA`) |
| Textos | 347, com 1 a 3 ocorrencias cada |
| Ocorrencias | 700: 350 positivas e 350 negativas |
| sha256 | `ff21394b6b2e7c2f6ce3c0451a1ed77bac2e48becde145988e33be8ea30aa43e` |

| Tipo | Positivos | Negativos por classe |
|---|---:|---|
| CPF | 50 | N1 10, N2 11, N3 10, N4 9, N5 10 |
| CNPJ | 50 (25 numericos, 25 alfanumericos) | N1 10, N2 10, N3 10, N4 10, N5 10 (35 numericos, 15 alfanumericos) |
| CNS | 50 | N1 10, N2 10, N3 10, N4 10, N5 10 |
| PIS/NIT | 50 | N1 10, N2 11, N3 10, N4 9, N5 10 |
| Titulo | 50 | N1 10, N2 11, N3 10, N4 9, N5 10 |
| Telefone | 50 (celulares) | T1 25, T2 25 |
| Endereco eletronico | 50 (dominios reservados) | E1 25, E2 25 |

**Reprodutibilidade verificada:** o mesmo gerador, com a mesma semente, produz o mesmo
sha256 no Python 3.13.2 da maquina do experimento e num Python 3.10.12 independente. A
geracao nao depende da versao do interpretador entre essas duas.

O corpus entra no mapeamento de rotulos (ADR-0018) com um registro por texto: grupo PII,
`origem_rotulo = propria`, e as contagens de ocorrencias como atributo. O gabarito por
ocorrencia fica no proprio corpus.

**RQ-02:** a aceitacao ("gabarito versionado, com contagem declarada de positivos e de
negativos dificeis por tipo") tem evidencia nesta secao e no arquivo. A mudanca de estado
do requisito e feita no fechamento da etapa.

## Data da revisao
2026-10-14

---

## Revisao de 28/10/2026: formato parcial de mascara

**Contexto.** Na orientacao de 21/10/2026, o orientador perguntou se o sistema aceita
documento sem pontuacao, formatado e **parcialmente formatado**, e alertou que um dado
pode vazar justamente por estar parcialmente formatado. O corpus de 14/10 so tinha duas
formas nos positivos de documento (mascara completa, 25; sem mascara, 25). A N3
("formato parcial") e outra coisa: documento com um digito a menos. A lacuna era real, e
o corpus ainda nao estava congelado.

**Decisao do autor, 28/10/2026**, antes de qualquer regra da camada:

- **Regra unica de formato parcial**, para os cinco documentos: a mascara oficial com
  pelo menos um separador removido e pelo menos um mantido; ou, quando a mascara nao e so
  de espacos, todos os separadores trocados por espaco. Sorteio com a semente fixa
  (`mascarar_parcial`). Exemplos de forma: `999.999.99999`, `999999.999-99`,
  `999 999 999 99`; `9999 99999999` no titulo.
- **Positivos de documento:** 17 com mascara completa, 17 sem mascara e 16 parciais
  (`i % 3`). O CNPJ mantem 25 numericos e 25 alfanumericos.
- **Telefone:** quinto formato, parcial (o formato `(DD) NNNNN-NNNN` sem o espaco, sem o
  hifen ou sem os parenteses); 10 positivos por formato. O T1 passa a sortear entre os
  cinco formatos.
- **N1** (digito verificador invalido): 5 dos 10 de cada documento em formato parcial.
  Sem isso, "estar parcialmente formatado" seria pista exclusiva de positivo, e um
  detector ganharia acerto sem merecer.
- O atributo `mascara` dos positivos de documento e da N1 passa de booleano para
  `completa`, `ausente` ou `parcial`.

**Alternativas.** (a) So no CPF, o tipo citado na orientacao: mais rapido, mas o alerta
vale para qualquer documento mascarado. (b) Nao incluir e declarar a limitacao:
descartada, a lacuna era corrigivel antes do congelamento.

**Consequencia.** O protocolo 8.4 passa a reportar o resultado por formato de mascara
(completa, ausente, parcial), em vez de "com e sem mascara". Como a ordem dos sorteios
mudou, todo o corpus foi gerado de novo: numeros e frases diferentes dos de 14/10, com as
mesmas classes e contagens de ocorrencia.

## Resultado da geracao - 28/10/2026

`python scripts/gerar_corpus_pii.py`, gerado inicialmente em Python 3.10.12.

| Item | Valor |
|---|---|
| Arquivo | `conjunto_teste/pii/corpus.jsonl` (LF, 355 linhas) |
| Semente | 20260829 (`SEMENTE_MESTRA`) |
| Textos | 355, com 1 a 3 ocorrencias cada |
| Ocorrencias | 700: 350 positivas e 350 negativas, mesmas classes e contagens de 14/10 |
| sha256 | `2ed3eb9fc6cba2746ec60c544768d5e42b13eb730c2583e3aafe944c2990a6c7` |

| Formato | Positivos por documento | N1 por documento |
|---|---:|---:|
| completa | 17 | 5 |
| ausente | 17 | - |
| parcial | 16 | 5 |

CNPJ positivo por formato e natureza: numerico 9 completa, 8 ausente, 8 parcial;
alfanumerico 8, 9, 8. Telefone positivo: 10 em cada um dos cinco formatos.

O corpus de 14/10 (sha256 `ff21394b...30aa43e`) fica no historico do Git e deixa de valer.
