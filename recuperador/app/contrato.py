"""Contrato do servico de recuperacao.

Existe separado da camada de propósito. A camada e o objeto avaliado na condicao B,
e sua latencia interna e um indicador do trabalho: acrescentar vetorizacao e
consulta ao Qdrant dentro dela tornaria o `tempo_ms` incomparavel com as demais
condicoes (ADR-0011).
"""

from pydantic import BaseModel, Field


class Requisicao(BaseModel):
    pergunta: str
    k: int = Field(default=3, ge=1, le=10)
    id_requisicao: str


class Documento(BaseModel):
    id_documento: str
    numero_pedido: str
    texto: str
    escore: float


class Resposta(BaseModel):
    documentos: list[Documento]
    k: int
    tempo_ms: float
    # Rastreabilidade: liga cada recuperacao ao indice que a produziu. Sem isso, um
    # registro bruto nao permite reconstruir qual corpus e qual modelo de
    # embeddings geraram aquele contexto.
    versao_indice: str
    # Exigido pelo ADR-0002: o executor registra quais documentos entraram no top-k
    # para marcar como invalido o caso em que o documento alvo nao foi recuperado.
    ids_recuperados: list[str]
