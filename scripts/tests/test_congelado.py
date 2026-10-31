"""Principio I da constituicao, verificavel.

Antes do congelamento: os modulos de regra nao existem. Depois: todo hash registrado em
`conjunto_teste/CONGELADO.md` confere com o arquivo atual, e a data do congelamento
precede a criacao dos modulos de regra.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("congelar", RAIZ / "scripts" / "congelar.py")
congelar = importlib.util.module_from_spec(_spec)
sys.modules["congelar"] = congelar
_spec.loader.exec_module(congelar)
CONGELADO = RAIZ / "conjunto_teste" / "CONGELADO.md"
MODULOS = ("normalizacao.py", "deteccao.py", "decisao.py")


def _existem_modulos() -> list[str]:
    return congelar.modulos_de_regra()


def test_sem_congelamento_nao_ha_modulo_de_regra():
    if not CONGELADO.exists():
        assert _existem_modulos() == []


def test_hashes_do_congelamento_conferem():
    if not CONGELADO.exists():
        return
    texto = CONGELADO.read_text(encoding="utf-8")
    linhas = re.findall(r"^\| `([^`]+)` \| [^|]+ \| `([0-9a-f]{64})` \|$", texto, re.M)
    assert linhas, "nenhum arquivo listado no CONGELADO.md"
    for caminho, esperado in linhas:
        assert congelar.hash_registrado(caminho) == esperado, f"{caminho} mudou depois do congelamento"


def test_previa_lista_todo_arquivo_congelado_com_hash_conferivel():
    """A pre-visualizacao gera uma linha com hash para cada item, e cada uma confere."""
    linhas = re.findall(r"^\| `([^`]+)` \| [^|]+ \| `([0-9a-f]{64})` \|$", congelar.conteudo(), re.M)
    assert len(linhas) == len(congelar.CONGELADOS) + 1
    for caminho, esperado in linhas:
        assert congelar.hash_registrado(caminho) == esperado


def test_secoes_fechadas_do_protocolo():
    texto = congelar.secoes_fechadas(RAIZ / "docs" / "protocolo.md")
    titulos = re.findall(r"^## (\d)\.", texto, re.M)
    assert titulos == ["1", "2", "3", "8"]
