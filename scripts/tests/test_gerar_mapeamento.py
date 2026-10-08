"""Funcoes puras do gerador de mapeamento (ADR-0018). Nao le os conjuntos."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("gerar_mapeamento", RAIZ / "scripts" / "gerar_mapeamento.py")
mod = importlib.util.module_from_spec(_spec)
sys.modules["gerar_mapeamento"] = mod
_spec.loader.exec_module(mod)


def test_eixo_vazamento_das_duas_categorias():
    assert mod.eixo_vazamento(
        "Information Hazards",
        "Risks from leaking or inferring sensitive information (organization/gov)",
    ) == "organizacao_governo"
    assert mod.eixo_vazamento(
        "Information Hazards",
        "Compromise privacy by leaking or inferring private information (person/individual)",
    ) == "privacidade_individuo"


def test_fora_da_area_de_vazamento_nao_ha_eixo():
    assert mod.eixo_vazamento("Malicious Uses", "Assisting illegal activities") is None


def test_rotulo_desconhecido_na_area_falha_em_vez_de_silenciar():
    with pytest.raises(KeyError):
        mod.eixo_vazamento("Information Hazards", "categoria inventada")


def test_slug():
    assert mod.slug("Marketing & Advertising") == "marketing-advertising"
    assert mod.slug("Scams & Fraud") == "scams-fraud"
