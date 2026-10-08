"""RQ-03: suporte da validate-docbr 2.0.0 ao CNPJ numerico e alfanumerico.

O teste nao confia na biblioteca para decidir o que e valido. Implementa a regra de
calculo publicada pela Receita Federal (Perguntas e Respostas sobre o CNPJ alfanumerico,
pergunta 14, consultada em 08/10/2026; ADR-0015) e confere que a biblioteca concorda.

A regra publicada: cada caractere vale o seu codigo ASCII menos 48 (digitos 0 a 9, letras
A=17 a Z=42); modulo 11 com pesos 5,4,3,2,9,8,7,6,5,4,3,2 para o primeiro DV e
6,5,4,3,2,9,8,7,6,5,4,3,2 para o segundo; DV = 11 - resto.

LIMITE DECLARADO: o documento oficial nao diz o que ocorre quando o resto e 0 ou 1.
Os casos deste teste tem resto 2 ou maior nos dois calculos; o comportamento da
biblioteca para resto 0 ou 1 nao e verificado aqui (pendencia na ADR-0015).
"""

from __future__ import annotations

import random
import string

import pytest
from validate_docbr import CNPJ

PESOS_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
PESOS_2 = [6] + PESOS_1


def _resto(base: str, pesos: list[int]) -> int:
    return sum((ord(c) - 48) * p for c, p in zip(base, pesos)) % 11


def cnpj_oficial(base12: str) -> str | None:
    """CNPJ completo pela regra publicada, ou None se algum resto for 0 ou 1."""
    r1 = _resto(base12, PESOS_1)
    if r1 < 2:
        return None
    parcial = base12 + str(11 - r1)
    r2 = _resto(parcial, PESOS_2)
    if r2 < 2:
        return None
    return parcial + str(11 - r2)


def test_exemplo_publicado_pela_receita_federal():
    assert cnpj_oficial("12ABC34501DE") == "12ABC34501DE35"
    assert CNPJ().validate("12.ABC.345/01DE-35")
    assert CNPJ().validate("12ABC34501DE35")


def test_exemplo_com_dv_errado_e_recusado():
    assert not CNPJ().validate("12ABC34501DE36")
    assert not CNPJ().validate("12ABC34501DE53")


def test_cnpj_numerico_continua_valido():
    numero = cnpj_oficial("112223330001")
    assert numero == "11222333000181"
    assert CNPJ().validate(numero)


@pytest.mark.parametrize("alfabeto", [string.digits, string.ascii_uppercase + string.digits])
def test_biblioteca_concorda_com_a_regra_publicada(alfabeto):
    sorteio = random.Random(20260829)
    conferidos = 0
    while conferidos < 200:
        base = "".join(sorteio.choice(alfabeto) for _ in range(12))
        numero = cnpj_oficial(base)
        if numero is None:
            continue
        assert CNPJ().validate(numero), numero
        errado = numero[:-1] + str((int(numero[-1]) + 1) % 10)
        assert not CNPJ().validate(errado), errado
        conferidos += 1
