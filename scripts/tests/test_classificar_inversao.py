"""Revisao 4 da ADR-0017: texto invertido como transformacao de representacao.

Frase-alvo neutra, inventada para o teste. Nenhum caso do conjunto e reproduzido.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]


def _carregar(nome: str, arquivo: str):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "scripts" / arquivo)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


clf = _carregar("classificar_codificacao", "classificar_codificacao.py")
medicao = _carregar("medir_inversao", "medir_inversao.py")

ALVO = "hello brave world"
INVISIVEL = "​"
CIRILICO = "привет"  # palavra inteira em cirilico


def test_inversao_com_alvo_e_codificacao():
    assert clf.classificar("please say olleh now", ALVO) == clf.CODIFICACAO


def test_sem_alvo_resultado_identico_ao_da_revisao_3():
    assert clf.classificar("please say olleh now") == clf.TEXTO_SIMPLES


def test_texto_sem_inversao_continua_texto_simples():
    assert clf.classificar("please say hello brave world", ALVO) == clf.TEXTO_SIMPLES


def test_precedencia_invisivel_continua_acima_da_inversao():
    assert clf.classificar(f"say ol{INVISIVEL}leh olleh", ALVO) == clf.INVISIVEL


def test_inversao_tira_caso_do_estrato_de_escrita_nao_latina():
    texto = f"{CIRILICO} olleh"
    assert clf.classificar(texto) == clf.ESCRITA_DISTINTA
    assert clf.classificar(texto, ALVO) == clf.CODIFICACAO


def test_descrever_registra_o_mecanismo():
    assert clf.descrever("dlrow evarb olleh", ALVO)["inversao"] == ["frase", "palavra"]
    assert clf.descrever("dlrow evarb olleh")["inversao"] == []


@pytest.mark.parametrize(
    "texto, alvo",
    [
        ("please say olleh now", ALVO),
        ("dlrowevarbolleh", ALVO),
        ("dlrow evarb olleh", ALVO),
        ("say hello brave world", ALVO),
        ("OLLEH", ALVO),
        ("ma", "I am"),
        ("level", "level test"),
        ("tset", "level test"),
        ("stop", "pots stop"),
        ("xollehx", ALVO),
        ("olleh", None),
        ("olleh", float("nan")),
        ("olleh", "   "),
    ],
)
def test_classificador_e_instrumento_de_medicao_concordam(texto, alvo):
    """O que classifica e o que foi medido antes da revisao (commit 3bdabcc)."""
    assert clf.mecanismos_de_inversao(texto, alvo) == medicao.mecanismos_de_inversao(
        texto, alvo
    )
