"""Teste de integracao do indice: embeddings reais sobre Qdrant em memoria.

Marcado como `lento` porque baixa o modelo de embeddings (1 GB) na primeira
execucao. Roda com:

    pytest -m lento

O que ele prova, e que nenhum teste de contrato prova: que a recuperacao pareada do
ADR-0002 funciona de fato — cada pergunta que cita um numero de pedido traz o seu
documento no top-3, com o modelo e a metrica de distancia realmente configurados.
"""

import json
from pathlib import Path

import pytest

from recuperador.app.indexar import indexar, verificar_recuperacao
from recuperador.app.indice import IndiceQdrant, carregar_documentos, hash_do_estado

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "base_conhecimento"

pytestmark = pytest.mark.lento


@pytest.fixture(scope="module")
def indice_carregado(monkeypatch_module=None):
    qdrant_client = pytest.importorskip("qdrant_client")
    pytest.importorskip("fastembed")
    from fastembed import TextEmbedding

    from recuperador.app import indexar as modulo_indexar
    from recuperador.app.indice import MODELO_EMBEDDINGS

    modulo_indexar.BASE = BASE
    try:
        modelo = TextEmbedding(model_name=MODELO_EMBEDDINGS)
    except Exception as erro:  # noqa: BLE001
        pytest.skip(
            f"modelo de embeddings indisponivel nesta maquina ({erro}). "
            "A verificacao canonica roda no conteiner: "
            "docker compose exec recuperador python -m app.indexar"
        )
    indice = IndiceQdrant(
        cliente=qdrant_client.QdrantClient(":memory:"), modelo=modelo
    )
    documentos = carregar_documentos(BASE)
    indexar(indice, documentos)
    return indice, documentos


def test_vetor_tem_a_dimensao_declarada(indice_carregado) -> None:
    indice, _ = indice_carregado
    from recuperador.app.indice import DIMENSOES

    assert len(indice.vetorizar("teste de dimensao")) == DIMENSOES


def test_toda_pergunta_pareada_recupera_seu_documento(indice_carregado) -> None:
    """Evidencia de conclusao da tarefa 2.5 e base empirica do ADR-0002."""
    indice, documentos = indice_carregado
    resultados = verificar_recuperacao(indice, documentos, k=3)
    falhas = [r for r in resultados if not r["no_top_k"]]
    assert not falhas, json.dumps(falhas, ensure_ascii=False, indent=2)
    assert len(resultados) == 30


def test_pergunta_pareada_traz_o_alvo_em_primeiro_lugar(indice_carregado) -> None:
    """Mais forte que o anterior, e o que se espera quando a pergunta cita o numero
    do pedido. Se falhar, o pareamento ainda vale, mas convem saber.
    """
    indice, documentos = indice_carregado
    resultados = verificar_recuperacao(indice, documentos, k=3)
    fora_do_primeiro = [r["id_documento"] for r in resultados if r["posicao"] != 1]
    assert not fora_do_primeiro, fora_do_primeiro


def test_hash_do_estado_muda_com_o_conteudo() -> None:
    """RQ-18: o hash precisa distinguir a base limpa da base contaminada."""
    documentos = carregar_documentos(BASE)
    original = hash_do_estado(documentos)
    contaminado = [dict(d) for d in documentos]
    contaminado[0]["texto"] += "\n[CARGA DE INJECAO INDIRETA]"
    assert hash_do_estado(contaminado) != original
    assert hash_do_estado(documentos) == original
