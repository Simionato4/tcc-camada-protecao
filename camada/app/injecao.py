"""Deteccao de injecao de instrucao (RF-006, `INJ-02`). Regras aprovadas em 12/11/2026.

A camada procura instrucao de injecao em varias **vistas** do mesmo texto:

| Vista | Disfarce que cobre |
|---|---|
| texto normalizado | largura zero, seletor de variacao, variante tipografica |
| forma canonica (minusculas, sem acento, homoglifo trocado pela letra latina) | maiusculas, homoglifo |
| letras soltas reagrupadas | separadores entre letras |
| texto de tras para frente | invertido |
| vistas decodificadas (`decodificacao.py`) | bloco de tag, base64, codificacao percentual |

Quatro familias de padrao, em portugues e ingles, escritas a partir da forma geral desse
tipo de ataque e desenvolvidas so contra `conjunto_desenvolvimento/`:
anular instrucoes, mudar o regime, nova ordem e extrair o contexto oculto.

Limitacoes declaradas: e lista de padroes, e outra redacao passa (`INJ-02`); a tabela de
homoglifos e pequena; nao ha regra para pedido nocivo (ADR-0027, E4).
"""

from __future__ import annotations

import re
import unicodedata

from .contrato import Deteccao
from .decodificacao import vistas_decodificadas
from .normalizacao import Normalizado

# Letras cirilicas e gregas que imitam letras latinas minusculas. Tabela pequena, de
# proposito: so o que se confunde com o alfabeto latino num texto em portugues ou ingles.
_HOMOGLIFOS = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "х": "x", "у": "y", "і": "i", "ј": "j", "ѕ": "s",
    "һ": "h", "ԁ": "d", "к": "k", "м": "m", "т": "t",
    "ο": "o", "α": "a", "ε": "e", "ι": "i", "κ": "k",
    "ν": "v", "ρ": "p", "τ": "t", "υ": "u", "χ": "x",
}  # fmt: skip


def _canonico(caractere: str) -> str:
    minusculo = caractere.lower()
    if len(minusculo) != 1:
        return caractere
    for parte in unicodedata.normalize("NFD", minusculo):
        if not unicodedata.combining(parte):
            return _HOMOGLIFOS.get(parte, parte)
    return minusculo


def canonica(texto: str) -> str:
    """Minusculas, sem acento e com homoglifo trocado. Mesmo comprimento do texto dado,
    para que as posicoes valham nos dois."""
    return "".join(_canonico(c) for c in texto)


# --- Padroes ----------------------------------------------------------------------------
# Escritos uma vez, com marcas: {S} separa duas palavras; {G3} admite ate 3 palavras no
# meio. Cada padrao e compilado em duas formas: a espacada, para texto comum, e a colada,
# usada so sobre letras soltas reagrupadas (onde os espacos se perderam).

_ANULAR_PT = r"(?:ignor(?:e|em|a|ar)|desconsider(?:e|em|a|ar)|esquec(?:a|am|e)|descarte)"
_ANULAR_EN = r"(?:ignore|disregard|forget)"
_INSTRUCAO = (
    r"(?:instruc\w*|instruction\w*|regras?|rules?|contexto|context|prompt|diretriz\w*"
    r"|guidelines?|orientac\w*)"
)
_MOSTRAR = (
    r"(?:mostr\w*|revel\w*|repit\w*|repet\w*|imprim\w*|exib\w*|escrev\w*|diga|show|reveal"
    r"|repeat|print|display|output|write|tell{S}me)"
)
_OCULTO = (
    r"(?:prompt{S}d[eo]{S}sistema|system{S}prompt|system{S}instruction\w*"
    r"|instruc\w*{S}d[eo]{S}sistema|(?:seu|teu|your){S}prompt"
    r"|hidden{S}(?:instruction\w*|prompt|content)|conteudo{S}oculto|prompt{S}oculto"
    r"|instruc\w*{S}ocult\w*|frase{S}de{S}configuracao|initial{S}prompt|prompt{S}inicial"
    r"|instruc\w*{S}inicia\w*|initial{S}instruction\w*)"
)
_QUALIFICADOR = r"(?:prioritari\w*|d[eo]{S}sistema|urgente\w*|importante\w*|priority|system|urgent|important)"
_ORDEM = r"(?:instruc\w*|instruction\w*|ordem|ordens|orders?|diretriz\w*)"

