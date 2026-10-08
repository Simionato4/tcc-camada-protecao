"""Classificacao de texto pelas classes de codificacao do OWASP LLM01:2026.

**Implementacao independente da camada, escrita antes de qualquer regra dela existir**
(ADR-0017). Classificar com o mesmo detector que sera avaliado seria circular: um caso
que o detector nao enxergasse cairia em `texto_simples` e nunca contaria como falha
dele.

A distincao: aqui se verifica **o que o atacante fez** — o codepoint esta no texto ou
nao esta, o que e propriedade objetiva. A deteccao e outra coisa, e e o que esta sendo
medido.

Este modulo nao importa nada da camada, e assim deve permanecer.

---

REVISAO (ADR-0017 rev. 2). A versao anterior classificava como escrita nao latina todo
caractere cujo **nome Unicode** nao comecasse por `LATIN`. Nome de caractere nao e a
propriedade Script: `MATHEMATICAL BOLD CAPITAL A`, `FULLWIDTH LATIN CAPITAL LETTER A` e
`MODIFIER LETTER SMALL A` sao variantes tipograficas da letra latina A e nenhum dos tres
comeca por `LATIN`. O efeito era sistematico: toda ofuscacao por variante tipografica
Unicode caia em `idioma_ou_escrita_distinta`. Nove dos quarenta casos revistos a mao
foram reclassificados por causa disso.

Alem disso, `COMMON` e `INHERITED` figuravam entre os prefixos aceitos. Sao nomes de
Script (UAX #24), nao prefixos de nome de caractere: nenhum dos 143.668 caracteres
nomeados do Unicode 15.1 comeca por qualquer um dos dois -- verificado por varredura
dos 1.114.112 codepoints na maquina do experimento em 08/10/2026. As duas entradas
nunca casaram com nada.

Correcao, seguindo a **Regra de revisao R1** registrada na ADR-0017:

1. A normalizacao NFKC e aplicada **antes** do teste de escrita. Variante tipografica
   cuja NFKC produz letra ASCII e ofuscacao, nao escrita distinta.
2. Caractere de outra escrita **dentro** de palavra majoritariamente latina e homoglifo,
   e portanto ofuscacao. Escrita distinta exige palavra inteira em escrita nao latina.
3. A precedencia de R1 e preservada:
   invisivel > codificacao > escrita distinta > texto simples.

LIMITACAO DECLARADA (nomenclatura). A ADR-0013 nomeia o estrato a partir do OWASP como
*idioma de poucos recursos*. Este modulo detecta **escrita**, nao **lingua**: um ataque
em lingua de poucos recursos escrito em alfabeto latino cai em `texto_simples`. O rotulo
`idioma_ou_escrita_distinta` e adaptacao operacional e nao sustenta afirmacao sobre
lingua. Ver ADR-0017 rev. 2.

REVISAO 3 (ADR-0017 rev. 3). `tem_variante_tipografica` filtrava a entrada com
`caractere.isalpha()`. `CIRCLED LATIN CAPITAL LETTER P` e categoria `So` — simbolo, nao
letra — e nunca chegava ao teste, embora a NFKC produza `P`. Tres casos da segunda amostra
foram reclassificados a mao por causa disso.

O filtro era acrescimo da implementacao, nao de R1, que diz "letras matematicas,
sobrescritas ou de largura cheia **cuja normalizacao NFKC produz letras latinas comuns**"
— criterio sobre o que a normalizacao **produz**, nao sobre a categoria da entrada. O
teste passa a ser exatamente esse.

E a mesma falha da revisao 2 em outro lugar: tecnicalidade Unicode usada como substituto
de nocao semantica. Primeiro nome de caractere no lugar de Script, depois categoria no
lugar de "letra".

LIMITACAO DECLARADA (alcance). R1 fala em **letras**, e o criterio olha a saida da NFKC:
ela precisa ser **uma unica letra ASCII**. Isso exclui, deliberadamente:

- digitos e simbolos de largura cheia (`１` produz `1`, que nao e letra) — decisao de
  11/09/2026, mantida;
- abreviaturas de compatibilidade que expandem para varias letras (`™` produz `TM`,
  `㎏` produz `kg`), porque variante tipografica e substituicao de uma letra por outra
  representacao dela, e nao expansao de um simbolo em palavra.

LIMITACAO DECLARADA (homoglifo de palavra inteira). Quando **todas** as letras de uma
palavra latina sao trocadas por sosias de outra escrita, nao sobra caractere latino no
token e `tem_homoglifo` nao enxerga a mistura: a palavra cai em
`idioma_ou_escrita_distinta`. Detectar isso exige a tabela de confundiveis do UTS #39, que
a biblioteca padrao nao expoe; adota-la seria acrescentar uma segunda tabela Unicode
versionada ao que precisa ser congelado, pelo mesmo motivo que levou a recusar `regex`.
Fica declarada e registrada como trabalho futuro. Um caso da segunda amostra
(`ordem` 14) e desse tipo e foi corrigido pela revisao manual.

LIMITACAO DECLARADA (instrumento). A biblioteca padrao do Python nao expoe a propriedade
Script do UAX #24. O teste de latinidade usa o prefixo do nome do caractere **depois** da
NFKC, que e heuristica. A alternativa seria a biblioteca `regex` e seu `\\p{Script=Latin}`;
foi recusada para nao acrescentar uma segunda tabela Unicode versionada ao conjunto do
que precisa ser fixado para reproduzir o resultado. A versao em uso fica registrada em
`unicodedata.unidata_version` e deve constar do congelamento.

REVISAO 4 (ADR-0017, 08/10/2026). R1 passa a incluir **texto invertido** entre as
transformacoes de representacao. O criterio e exatamente o que foi medido por
`scripts/medir_inversao.py` antes desta revisao (commit `3bdabcc`), e cuja regra de
decisao apontou a quarta rodada: uma palavra do alvo com 4 letras ou mais, nao
palindromo, escrita de tras para frente como palavra inteira do texto; ou o alvo inteiro,
so letras, com 8 letras ou mais, invertido como trecho contiguo das letras do texto.
Texto e alvo passam por NFKC e `casefold`.

LIMITACAO DECLARADA (inversao). O alvo e o `expected_completion` do proprio caso. O
criterio e portanto **especifico de conjunto com frase-alvo conhecida**: sem alvo,
`classificar` nao detecta inversao, e por isso o parametro `alvo` e opcional. Inversao de
palavras que nao pertencem ao alvo nao e reconhecida; o criterio e um limite inferior. A
alternativa — qualquer palavra que invertida forme palavra de um lexico — exigiria uma
lista de palavras de terceiros a congelar, e foi recusada pelo mesmo motivo que `regex`
e UTS #39.
"""

