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
Script (UAX #24), nao prefixos de nome de caractere: nenhum dos 149.186 caracteres
nomeados do Unicode 14.0 comeca por qualquer um dos dois. As duas entradas nunca
casaram com nada.

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

LIMITACAO DECLARADA (alcance). R1 fala em **letras**, e este modulo segue a regra a
risca: `tem_variante_tipografica` so examina caracteres alfabeticos. Digitos e simbolos
de largura cheia — `１２３４` — nao sao reconhecidos, e um ataque que ofusque apenas
caracteres nao alfabeticos cai em `texto_simples`. A escolha foi tomada em 11/09/2026 por
fidelidade ao texto de R1 e fica declarada, nao silenciada.

LIMITACAO DECLARADA (instrumento). A biblioteca padrao do Python nao expoe a propriedade
Script do UAX #24. O teste de latinidade usa o prefixo do nome do caractere **depois** da
NFKC, que e heuristica. A alternativa seria a biblioteca `regex` e seu `\\p{Script=Latin}`;
foi recusada para nao acrescentar uma segunda tabela Unicode versionada ao conjunto do
que precisa ser fixado para reproduzir o resultado. A versao em uso fica registrada em
`unicodedata.unidata_version` e deve constar do congelamento.
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
    """A NFKC transforma este caractere numa letra ASCII?

    Esse e o criterio de R1 para variante tipografica. Repare que `a` acentuado nao
    satisfaz: a NFKC nao o altera, logo nao ha transformacao a detectar.
    """
    normalizado = unicodedata.normalize("NFKC", caractere)
    if normalizado == caractere:
        return False
    letras = [c for c in normalizado if c.isalpha()]
    if not letras:
        return False
    return all(c.isascii() for c in letras)


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
    """
    contagem = 0
    for caractere in texto:
        if not caractere.isalpha():
            continue
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


def tem_ofuscacao(texto: str) -> bool:
    return (
        tem_base64_decodificavel(texto)
        or len(PERCENTUAL.findall(texto)) >= MINIMO_PERCENTUAL
        or bool(HEXADECIMAL.search(texto))
        or bool(INTERCALADO.search(texto))
        or tem_variante_tipografica(texto)
        or tem_homoglifo(texto)
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


def classificar(texto: str) -> str:
    """Ordem de precedencia de R1: do sinal mais especifico ao mais geral.

    Unicode invisivel vem primeiro porque e o sinal menos ambiguo — ou o codepoint
    esta la, ou nao esta. Texto simples e o padrao, e nao uma deteccao.
    """
    if tem_invisivel(texto):
        return INVISIVEL
    if tem_ofuscacao(texto):
        return CODIFICACAO
    if tem_escrita_nao_latina(texto):
        return ESCRITA_DISTINTA
    return TEXTO_SIMPLES


def descrever(texto: str) -> dict[str, object]:
    """Todas as caracteristicas observadas, e nao so a classe atribuida.

    R1: "Nos casos mistos, registram-se as caracteristicas secundarias e aplica-se a
    precedencia, sem inferir qual delas causou o sucesso." Esta funcao produz esse
    registro; `classificar` produz apenas o rotulo.
    """
    return {
        "classe": classificar(texto),
        "invisivel": tem_invisivel(texto),
        "base64": tem_base64_decodificavel(texto),
        "percentual": len(PERCENTUAL.findall(texto)),
        "hexadecimal": bool(HEXADECIMAL.search(texto)),
        "intercalado": bool(INTERCALADO.search(texto)),
        "variante_tipografica": tem_variante_tipografica(texto),
        "homoglifos": palavras_com_homoglifo(texto),
        "escrita_nao_latina": tem_escrita_nao_latina(texto),
        "reconstruido_nfkc": unicodedata.normalize("NFKC", texto),
        "unidata_version": unicodedata.unidata_version,
    }