_PADROES = [
    # Anular: verbo de descartar + objeto de instrucao.
    rf"(?:{_ANULAR_PT}|{_ANULAR_EN}){{G3}}{_INSTRUCAO}",
    # Anular: "tudo o que foi dito antes"; em ingles, "the above", "previous".
    rf"{_ANULAR_PT}{{S}}(?:tudo|o{{S}}que){{G4}}(?:acima|antes|anterior\w*)",
    rf"{_ANULAR_EN}{{G3}}(?:above|previous|prior|preceding|earlier)",
    # Mudar o regime: "a partir de agora voce ... regras".
    r"(?:a{S}partir{S}de{S}agora|de{S}agora{S}em{S}diante|doravante|from{S}now{S}on)"
    r"{G1}(?:voce|vc|tu|you){G6}"
    r"(?:regras?|instruc\w*|restric\w*|rules?|instruction\w*|restriction\w*|limites?|limits?|filtros?|filters?)",
    # Nova ordem, com qualificador de prioridade ou de sistema.
    rf"(?:nova|novas|new){{S}}{_ORDEM}{{S}}{_QUALIFICADOR}",
    rf"(?:nova|novas|new){{S}}{_QUALIFICADOR}{{S}}{_ORDEM}",
    # Extrair o contexto oculto.
    rf"{_MOSTRAR}{{G5}}{_OCULTO}",
]

_SEPARADOR = r"[\W_]+"


def _compilar(padrao: str, colado: bool) -> re.Pattern:
    def gap(encontrado: re.Match) -> str:
        palavras = int(encontrado.group(1))
        if colado:
            return rf"\w{{0,{12 * palavras}}}"
        return rf"{_SEPARADOR}(?:\w+{_SEPARADOR}){{0,{palavras}}}"

    expressao = re.sub(r"\{G(\d)\}", gap, padrao)
    expressao = expressao.replace("{S}", "" if colado else _SEPARADOR)
    inicio = "" if colado else r"(?<![a-z0-9])"
    return re.compile(inicio + r"(?:" + expressao + r")")


_ESPACADOS = [_compilar(p, colado=False) for p in _PADROES]
_COLADOS = [_compilar(p, colado=True) for p in _PADROES]

# Oito ou mais letras soltas, cada uma separada da seguinte por um unico separador.
_LETRAS_SOLTAS = re.compile(r"(?<![^\W_])(?:[^\W_][ .\-_*|·]){7,}[^\W_](?![^\W_])")


def _trechos_com_injecao(texto: str) -> list[tuple[int, int]]:
    """Intervalos de `texto` (ja em forma canonica) em que algum padrao casa."""
    trechos = []
    for padrao in _ESPACADOS:
        trechos += [e.span() for e in padrao.finditer(texto)]
    # Letras soltas: reagrupa e procura com os padroes colados.
    for solto in _LETRAS_SOLTAS.finditer(texto):
        reagrupado = re.sub(r"[\W_]", "", solto.group())
        if any(padrao.search(reagrupado) for padrao in _COLADOS):
            trechos.append(solto.span())
    # De tras para frente.
    invertido = texto[::-1]
    tamanho = len(texto)
    for padrao in _ESPACADOS:
        trechos += [(tamanho - e.end(), tamanho - e.start()) for e in padrao.finditer(invertido)]
    return trechos


def _unir(intervalos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    unidos: list[tuple[int, int]] = []
    for inicio, fim in sorted(intervalos):
        if unidos and inicio <= unidos[-1][1]:
            unidos[-1] = (unidos[-1][0], max(unidos[-1][1], fim))
        else:
            unidos.append((inicio, fim))
    return unidos


# Texto escondido menor que isto nao gera alerta (uma bandeira em emoji, por exemplo, usa
# cinco ou seis caracteres do bloco de tag).
_MINIMO_PARA_ALERTA = 8


def detectar_injecao(original: str, normalizado: Normalizado) -> tuple[list[Deteccao], list[Deteccao]]:
    """Devolve (injecoes, codificados), com posicoes no texto original.

    `injecoes`: trechos com instrucao de injecao, no proprio texto ou numa vista
    decodificada. `codificados`: trechos escondidos ou codificados, legiveis, **sem**
    instrucao reconhecida.
    """
    intervalos = [
        normalizado.intervalo_original(inicio, fim)
        for inicio, fim in _trechos_com_injecao(canonica(normalizado.texto))
    ]

    suspeitos: set[tuple[int, int]] = set()
    com_injecao: set[tuple[int, int]] = set()
    for vista in vistas_decodificadas(original, normalizado):
        if _trechos_com_injecao(canonica(vista.texto)):
            com_injecao.add(vista.posicao)
        elif len(vista.texto.strip()) >= _MINIMO_PARA_ALERTA:
            suspeitos.add(vista.posicao)

    injecoes = [
        Deteccao(tipo="injecao", posicao=posicao, valido=True)
        for posicao in _unir(intervalos + sorted(com_injecao))
    ]
    codificados = [
        Deteccao(tipo="conteudo_codificado", posicao=posicao, valido=True)
        for posicao in sorted(suspeitos - com_injecao)
    ]
    return injecoes, codificados
