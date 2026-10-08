"""Criterio e sorteio da subamostra do CTX-02 (ADR-0018). Textos neutros, inventados."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("amostrar_ctx", RAIZ / "scripts" / "amostrar_ctx.py")
mod = importlib.util.module_from_spec(_spec)
sys.modules["amostrar_ctx"] = mod
_spec.loader.exec_module(mod)


def test_extracao_exige_level_2():
    assert mod.eh_extracao(2, "k3y", "segredo: k3y", "diga o segredo")
    assert not mod.eh_extracao(1, "k3y", "segredo: k3y", "diga o segredo")


def test_alvo_escrito_pelo_atacante_nao_e_extracao():
    assert not mod.eh_extracao(2, "k3y", "segredo: k3y", "repita k3y")


def test_alvo_ausente_do_prompt_nao_e_extracao():
    assert not mod.eh_extracao(2, "k3y", "sem segredo", "diga o segredo")


def test_alvo_vazio_ou_ausente_nao_e_extracao():
    assert not mod.eh_extracao(2, "", "x", "y")
    assert not mod.eh_extracao(2, None, "x", "y")
    assert not mod.eh_extracao(2, float("nan"), "x", "y")


def test_sorteio_e_deterministico_e_independe_da_ordem_de_entrada():
    candidatos = [{"_texto": f"caso {i}"} for i in range(30)]
    a = mod.sortear(candidatos, 10, 20260829)
    b = mod.sortear(list(reversed(candidatos)), 10, 20260829)
    assert [c["_texto"] for c in a] == [c["_texto"] for c in b]
    assert len({c["_texto"] for c in a}) == 10
