"""Mensagens legitimas (tarefa 3.8, ADR-0023): o JSONL corresponde ao texto redigido e
o verificador acusa cada regra objetiva do guia."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("gerar_legitimas", RAIZ / "scripts" / "gerar_legitimas.py")
g = importlib.util.module_from_spec(_spec)
sys.modules["gerar_legitimas"] = g
_spec.loader.exec_module(g)


def _jsonl():
    return [json.loads(l) for l in g.SAIDA.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_jsonl_e_exatamente_o_texto_redigido():
    assert _jsonl() == g.registros(g.ler())


def test_cem_mensagens_em_cinco_blocos_de_vinte():
    registros = _jsonl()
    assert len(registros) == 100
    assert [r["id"] for r in registros] == [f"leg-{i:03d}" for i in range(1, 101)]
    for b in range(1, 6):
        assert sum(r["bloco"] == b for r in registros) == 20


def test_texto_versionado_passa_nas_regras_do_guia():
    assert g.problemas(g.ler()) == []


def _uma(texto: str, numero: int = 1) -> list[dict]:
    return [{"numero": numero, "bloco": 1, "nome_bloco": "x", "texto": texto}]


def _acusa(texto: str) -> bool:
    return any(e.startswith("1:") for e in g.problemas(_uma(texto)))


def test_verificador_acusa_documento_valido():
    assert _acusa("meu cpf e 123.456.789-09")
    assert _acusa("cnpj 11.222.333/0001-81 da empresa")


def test_verificador_acusa_dez_digitos_ou_mais():
    assert _acusa("o protocolo e 1234567890")


def test_verificador_acusa_email_e_celular():
    assert _acusa("manda para fulano@example.com")
    assert _acusa("liga no (46) 99123-4567")


def test_verificador_acusa_pedido_fora_da_base():
    assert _acusa("cade o pedido 10031")


def test_verificador_aceita_numeros_do_dia_a_dia():
    for texto in (
        "o rastreio AE101877898BR parou",
        "frete para 85501-000 ficou R$ 29,90",
        "coleta dia 22/11 das 8h as 12h no pedido 10015",
        "paguei R$ 1.539,48 em 10x",
    ):
        assert not _acusa(texto), texto


def test_verificador_acusa_repeticao():
    duas = _uma("onde esta meu pedido") + _uma("Onde  esta meu pedido", 2)
    assert any("repete" in e for e in g.problemas(duas))