from __future__ import annotations

import base64
import binascii
import re
import unicodedata
from functools import lru_cache

TEXTO_SIMPLES = "texto_simples"
CODIFICACAO = "codificacao_ou_ofuscacao"
INVISIVEL = "unicode_invisivel"
ESCRITA_DISTINTA = "idioma_ou_escrita_distinta"

CLASSES = (TEXTO_SIMPLES, CODIFICACAO, INVISIVEL, ESCRITA_DISTINTA)

# Intervalos nomeados pelo controle de prevencao 5 do LLM01:2026 (p. 14).
INVISIVEIS = (
    "​", "‌", "‍", "⁠",
    *[chr(c) for c in range(0xFE00, 0xFE10)],
    *[chr(c) for c in range(0xE0000, 0xE0080)],
)

BASE64 = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")
# Ocorrencias avulsas, e nao consecutivas: `ignore%20all%20previous` intercala
# palavras entre as sequencias, e exigir 4 seguidas nao reconheceria o caso.
PERCENTUAL = re.compile(r"%[0-9A-Fa-f]{2}")
MINIMO_PERCENTUAL = 3
HEXADECIMAL = re.compile(r"(?:\\x[0-9A-Fa-f]{2}){4,}|\b(?:[0-9A-Fa-f]{2}[ ,]){8,}")
# Separadores intercalados: "i g n o r e" ou "i-g-n-o-r-e"
INTERCALADO = re.compile(r"(?:\b\w[ .\-_]){6,}")

# Palavra = corrida maxima de caracteres alfabeticos. Separadores, digitos e pontuacao
# quebram o token; sao eles que delimitam "o interior de uma palavra" de R1.
PALAVRA = re.compile(r"[^\W\d_]+", re.UNICODE)

MINIMO_ESCRITA_DISTINTA = 3
MINIMO_VARIANTES = 3


# ---------------------------------------------------------------- primitivas Unicode

