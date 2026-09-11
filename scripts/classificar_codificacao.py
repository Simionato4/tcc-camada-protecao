"""Classificacao de texto pelas classes de codificacao do OWASP LLM01:2026.

**Implementacao independente da camada, escrita antes de qualquer regra dela existir**
(ADR-0017). Classificar com o mesmo detector que sera avaliado seria circular: um caso
que o detector nao enxergasse cairia em `texto_simples` e nunca contaria como falha
dele.

A distincao: aqui se verifica **o que o atacante fez** — o codepoint esta no texto ou
nao esta, o que e propriedade objetiva. A deteccao e outra coisa, e e o que esta sendo
medido.

Este modulo nao importa nada da camada, e assim deve permanecer.
"""

from __future__ import annotations

import base64
import binascii
import re
import unicodedata

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

ESCRITAS_LATINAS = ("LATIN", "COMMON", "INHERITED")


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


def tem_ofuscacao(texto: str) -> bool:
    return (
        tem_base64_decodificavel(texto)
        or len(PERCENTUAL.findall(texto)) >= MINIMO_PERCENTUAL
        or bool(HEXADECIMAL.search(texto))
        or bool(INTERCALADO.search(texto))
    )


def tem_escrita_nao_latina(texto: str, limite: int = 3) -> bool:
    """Conta letras de escrita nao latina.

    LIMITACAO DECLARADA: detecta **escrita**, e nao **lingua**. Um ataque em lingua de
    poucos recursos escrita em alfabeto latino nao e reconhecido aqui, e depende da
    revisao manual (ADR-0017).
    """
    contagem = 0
    for caractere in texto:
        if not caractere.isalpha():
            continue
        try:
            nome = unicodedata.name(caractere)
        except ValueError:
            continue
        if not any(nome.startswith(e) for e in ESCRITAS_LATINAS):
            contagem += 1
            if contagem >= limite:
                return True
    return False


def classificar(texto: str) -> str:
    """Ordem de precedencia: do sinal mais especifico ao mais geral.

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
