"""Decodificacao para analise (RF-006, RQ-08; ADR-0027, E1).

A camada decodifica para **analisar**. O que ela encaminha e sempre o texto original:
entregar o decodificado ao modelo seria fazer o trabalho do atacante (RQ-08).

Cada trecho decodificado vira uma "vista": o texto obtido, a posicao do trecho de origem
no texto ORIGINAL, a origem e o nivel. Origens:
- `bloco_de_tag`: caracteres U+E0020 a U+E007E, que espelham o ASCII e nao aparecem na
  tela. A normalizacao os remove; aqui o texto escondido neles e lido;
- `base64`;
- `percentual`: codificacao percentual (`%20`), com pelo menos tres sequencias no trecho.

Profundidade maxima de 2 niveis. Cada resultado e limitado ao tamanho maximo da entrada;
resultado maior e descartado e nao e aprofundado.
"""

from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass
from urllib.parse import unquote

from .contrato import TAMANHO_MAXIMO_TEXTO
from .normalizacao import Normalizado

NIVEL_MAXIMO = 2

_TAG = re.compile("[\U000E0020-\U000E007E]+")
_BASE64 = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{16,}={0,2}(?![A-Za-z0-9+/=])")
_TRECHO = re.compile(r"\S+")
_PERCENTUAL = re.compile(r"%[0-9A-Fa-f]{2}")
_MINIMO_DE_SEQUENCIAS_PERCENTUAIS = 3


@dataclass(frozen=True)
class Vista:
    texto: str
    posicao: tuple[int, int]  # no texto ORIGINAL
    origem: str
    nivel: int


def _legivel(texto: str) -> bool:
    """Texto de verdade: nao vazio e so com caracteres imprimiveis ou de quebra."""
    return bool(texto.strip()) and all(c.isprintable() or c in "\n\r\t" for c in texto)


def _de_base64(trecho: str) -> str | None:
    sem_preenchimento = trecho.rstrip("=")
    completo = sem_preenchimento + "=" * (-len(sem_preenchimento) % 4)
    try:
        texto = base64.b64decode(completo, validate=True).decode("utf-8")
    except (binascii.Error, ValueError):
        return None
    return texto if _legivel(texto) else None


def _de_percentual(trecho: str) -> str | None:
    if len(_PERCENTUAL.findall(trecho)) < _MINIMO_DE_SEQUENCIAS_PERCENTUAIS:
        return None
    try:
        texto = unquote(trecho, errors="strict")
    except UnicodeDecodeError:
        return None
    return texto if _legivel(texto) else None


def _decodificar(texto: str) -> list[tuple[int, int, str, str]]:
    """Trechos codificados de `texto`: (inicio, fim, origem, decodificado)."""
    achados = []
    for encontrado in _BASE64.finditer(texto):
        decodificado = _de_base64(encontrado.group())
        if decodificado is not None:
            achados.append((encontrado.start(), encontrado.end(), "base64", decodificado))
    for encontrado in _TRECHO.finditer(texto):
        decodificado = _de_percentual(encontrado.group())
        if decodificado is not None:
            achados.append((encontrado.start(), encontrado.end(), "percentual", decodificado))
    return sorted(achados)


def vistas_decodificadas(
    original: str, normalizado: Normalizado, limite: int = TAMANHO_MAXIMO_TEXTO
) -> list[Vista]:
    """Vistas decodificadas do texto, ate o nivel 2, em ordem de posicao e de nivel."""
    primeiro_nivel: list[Vista] = []

    for encontrado in _TAG.finditer(original):
        escondido = "".join(chr(ord(c) - 0xE0000) for c in encontrado.group())
        primeiro_nivel.append(Vista(escondido, encontrado.span(), "bloco_de_tag", 1))

    for inicio, fim, origem, decodificado in _decodificar(normalizado.texto):
        posicao = normalizado.intervalo_original(inicio, fim)
        primeiro_nivel.append(Vista(decodificado, posicao, origem, 1))

    vistas: list[Vista] = []
    for vista in sorted(primeiro_nivel, key=lambda v: v.posicao):
        if len(vista.texto) > limite:
            continue  # descartada e nao aprofundada
        vistas.append(vista)
        for _, _, origem, decodificado in _decodificar(vista.texto):
            if len(decodificado) <= limite:
                vistas.append(Vista(decodificado, vista.posicao, origem, NIVEL_MAXIMO))
    return vistas
