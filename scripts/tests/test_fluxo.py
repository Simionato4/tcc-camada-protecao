"""Fluxo do assistente (variavel de controle): desvio por decisao de bloquear (RF-013).

Depois de cada um dos tres pontos da camada, o fluxo testa `decisao == 'bloquear'`; se
verdadeiro, responde com a mensagem de bloqueio e nao segue adiante (o modelo nao e
chamado depois de bloqueio na entrada ou no contexto). Confere a estrutura do JSON
exportado; o comportamento e conferido no n8n (assistente/README.md).
"""

from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FLUXO = json.loads((RAIZ / "assistente" / "fluxo.json").read_text(encoding="utf-8"))
NOS = {n["name"]: n for n in FLUXO["nodes"]}
LIGACOES = FLUXO["connections"]


def _saidas(no: str) -> list[list[str]]:
    return [[d["node"] for d in saida] for saida in LIGACOES.get(no, {}).get("main", [])]


def _testa_bloqueio(no: str) -> bool:
    if NOS[no]["type"] != "n8n-nodes-base.if":
        return False
    cond = NOS[no]["parameters"]["conditions"]["conditions"]
    return any(c["leftValue"] == "={{ $json.decisao }}" and c["rightValue"] == "bloquear" for c in cond)


def test_cada_ponto_da_camada_tem_desvio_por_bloqueio():
    seguinte = {
        "Camada - entrada": "Recuperador - buscar",
        "Camada - contexto": "Modelo",
        "Camada - saida": "Responder",
    }
    for camada, normal in seguinte.items():
        [[se]] = _saidas(camada)
        assert _testa_bloqueio(se), camada
        verdadeiro, falso = _saidas(se)
        assert verdadeiro == ["Responder bloqueio"], camada
        assert falso == [normal], camada


def test_resposta_de_bloqueio_e_resposta_ao_webhook_com_o_ponto():
    no = NOS["Responder bloqueio"]
    assert no["type"] == "n8n-nodes-base.respondToWebhook"
    corpo = no["parameters"]["responseBody"]
    assert "decisao: 'bloquear'" in corpo and "ponto_bloqueio" in corpo


def test_modelo_so_e_alcancado_pelo_ramo_sem_bloqueio():
    origens = [o for o, l in LIGACOES.items() for saida in l["main"] for d in saida if d["node"] == "Modelo"]
    assert origens == ["Bloqueado no contexto?"]
