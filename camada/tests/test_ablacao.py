"""Ablacao da normalizacao (Etapa 4, T012; RF-012, RQ-12; cenario 3 da Historia 2).

Desligar o estagio de normalizacao nao pode mudar mais nada na camada. Enquanto nao ha
deteccao, isso significa: a resposta e a mesma com o estagio ligado e desligado, salvo o
tempo. Quando a deteccao existir, este arquivo ganha o caso em que o resultado difere so
por causa da normalizacao.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from camada.app import main
from camada.app.normalizacao import normalizar

cliente = TestClient(main.app)

TEXTO_COM_INVISIVEL = "pe\u200Bdido \uFF11\uFF10 con\uFB01rmado"


def test_estagio_desligado_devolve_o_texto_e_o_mapa_identidade() -> None:
    resultado = normalizar(TEXTO_COM_INVISIVEL, ativa=False)
    assert resultado.texto == TEXTO_COM_INVISIVEL
    assert resultado.mapa == tuple(range(len(TEXTO_COM_INVISIVEL)))
    assert resultado.intervalo_original(2, 5) == (2, 5)


def test_estagio_ligado_e_o_padrao() -> None:
    assert normalizar(TEXTO_COM_INVISIVEL) == normalizar(TEXTO_COM_INVISIVEL, ativa=True)
    assert normalizar(TEXTO_COM_INVISIVEL).texto == "pedido 10 confirmado"


@pytest.mark.parametrize("valor,esperado", [("ligada", True), ("desligada", False)])
def test_configuracao_aceita(valor: str, esperado: bool) -> None:
    assert main.ler_normalizacao(valor) is esperado


@pytest.mark.parametrize("valor", ["", "sim", "LIGADA", "0", "false"])
def test_configuracao_desconhecida_impede_a_camada_de_subir(valor: str) -> None:
    with pytest.raises(ValueError):
        main.ler_normalizacao(valor)


def _resposta(ponto: str, id_requisicao: str) -> dict:
    corpo = cliente.post(
        f"/{ponto}",
        json={
            "ponto": ponto,
            "texto": TEXTO_COM_INVISIVEL,
            "id_requisicao": id_requisicao,
            "condicao": "B",
        },
    ).json()
    corpo.pop("tempo_ms")
    return corpo


@pytest.mark.parametrize("ponto", ["entrada", "contexto", "saida"])
def test_desligar_a_normalizacao_nao_muda_o_resto(ponto: str, monkeypatch) -> None:
    id_requisicao = str(uuid.uuid4())
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", True)
    ligada = _resposta(ponto, id_requisicao)
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", False)
    desligada = _resposta(ponto, id_requisicao)
    assert ligada == desligada
    assert ligada["texto"] == TEXTO_COM_INVISIVEL  # encaminha o original


def test_saude_informa_o_estado_do_estagio(monkeypatch) -> None:
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", True)
    assert cliente.get("/saude").json()["normalizacao"] == "ligada"
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", False)
    assert cliente.get("/saude").json()["normalizacao"] == "desligada"
