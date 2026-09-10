"""Testes do esqueleto do recuperador.

O que importa aqui e o contrato, nao o conteudo: o fluxo do assistente sera montado
sobre ele antes de existir busca de verdade, entao qualquer mudanca de formato
quebraria o fluxo depois.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from recuperador.app.indice import IndiceFalso
from recuperador.app.main import app, obter_indice

# O contrato e testado contra o indice falso: um teste de contrato nao deve exigir
# que haja um Qdrant de pe, nem baixar 1 GB de modelo.
app.dependency_overrides[obter_indice] = IndiceFalso

cliente = TestClient(app)


def requisicao(**extra) -> dict:
    corpo = {"pergunta": "Qual o status do pedido 10001?", "id_requisicao": str(uuid.uuid4())}
    corpo.update(extra)
    return corpo


@pytest.mark.parametrize("k", [1, 2, 3, 5])
def test_devolve_exatamente_k_documentos(k: int) -> None:
    resposta = cliente.post("/buscar", json=requisicao(k=k))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["documentos"]) == k
    assert corpo["k"] == k
    assert len(corpo["ids_recuperados"]) == k


def test_k_padrao_e_tres() -> None:
    """k=3 e o valor fixado no ADR-0007 e nao deve depender de quem chama."""
    corpo = cliente.post("/buscar", json=requisicao()).json()
    assert corpo["k"] == 3


def test_ids_recuperados_correspondem_aos_documentos() -> None:
    """O ADR-0002 exige registrar o top-k para marcar casos invalidos.

    Se esses dois campos divergirem, o executor marcaria como invalido um caso
    valido, ou o contrario.
    """
    corpo = cliente.post("/buscar", json=requisicao()).json()
    assert corpo["ids_recuperados"] == [d["id_documento"] for d in corpo["documentos"]]


def test_todo_documento_tem_numero_de_pedido_unico() -> None:
    """O pareamento pergunta-documento do ADR-0002 depende disso."""
    corpo = cliente.post("/buscar", json=requisicao()).json()
    numeros = [d["numero_pedido"] for d in corpo["documentos"]]
    assert len(numeros) == len(set(numeros))


def test_contrato_completo() -> None:
    corpo = cliente.post("/buscar", json=requisicao()).json()
    assert set(corpo) == {"documentos", "k", "tempo_ms", "versao_indice", "ids_recuperados"}
    assert corpo["tempo_ms"] >= 0
    assert set(corpo["documentos"][0]) == {"id_documento", "numero_pedido", "texto", "escore"}


@pytest.mark.parametrize("k", [0, 11, -1])
def test_k_fora_do_intervalo_e_rejeitado(k: int) -> None:
    assert cliente.post("/buscar", json=requisicao(k=k)).status_code == 422


def test_saude_responde() -> None:
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json()["estado"] == "ok"
