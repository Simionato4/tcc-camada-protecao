"""Contrato da camada (Etapa 4, Fase 0; ADR-0027). Sem regra: so limites e forma."""

import uuid

from fastapi.testclient import TestClient

from camada.app.contrato import TAMANHO_MAXIMO_TEXTO, Deteccao
from camada.app.main import app

cliente = TestClient(app)


def _post(texto: str, id_requisicao: str | None = None):
    return cliente.post(
        "/entrada",
        json={
            "ponto": "entrada",
            "texto": texto,
            "id_requisicao": id_requisicao or str(uuid.uuid4()),
            "condicao": "B",
        },
    )


def test_texto_no_limite_e_aceito():
    assert _post("a" * TAMANHO_MAXIMO_TEXTO).status_code == 200


def test_texto_acima_do_limite_e_recusado_sem_encaminhar():
    resposta = _post("a" * (TAMANHO_MAXIMO_TEXTO + 1))
    assert resposta.status_code == 422


def test_limite_e_o_decidido_na_adr_0027():
    assert TAMANHO_MAXIMO_TEXTO == 20_000


def test_identificador_fora_do_formato_uuid_e_recusado():
    assert _post("ok", id_requisicao="verificacao").status_code == 422
    assert _post("ok", id_requisicao="1234").status_code == 422


def test_posicao_da_deteccao_e_declarada_no_texto_original():
    """RQ-07: o contrato fixa o sistema de coordenadas; o teste de comportamento vem com
    a normalizacao (Fase 1, T010), que e quem produz o mapa de posicoes."""
    doc = Deteccao.__doc__ or ""
    assert "texto ORIGINAL" in doc
    assert "JA NORMALIZADO" not in doc


def test_resposta_sem_erro_tem_campo_erro_vazio():
    assert _post("ok").json()["erro"] is None