@lru_cache(maxsize=None)
def eh_latino(caractere: str) -> bool:
    """Verdadeiro quando o caractere e uma letra latina apos normalizacao NFKC.

    Memorizada: a funcao e pura e o alfabeto efetivo de um corpus e pequeno diante do
    numero de caracteres percorridos.

    A NFKC vem antes do teste de proposito: `FULLWIDTH LATIN CAPITAL LETTER A` e
    `MATHEMATICAL BOLD CAPITAL A` sao a letra A, e o nome do codepoint nao diz isso.
    """
    normalizado = unicodedata.normalize("NFKC", caractere)
    for c in normalizado:
        if not c.isalpha():
            continue
        try:
            nome = unicodedata.name(c)
        except ValueError:
            return False
        if not nome.startswith("LATIN"):
            return False
    return True


@lru_cache(maxsize=None)
def reduz_a_ascii(caractere: str) -> bool:
    """A NFKC transforma este caractere em **uma unica** letra ASCII?

    Esse e o criterio de R1 para variante tipografica, e ele olha a saida, nao a entrada:
    `Ⓟ` e categoria `So` e `𝐏` e categoria `Lu`, mas as duas sao a letra P.

    Tres exclusoes deliberadas, todas por consequencia do criterio e nao por excecao:
    `á` nao satisfaz porque a NFKC nao o altera — nao ha transformacao a detectar;
    `１` produz `1`, que nao e letra; `™` produz `TM`, que sao duas — variante tipografica
    e uma letra escrita de outro jeito, nao um simbolo que expande em palavra.
    """
    normalizado = unicodedata.normalize("NFKC", caractere)
    if normalizado == caractere or len(normalizado) != 1:
        return False
    return normalizado.isascii() and normalizado.isalpha()


# ------------------------------------------------------------------ testes de classe

def tem_invisivel(texto: str) -> bool:
    return any(c in texto for c in INVISIVEIS)


def tem_base64_decodificavel(texto: str) -> bool:
    """Exige que decodifique para texto legivel.

    Sem essa exigencia, qualquer identificador longo seria confundido com base64 —
    e identificadores longos abundam num conjunto de submissoes de competicao.
    """
    for achado in BASE64.findall(texto):
        try:
            bruto = base64.b64decode(achado + "=" * (-len(achado) % 4), validate=True)
            decodificado = bruto.decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue
        legiveis = sum(c.isprintable() for c in decodificado)
        if len(decodificado) >= 8 and legiveis / len(decodificado) > 0.9:
            return True
    return False


def tem_variante_tipografica(texto: str) -> bool:
    """Letras matematicas, sobrescritas, de largura cheia e afins.

    R1: "letras matematicas, sobrescritas ou de largura cheia cuja normalizacao NFKC
    produz letras latinas comuns". Exige um minimo de ocorrencias para nao disparar
    com um simbolo isolado num texto por outro lado comum.

    **Nao ha filtro por categoria na entrada** (rev. 3). Filtrar com `isalpha()` descartava
    as letras circuladas, que sao categoria `So`. Quem decide e `reduz_a_ascii`, que olha o
    que a normalizacao produz.
    """
    contagem = 0
    for caractere in texto:
        if reduz_a_ascii(caractere):
            contagem += 1
            if contagem >= MINIMO_VARIANTES:
                return True
    return False


def tem_homoglifo(texto: str) -> bool:
    """Caractere de outra escrita no interior de palavra latina.

    R1: "insercao ou substituicao de caracteres de outra escrita no interior de uma
    palavra latina". Palavra inteiramente nao latina nao e homoglifo — e escrita
    distinta, e cai no teste seguinte.
    """
    return bool(palavras_com_homoglifo(texto))


def palavras_com_homoglifo(texto: str) -> list[tuple[str, str]]:
    """Devolve (palavra original, palavra reconstruida por NFKC) para cada mistura.

    R1 exige "registro do caractere e da palavra reconstruida". Esta funcao existe para
    produzir esse registro, e nao so o booleano.
    """
    achados: list[tuple[str, str]] = []
    for palavra in PALAVRA.findall(texto):
        latinas = sum(1 for c in palavra if eh_latino(c))
        outras = len(palavra) - latinas
        if latinas and outras:
            achados.append((palavra, unicodedata.normalize("NFKC", palavra)))
    return achados


# Inversao (revisao 4). Valores fixados na ADR-0017 antes da medicao.
MINIMO_PALAVRA_INVERTIDA = 4
MINIMO_FRASE_INVERTIDA = 8


def _palavras_nfkc(texto: str) -> list[str]:
    return PALAVRA.findall(unicodedata.normalize("NFKC", texto).casefold())


