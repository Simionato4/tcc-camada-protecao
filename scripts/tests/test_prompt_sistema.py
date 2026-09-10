"""Testes do prompt de sistema (tarefa 2.6, requisito RQ-01).

O prompt e variavel de controle e carrega o instrumento de medicao da categoria de
exposicao de contexto interno. Um erro aqui contamina as quatro condicoes de uma vez.
"""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "gerar_prompt", RAIZ / "scripts" / "gerar_prompt_sistema.py"
)
gerar_prompt = importlib.util.module_from_spec(_spec)
sys.modules["gerar_prompt"] = gerar_prompt
_spec.loader.exec_module(gerar_prompt)

SEMENTE = 20260829


@pytest.fixture(scope="module")
def texto() -> str:
    marcador = gerar_prompt.derivar_marcador(SEMENTE)
    return gerar_prompt.extrair_texto(gerar_prompt.montar(marcador))


def test_marcador_tem_formato_improvavel_por_acaso() -> None:
    """Doze digitos hexadecimais dao 2^48 possibilidades.

    Se o marcador pudesse surgir por acaso na saida do modelo, sua ocorrencia
    deixaria de ser evidencia de vazamento e viraria ruido no criterio CTX-02.
    """
    marcador = gerar_prompt.derivar_marcador(SEMENTE)
    assert re.fullmatch(r"CANARIO-TCC-[0-9A-F]{12}", marcador)


def test_marcador_e_reproduzivel_e_depende_da_semente() -> None:
    assert gerar_prompt.derivar_marcador(SEMENTE) == gerar_prompt.derivar_marcador(SEMENTE)
    assert gerar_prompt.derivar_marcador(SEMENTE) != gerar_prompt.derivar_marcador(SEMENTE + 1)


def test_marcador_aparece_uma_unica_vez_no_prompt(texto: str) -> None:
    """Mais de uma ocorrencia tornaria ambigua a contagem de vazamentos."""
    assert texto.count(gerar_prompt.derivar_marcador(SEMENTE)) == 1


def test_prompt_nao_contem_segredo(texto: str) -> None:
    """Criterios PII-05 e CTX-01: o contexto oculto nao carrega dado cuja
    divulgacao produza impacto de seguranca direto.
    """
    proibidos = [
        r"sk-[A-Za-z0-9_\-]{10,}",          # chave de API
        r"(?i)\bsenha\b|\bpassword\b",
        r"(?i)api[_\- ]?key",
        r"(?i)authorization:\s*bearer",
        r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",   # CPF
        r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",  # CNPJ
        r"(?i)postgres(ql)?://|mysql://|mongodb(\+srv)?://",  # cadeia de conexao
    ]
    for padrao in proibidos:
        assert not re.search(padrao, texto), f"prompt contem padrao proibido: {padrao}"


def test_prompt_restringe_a_resposta_ao_contexto(texto: str) -> None:
    """Sem essa restricao, a condicao A responderia de conhecimento proprio e o
    vazamento pela base de conhecimento deixaria de ser observavel.
    """
    assert "contexto" in texto.lower()


def test_prompt_cabe_no_orcamento(texto: str) -> None:
    """O prompt entra em toda chamada das 3.883 previstas. Cada 100 tokens a mais
    custam cerca de US$ 0,39 no experimento completo.
    """
    tokens_estimados = len(texto) / 3.08
    assert tokens_estimados < 300, f"{tokens_estimados:.0f} tokens"


def test_arquivo_em_disco_corresponde_a_semente() -> None:
    caminho = gerar_prompt.DESTINO
    if not caminho.exists():
        pytest.skip("prompt ainda nao gerado; rode scripts/gerar_prompt_sistema.py")
    esperado = gerar_prompt.montar(gerar_prompt.derivar_marcador(SEMENTE))
    assert caminho.read_bytes().decode("utf-8") == esperado
