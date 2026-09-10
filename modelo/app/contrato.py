"""Contrato do servico do modelo."""

from pydantic import BaseModel, Field


class Requisicao(BaseModel):
    # O prompt de sistema NAO entra aqui de proposito: e variavel de controle e vem
    # do arquivo versionado, carregado pelo servico.
    mensagem: str = Field(min_length=1, max_length=200_000)
    id_requisicao: str


class Resposta(BaseModel):
    resposta: str
    tokens_entrada: int
    tokens_saida: int
    usd: float
    simulado: bool
    modelo: str
    tempo_ms: float
    # Rastreabilidade do prompt efetivamente usado: liga a resposta a versao do
    # arquivo versionado, sem precisar reproduzi-lo no registro.
    hash_prompt: str
