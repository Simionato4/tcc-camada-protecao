"""Recuperacao pareada com embeddings degenerados (ADR-0012).

O modelo de embeddings e substituido por um que devolve **o mesmo vetor para
qualquer texto**. Isso reproduz, no pior caso possivel, a falha medida em
10/09/2026: com 30 documentos de estrutura quase identica, o vetor da pergunta
praticamente nao depende dela, e a busca densa devolveu sempre os mesmos tres
documentos, acertando 3 de 30.

Se o alvo for recuperado mesmo assim, a garantia do pareamento nao depende da
qualidade dos embeddings — que e exatamente o que o ADR-0012 afirma. Um teste com o
modelo real seria mais fraco: passaria por sorte de ranking.
"""

import json
from pathlib import Path

import pytest

qdrant_client = pytest.importorskip("qdrant_client")

from recuperador.app.indexar import indexar, verificar_recuperacao  # noqa: E402
from recuperador.app.indice import (  # noqa: E402
    DIMENSOES,
    IndiceQdrant,
    carregar_documentos,
)

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "base_conhecimento"


class ModeloDegenerado:
    """Devolve sempre o mesmo vetor, para qualquer entrada."""

    def embed(self, textos):
        import numpy as np

        for _ in textos:
            yield np.ones(DIMENSOES, dtype="float32")


@pytest.fixture(scope="module")
def indice():
    from recuperador.app import indexar as modulo

    modulo.BASE = BASE
    indice = IndiceQdrant(
        cliente=qdrant_client.QdrantClient(":memory:"), modelo=ModeloDegenerado()
    )
    indexar(indice, carregar_documentos(BASE))
    return indice


def test_todas_as_perguntas_pareadas_recuperam_o_alvo(indice) -> None:
    """Evidencia de conclusao da tarefa 2.5."""
    documentos = carregar_documentos(BASE)
    resultados = verificar_recuperacao(indice, documentos, k=3)
    falhas = [r for r in resultados if not r["no_top_k"]]
    assert not falhas, json.dumps(falhas, ensure_ascii=False, indent=2)
    assert len(resultados) == 30


def test_alvo_vem_sempre_em_primeira_posicao(indice) -> None:
    """O filtro exato precede a similaridade, entao a posicao e determinada."""
    documentos = carregar_documentos(BASE)
    resultados = verificar_recuperacao(indice, documentos, k=3)
    assert all(r["posicao"] == 1 for r in resultados)


def test_contexto_mantem_sempre_k_documentos(indice) -> None:
    """O ADR-0007 fixa k=3 como variavel de controle. O filtro traz um documento;
    as duas vagas restantes sao preenchidas por similaridade.
    """
    for k in (1, 2, 3, 5):
        achados = indice.buscar("Qual o status do pedido 10007?", k)
        assert len(achados) == k
        ids = [a.id_documento for a in achados]
        assert len(set(ids)) == k, "documento repetido no contexto"


def test_pergunta_sem_numero_de_pedido_usa_apenas_similaridade(indice) -> None:
    achados = indice.buscar("Qual a politica de troca da loja?", 3)
    assert len(achados) == 3


def test_pedido_inexistente_nao_quebra_a_busca(indice) -> None:
    """Caso que ocorrera com mensagens legitimas e de ataque que citam pedidos
    fictícios. Deve degradar para similaridade, e nao falhar.
    """
    achados = indice.buscar("Qual o status do pedido 99999?", 3)
    assert len(achados) == 3
