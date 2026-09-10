"""Testes do esqueleto da camada.

O teste que importa aqui e o de invariancia: enquanto nao houver regra, nenhum
texto pode ser alterado. Quando as regras chegarem, este teste continua valendo
para a condicao A, e e a garantia mecanica de que a condicao sem protecao
realmente nao protege nada.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from camada.app.main import app

cliente = TestClient(app)

TEXTOS = [
    "Qual o prazo de entrega do pedido 10482?",
    "Meu CPF e 529.982.247-25 e quero cancelar a compra.",
    "   texto   com   espacos   e \n quebras \t de linha  ",
    "",
    "emoji e acentos: cancelamento urgente ção \U0001f600",
]


@pytest.mark.parametrize("ponto", ["entrada", "contexto", "saida"])
@pytest.mark.parametrize("texto", TEXTOS)
def test_encaminha_sem_alterar_o_texto(ponto: str, texto: str) -> None:
    resposta = cliente.post(
        f"/{ponto}",
        json={
            "ponto": ponto,
            "texto": texto,
            "id_requisicao": str(uuid.uuid4()),
            "condicao": "A",
        },
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == texto
    assert corpo["deteccoes"] == []


@pytest.mark.parametrize("condicao", ["A", "B", "C", "D"])
def test_contrato_completo_em_todas_as_condicoes(condicao: str) -> None:
    resposta = cliente.post(
        "/entrada",
        json={
            "ponto": "entrada",
            "texto": "teste",
            "id_requisicao": str(uuid.uuid4()),
            "condicao": condicao,
        },
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {
        "decisao",
        "texto",
        "deteccoes",
        "tempo_ms",
        "versao_regras",
        "ponto",
        "condicao",
    }
    assert corpo["tempo_ms"] >= 0
    assert corpo["condicao"] == condicao


def test_ponto_invalido_e_rejeitado() -> None:
    resposta = cliente.post(
        "/entrada",
        json={
            "ponto": "inexistente",
            "texto": "teste",
            "id_requisicao": str(uuid.uuid4()),
            "condicao": "A",
        },
    )
    assert resposta.status_code == 422


def test_saude_responde() -> None:
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json()["estado"] == "ok"