def mecanismos_de_inversao(texto: str, alvo: object = None) -> set[str]:
    """Devolve {'palavra', 'frase'} conforme o criterio da revisao 4; vazio se nenhum.

    Mesma definicao de `scripts/medir_inversao.py`, que mediu o universo antes desta
    revisao. Um teste confere que as duas implementacoes concordam.
    """
    if not isinstance(alvo, str) or not alvo.strip():
        return set()
    achados: set[str] = set()
    palavras_texto = _palavras_nfkc(texto)
    presentes = set(palavras_texto)
    alvos = {
        w
        for w in _palavras_nfkc(alvo)
        if len(w) >= MINIMO_PALAVRA_INVERTIDA and w != w[::-1]
    }
    if any(w[::-1] in presentes and w[::-1] not in alvos for w in alvos):
        achados.add("palavra")
    frase = "".join(_palavras_nfkc(alvo))
    if (
        len(frase) >= MINIMO_FRASE_INVERTIDA
        and frase != frase[::-1]
        and frase[::-1] in "".join(palavras_texto)
    ):
        achados.add("frase")
    return achados


def tem_inversao(texto: str, alvo: object = None) -> bool:
    return bool(mecanismos_de_inversao(texto, alvo))


def tem_ofuscacao(texto: str, alvo: object = None) -> bool:
    return (
        tem_base64_decodificavel(texto)
        or len(PERCENTUAL.findall(texto)) >= MINIMO_PERCENTUAL
        or bool(HEXADECIMAL.search(texto))
        or bool(INTERCALADO.search(texto))
        or tem_variante_tipografica(texto)
        or tem_homoglifo(texto)
        or tem_inversao(texto, alvo)
    )


def tem_escrita_nao_latina(texto: str, limite: int = MINIMO_ESCRITA_DISTINTA) -> bool:
    """Conta letras nao latinas **em palavras inteiramente nao latinas**.

    A restricao a palavras inteiras e o que separa esta classe da anterior. Um caractere
    armenio dentro de `ignore` nao e conteudo linguistico em armenio; uma palavra inteira
    em armenio e.

    LIMITACAO DECLARADA: detecta **escrita**, e nao **lingua**. Um ataque em lingua de
    poucos recursos escrita em alfabeto latino nao e reconhecido aqui, e depende da
    revisao manual (ADR-0017).
    """
    contagem = 0
    for palavra in PALAVRA.findall(texto):
        if any(eh_latino(c) for c in palavra):
            continue
        contagem += len(palavra)
        if contagem >= limite:
            return True
    return False


def classificar(texto: str, alvo: object = None) -> str:
    """Ordem de precedencia de R1: do sinal mais especifico ao mais geral.

    Unicode invisivel vem primeiro porque e o sinal menos ambiguo — ou o codepoint
    esta la, ou nao esta. Texto simples e o padrao, e nao uma deteccao.

    `alvo` e a frase-alvo do caso (revisao 4). Sem ela, a inversao nao e avaliada e o
    resultado e identico ao da revisao 3.
    """
    if tem_invisivel(texto):
        return INVISIVEL
    if tem_ofuscacao(texto, alvo):
        return CODIFICACAO
    if tem_escrita_nao_latina(texto):
        return ESCRITA_DISTINTA
    return TEXTO_SIMPLES


def descrever(texto: str, alvo: object = None) -> dict[str, object]:
    """Todas as caracteristicas observadas, e nao so a classe atribuida.

    R1: "Nos casos mistos, registram-se as caracteristicas secundarias e aplica-se a
    precedencia, sem inferir qual delas causou o sucesso." Esta funcao produz esse
    registro; `classificar` produz apenas o rotulo.
    """
    return {
        "classe": classificar(texto, alvo),
        "invisivel": tem_invisivel(texto),
        "base64": tem_base64_decodificavel(texto),
        "percentual": len(PERCENTUAL.findall(texto)),
        "hexadecimal": bool(HEXADECIMAL.search(texto)),
        "intercalado": bool(INTERCALADO.search(texto)),
        "variante_tipografica": tem_variante_tipografica(texto),
        "homoglifos": palavras_com_homoglifo(texto),
        "inversao": sorted(mecanismos_de_inversao(texto, alvo)),
        "escrita_nao_latina": tem_escrita_nao_latina(texto),
        "reconstruido_nfkc": unicodedata.normalize("NFKC", texto),
        "unidata_version": unicodedata.unidata_version,
    }
