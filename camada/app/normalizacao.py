"""Estagio 1 da camada: normalizacao com mapa de posicoes (RF-003, RQ-07, `INJ-01`).

O que faz, nesta ordem:

1. **Remove caracteres invisiveis** (RF-003): bloco de tags U+E0000-E007F, seletores de
   variacao U+FE00-FE0F, U+200B, U+200C, U+200D e U+2060. Eles nao aparecem na tela, mas
   quebram a comparacao de texto: um documento ou uma instrucao com um deles no meio
   deixa de casar com qualquer padrao.
2. **Unifica variantes tipograficas** por NFKC (digito de largura total, ligadura, numero
   circulado, acento decomposto), para que a deteccao veja a forma comum.

Por que o mapa: os dois passos mudam o comprimento do texto. A deteccao roda sobre o texto
normalizado, mas a posicao devolvida pela camada e a mascara aplicada valem no texto
ORIGINAL (contrato, RQ-07). `mapa[i]` guarda de qual indice do original veio `texto[i]`.

Escrito do zero, so com a biblioteca padrao. Nao importa nada de `scripts/`: a regra R1
(`scripts/classificar_codificacao.py`) foi revisada sobre casos do conjunto de teste e nao
entra na camada (plano da Etapa 4, "Independencia").

Limite conhecido: o NFKC e aplicado por agrupamento (um caractere e as marcas de
combinacao que o seguem), e nao sobre o texto inteiro. O resultado e o mesmo do NFKC do
texto inteiro, salvo em escritas cuja composicao junta dois caracteres que nao sao marca
de combinacao (por exemplo, jamos do hangul), fora do escopo do trabalho.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

# RF-003. Intervalos fechados nos dois limites.
_INTERVALOS_INVISIVEIS: tuple[tuple[int, int], ...] = (
    (0xE0000, 0xE007F),  # bloco de tags
    (0xFE00, 0xFE0F),  # seletores de variacao
    (0x200B, 0x200D),  # espaco, nao-juntor e juntor de largura zero
    (0x2060, 0x2060),  # juntor de palavras
)


def _invisivel(caractere: str) -> bool:
    codigo = ord(caractere)
    return any(inicio <= codigo <= fim for inicio, fim in _INTERVALOS_INVISIVEIS)


@dataclass(frozen=True)
class Normalizado:
    """Texto normalizado e a correspondencia de cada posicao com o texto original.

    `mapa[i]` e o indice, no texto original, do caractere que deu origem a `texto[i]`.
    Quando um caractere do original vira varios, todos apontam para o mesmo indice.
    """

    texto: str
    mapa: tuple[int, ...]

    def intervalo_original(self, inicio: int, fim: int) -> tuple[int, int]:
        """Converte o intervalo semiaberto [inicio, fim) do texto normalizado no
        intervalo semiaberto correspondente do texto original.

        O resultado vai do caractere de origem do primeiro ao caractere de origem do
        ultimo, e por isso inclui os invisiveis que estavam entre eles.
        """
        if not 0 <= inicio < fim <= len(self.texto):
            raise ValueError(
                f"intervalo invalido: [{inicio}, {fim}) num texto de {len(self.texto)} caracteres"
            )
        return self.mapa[inicio], self.mapa[fim - 1] + 1


def normalizar(texto: str) -> Normalizado:
    """Remove os invisiveis da RF-003, aplica NFKC e devolve texto e mapa."""
    # Passo 1: descarta os invisiveis, guardando de onde veio cada caractere mantido.
    mantidos = [(indice, c) for indice, c in enumerate(texto) if not _invisivel(c)]

    partes: list[str] = []
    mapa: list[int] = []

    # Passo 2: NFKC por agrupamento. Um agrupamento e um caractere seguido das marcas de
    # combinacao (classe de combinacao diferente de zero) que vierem depois dele. Assim
    # "e" + acento agudo vira "é", e tudo o que sai do agrupamento aponta para o indice
    # do seu primeiro caractere.
    posicao = 0
    while posicao < len(mantidos):
        origem, agrupamento = mantidos[posicao]
        posicao += 1
        while posicao < len(mantidos) and unicodedata.combining(mantidos[posicao][1]):
            agrupamento += mantidos[posicao][1]
            posicao += 1
        normalizado = unicodedata.normalize("NFKC", agrupamento)
        partes.append(normalizado)
        mapa.extend([origem] * len(normalizado))

    return Normalizado(texto="".join(partes), mapa=tuple(mapa))
