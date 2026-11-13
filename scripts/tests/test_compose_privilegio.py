"""RQ-15: cada servico recebe so as variaveis de ambiente que usa.

Nenhum servico le o `.env` inteiro (`env_file`), e so o servico `modelo` recebe a chave da
Anthropic. Falha se alguem voltar a entregar credenciais a quem nao precisa delas.
"""

from __future__ import annotations

from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[2]


def _servicos() -> dict:
    return yaml.safe_load((RAIZ / "docker-compose.yml").read_text(encoding="utf-8"))["services"]


def _variaveis(servico: dict) -> set[str]:
    env = servico.get("environment") or []
    if isinstance(env, dict):
        return set(env)
    return {item.split("=", 1)[0] for item in env}


def test_nenhum_servico_le_o_env_inteiro():
    for nome, servico in _servicos().items():
        assert "env_file" not in servico, nome


def test_chave_da_anthropic_so_no_servico_modelo():
    com_chave = {n for n, s in _servicos().items() if "ANTHROPIC_API_KEY" in _variaveis(s)}
    assert com_chave == {"modelo"}


def test_camada_recebe_so_o_que_le():
    assert _variaveis(_servicos()["camada"]) == {
        "ARQUIVO_LOG",
        "NORMALIZACAO",
        "MARCADOR",
        "MODERACAO_SIMULADA",
        "OPENAI_API_KEY",
    }


def test_chave_da_openai_so_no_servico_camada():
    # A moderacao da condicao D e chamada pela camada (ADR-0027, E5).
    com_chave = {n for n, s in _servicos().items() if "OPENAI_API_KEY" in _variaveis(s)}
    assert com_chave == {"camada"}
