"""Testes do criterio de inversao (ADR-0017, bloco de 08/10/2026).

Frase-alvo neutra, inventada para o teste: o que se testa e a transformacao, nao o
conteudo de ataque. Nenhum caso do conjunto e reproduzido.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "medir_inversao", RAIZ / "scripts" / "medir_inversao.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules["medir_inversao"] = mod
_spec.loader.exec_module(mod)

ALVO = "hello brave world"


def test_palavra_alvo_invertida_e_detectada():
    assert mod.mecanismos_de_inversao("please say olleh now", ALVO) == {"palavra"}


def test_frase_alvo_inteira_invertida_sem_espacos_e_detectada():
    assert "frase" in mod.mecanismos_de_inversao("dlrowevarbolleh", ALVO)


def test_frase_alvo_invertida_com_espacos_e_detectada_pelos_dois_mecanismos():
    assert mod.mecanismos_de_inversao("dlrow evarb olleh", ALVO) == {"palavra", "frase"}


def test_controle_negativo_frase_alvo_na_ordem_normal():
    assert mod.mecanismos_de_inversao("say hello brave world", ALVO) == set()


def test_caixa_e_variante_tipografica_nao_escondem_a_inversao():
    assert mod.mecanismos_de_inversao("OLLEH", ALVO) == {"palavra"}
    largura_cheia = "".join(chr(0xFF41 + ord(c) - ord("a")) for c in "olleh")
    assert mod.mecanismos_de_inversao(largura_cheia, ALVO) == {"palavra"}


def test_palavra_curta_nao_conta():
    # "am" tem menos de MINIMO_PALAVRA letras; "ma" nao e detectado.
    assert mod.mecanismos_de_inversao("ma", "I am") == set()


def test_palindromo_nao_conta():
    # "level" invertido e "level": a presenca da palavra nao e inversao.
    assert mod.mecanismos_de_inversao("level", "level test") == set()
    assert mod.mecanismos_de_inversao("tset", "level test") == {"palavra"}


def test_inversao_que_coincide_com_outra_palavra_alvo_nao_conta():
    assert mod.mecanismos_de_inversao("stop", "pots stop") == set()


def test_inversao_dentro_de_palavra_maior_nao_conta_como_palavra():
    assert mod.mecanismos_de_inversao("xollehx", ALVO) == set()


def test_sem_alvo_nao_detecta():
    assert mod.mecanismos_de_inversao("olleh", None) == set()
    assert mod.mecanismos_de_inversao("olleh", float("nan")) == set()
    assert mod.mecanismos_de_inversao("olleh", "   ") == set()


def test_limiar_em_aritmetica_inteira():
    assert mod.limiar(18439) == 922
    assert mod.limiar(1185) == 60
    assert mod.limiar(112) == 6
    assert mod.limiar(67) == 4
    assert mod.limiar(100) == 5
