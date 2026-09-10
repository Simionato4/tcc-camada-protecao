"""Indice vetorial da base de conhecimento.

O modelo de embeddings e `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
(ADR-0011), executado localmente em CPU, sem chamada a servico externo.

Duas implementacoes de indice, com a mesma interface:

- `IndiceQdrant` — a real, usada pelos conteineres.
- `IndiceFalso` — devolve documentos fixos, usada nos testes de contrato e enquanto
  a base nao existir. Manter as duas atras da mesma interface evita que o teste do
  contrato dependa de haver um Qdrant de pe.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

MODELO_EMBEDDINGS = os.getenv(
    "MODELO_EMBEDDINGS", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
DIMENSOES = 768
COLECAO = os.getenv("COLECAO_QDRANT", "base_conhecimento")
CACHE_MODELOS = os.getenv("CACHE_MODELOS", "/opt/modelos")


# Reconhece o numero do pedido citado na pergunta. Exige a palavra "pedido" por
# perto: sem isso, CEP, telefone e valor monetario seriam confundidos com numero de
# pedido, e o filtro passaria a recuperar o documento errado com confianca.
PADRAO_PEDIDO = re.compile(r"pedido\s*(?:n[o\u00ba\u00b0]?\.?\s*)?(\d{4,8})", re.IGNORECASE)


def extrair_numero_pedido(pergunta: str) -> str | None:
    achado = PADRAO_PEDIDO.search(pergunta)
    return achado.group(1) if achado else None


@dataclass
class Achado:
    id_documento: str
    numero_pedido: str
    texto: str
    escore: float


class Indice(Protocol):
    def buscar(self, pergunta: str, k: int) -> list[Achado]: ...


class IndiceFalso:
    """Documentos fixos, com a mesma forma dos reais."""

    def __init__(self) -> None:
        self.documentos = [
            Achado(f"doc-stub-{i:03d}", str(10000 + i), f"Pedido {10000 + i}. Documento de teste.", 0.0)
            for i in range(1, 6)
        ]

    def buscar(self, pergunta: str, k: int) -> list[Achado]:
        return self.documentos[:k]


class IndiceQdrant:
    """Vetoriza a pergunta e consulta o Qdrant.

    O modelo e carregado uma unica vez, na construcao. Carrega-lo por requisicao
    acrescentaria segundos a cada chamada e distorceria qualquer medicao de tempo.
    """

    def __init__(self, url: str | None = None, cliente=None, modelo=None) -> None:
        """As dependencias pesadas so sao importadas quando realmente usadas.

        Importar `fastembed` no construtor exigiria a biblioteca ate quando o modelo
        e injetado — e o teste de recuperacao pareada injeta um modelo degenerado
        justamente para nao depender dela. Dependencia carregada por habito e
        dependencia que aparece onde nao deveria.
        """
        if cliente is None:
            from qdrant_client import QdrantClient

            cliente = QdrantClient(url=url or os.getenv("QDRANT_URL", "http://qdrant:6333"))
        self.cliente = cliente

        if modelo is None:
            from fastembed import TextEmbedding

            modelo = TextEmbedding(model_name=MODELO_EMBEDDINGS, cache_dir=CACHE_MODELOS)
        self.modelo = modelo

    def vetorizar(self, texto: str) -> list[float]:
        return next(iter(self.modelo.embed([texto]))).tolist()

    @staticmethod
    def _para_achado(ponto) -> Achado:
        return Achado(
            id_documento=ponto.payload["id_documento"],
            numero_pedido=ponto.payload["numero_pedido"],
            texto=ponto.payload["texto"],
            escore=float(ponto.score),
        )

    def _por_numero_pedido(self, numero: str, vetor: list[float]) -> list[Achado]:
        from qdrant_client import models

        resultado = self.cliente.query_points(
            collection_name=COLECAO,
            query=vetor,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="numero_pedido", match=models.MatchValue(value=numero)
                    )
                ]
            ),
            limit=1,
            with_payload=True,
        )
        return [self._para_achado(p) for p in resultado.points]

    def _por_similaridade(self, vetor: list[float], limite: int, excluir: set[str]) -> list[Achado]:
        resultado = self.cliente.query_points(
            collection_name=COLECAO,
            query=vetor,
            limit=limite + len(excluir),
            with_payload=True,
        )
        achados = [self._para_achado(p) for p in resultado.points]
        return [a for a in achados if a.id_documento not in excluir][:limite]

    def buscar(self, pergunta: str, k: int) -> list[Achado]:
        """Recuperacao em dois estagios: filtro exato mais similaridade (ADR-0012).

        Se a pergunta cita um numero de pedido, o documento correspondente e trazido
        por **filtro exato sobre o campo**, e nao por similaridade. As vagas
        restantes sao preenchidas por busca vetorial, de modo que o contexto mantem
        sempre k documentos, como o ADR-0007 fixa.

        Busca puramente densa nao funciona neste cenario: com 30 documentos de
        estrutura quase identica, o numero do pedido tem peso desprezivel no vetor
        da pergunta, e o ranking fica praticamente independente dela — medido em
        10/09/2026, com 3 acertos em 30. Sistemas reais de atendimento tambem nao
        localizam um pedido por similaridade semantica: extraem o identificador e
        filtram.
        """
        vetor = self.vetorizar(pergunta)
        numero = extrair_numero_pedido(pergunta)

        alvo = self._por_numero_pedido(numero, vetor) if numero else []
        faltam = max(0, k - len(alvo))
        complementos = self._por_similaridade(
            vetor, faltam, {a.id_documento for a in alvo}
        )
        return alvo + complementos


def carregar_documentos(pasta: Path) -> list[dict]:
    """Le os documentos gerados por scripts/gerar_base_conhecimento.py."""
    arquivos = sorted((pasta / "documentos").glob("doc-*.json"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum documento em {pasta / 'documentos'}")
    return [json.loads(a.read_text(encoding="utf-8")) for a in arquivos]


def hash_do_estado(documentos: list[dict]) -> str:
    """Resumo do conteudo indexado, para verificar restauracao da base (RQ-18).

    As cargas do BIPIA serao embutidas nos documentos na Etapa 3. Entre cenarios, a
    base precisa voltar a um estado conhecido, sob pena de contaminacao cruzada
    entre casos. Este hash e o que torna "voltou ao estado conhecido" verificavel
    em vez de presumido.
    """
    partes = [
        f"{d['id_documento']}:{hashlib.sha256(d['texto'].encode()).hexdigest()}"
        for d in sorted(documentos, key=lambda x: x["id_documento"])
    ]
    return hashlib.sha256("|".join(partes).encode()).hexdigest()
