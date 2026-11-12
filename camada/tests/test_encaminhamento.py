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
        "erro",
    }
    assert corpo["erro"] is None
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


def test_versao_das_regras_e_constante_do_codigo() -> None:
    """A versao nao vem do ambiente: as regras sao o codigo, e um rotulo configuravel por
    fora poderia informar uma versao que nao e a que roda (Etapa 4, T025)."""
    import inspect

    from camada.app import main

    assert main.VERSAO_REGRAS == "0.1.0"
    assert 'getenv("VERSAO_REGRAS"' not in inspect.getsource(main)
    assert cliente.get("/saude").json()["versao_regras"] == "0.1.0"
