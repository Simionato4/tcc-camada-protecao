"""O registro de procedencia versionado e exatamente o que o script gera.

Existe por causa de uma divergencia real: a licenca do BIPIA foi reconciliada em
17/09/2026 editando o ORIGEM.md a mao, enquanto o script e o origem.json continuavam
com "confirmar no arquivo LICENSE"; rodar o script de novo apagaria a reconciliacao
(corrigido em 31/10/2026). Le so os arquivos versionados; nao baixa nada.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("obter_conjuntos", RAIZ / "scripts" / "obter_conjuntos.py")
o = importlib.util.module_from_spec(_spec)
sys.modules["obter_conjuntos"] = o
_spec.loader.exec_module(o)

ORIGEM_JSON = RAIZ / "conjunto_teste" / "origem.json"
ORIGEM_MD = RAIZ / "conjunto_teste" / "ORIGEM.md"


def _ler(caminho: Path) -> str:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return arquivo.read()


def test_registro_versionado_e_o_que_o_script_gera():
    inventarios = json.loads(_ler(ORIGEM_JSON))
    texto_json, texto_md = o.renderizar_registro(inventarios)
    assert texto_json == _ler(ORIGEM_JSON)
    assert texto_md == _ler(ORIGEM_MD)


def test_licencas_iguais_no_script_e_no_registro():
    no_script = {c["nome"]: c["licenca"] for c in o.CONJUNTOS_HF + [o.CONJUNTO_GIT]}
    no_registro = {i["nome"]: i["licenca"] for i in json.loads(_ler(ORIGEM_JSON))}
    assert no_script == no_registro
    assert all("confirmar" not in v.lower() for v in no_registro.values())
