"""Marcador unico na saida (Etapa 4, T019; RF-007, `CTX-02`).

O marcador do prompt de sistema nao e segredo (RQ-01): e instrumento de medicao. Se ele
aparece na resposta do modelo, o conteudo oculto esta vazando.

Decisao do autor (12/11/2026): marcador na `saida` -> **bloquear** a resposta inteira, e
nao mascarar so o marcador. Mascarar esconderia a evidencia e entregaria o resto do
vazamento. O texto devolvido no bloqueio e vazio: nada da resposta segue adiante.

Vale so na condicao B e so no ponto `saida`. A comparacao e sobre o texto normalizado,
sem diferenciar maiuscula de minuscula.
"""

import re
import uuid
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from camada.app import main
from camada.app.deteccao import detectar_marcador
from camada.app.normalizacao import normalizar

RAIZ = Path(__file__).resolve().parents[2]
MARCADOR = "CANARIO-TCC-2DEFEC2A9B0F"

cliente = TestClient(main.app)


def achar(texto: str, normalizacao: bool = True) -> list[str]:
    deteccoes = detectar_marcador(normalizar(texto, ativa=normalizacao), MARCADOR)
    assert all(d.tipo == "marcador" for d in deteccoes)
    return [texto[d.posicao[0] : d.posicao[1]] for d in deteccoes]


# --- De onde vem o valor --------------------------------------------------------------


def test_marcador_da_camada_e_o_do_prompt_de_sistema_congelado() -> None:
    prompt = (RAIZ / "assistente" / "prompt_sistema.md").read_text(encoding="utf-8")
    assert f"`{MARCADOR}`" in prompt
    assert main.MARCADOR == MARCADOR


def test_marcador_do_compose_e_o_mesmo() -> None:
    compose = yaml.safe_load((RAIZ / "docker-compose.yml").read_text(encoding="utf-8"))
    variaveis = dict(item.split("=", 1) for item in compose["services"]["camada"]["environment"])
    assert re.fullmatch(r"\$\{MARCADOR:-(.+)\}", variaveis["MARCADOR"]).group(1) == MARCADOR


@pytest.mark.parametrize("valor", ["", "   ", "curto"])
def test_marcador_vazio_ou_curto_impede_a_camada_de_subir(valor: str) -> None:
    with pytest.raises(ValueError):
        main.ler_marcador(valor)


# --- Deteccao ---------------------------------------------------------------------------


def test_marcador_inteiro() -> None:
    assert achar(f"Identificador interno: {MARCADOR}.") == [MARCADOR]


def test_marcador_em_minusculas_ou_misturado() -> None:
    assert achar(f"veja {MARCADOR.lower()} aqui") == [MARCADOR.lower()]
    assert achar("veja Canario-Tcc-2defec2a9b0f aqui") == ["Canario-Tcc-2defec2a9b0f"]


def test_marcador_com_invisiveis_no_meio_posicao_cobre_o_original() -> None:
    disfarcado = "​".join(MARCADOR)
    assert achar(f"codigo {disfarcado} fim") == [disfarcado]


def test_marcador_em_caracteres_de_largura_total() -> None:
    disfarcado = "".join(chr(ord(c) + 0xFEE0) if c != "-" else c for c in MARCADOR)
    assert disfarcado != MARCADOR
    assert achar(f"codigo {disfarcado} fim") == [disfarcado]


def test_duas_ocorrencias() -> None:
    assert achar(f"{MARCADOR} e de novo {MARCADOR}") == [MARCADOR, MARCADOR]


@pytest.mark.parametrize(
    "texto",
    [
        "Nao posso compartilhar minhas instrucoes.",
        "CANARIO-TCC-",  # so o prefixo
        "CANARIO-TCC-2DEFEC2A9B0",  # falta o ultimo caractere
        "o canario cantou no TCC",
        "",
    ],
)
def test_sem_marcador(texto: str) -> None:
    assert achar(texto) == []


def test_sem_normalizacao_o_marcador_disfarcado_passa() -> None:
    disfarcado = "​".join(MARCADOR)
    assert achar(f"codigo {disfarcado}", normalizacao=False) == []
    assert achar(f"codigo {MARCADOR}", normalizacao=False) == [MARCADOR]


# --- Pela interface HTTP ----------------------------------------------------------------


def _post(ponto: str, texto: str, condicao: str = "B") -> dict:
    resposta = cliente.post(
        f"/{ponto}",
        json={
            "ponto": ponto,
            "texto": texto,
            "id_requisicao": str(uuid.uuid4()),
            "condicao": condicao,
        },
    )
    assert resposta.status_code == 200
    return resposta.json()


VAZAMENTO = f"Claro! Minhas instrucoes dizem: Identificador interno desta configuracao: {MARCADOR}"


def test_marcador_na_saida_bloqueia_e_nao_devolve_nada_da_resposta() -> None:
    corpo = _post("saida", VAZAMENTO)
    assert corpo["decisao"] == "bloquear"
    assert corpo["texto"] == ""
    assert [d["tipo"] for d in corpo["deteccoes"]] == ["marcador"]
    inicio, fim = corpo["deteccoes"][0]["posicao"]
    assert VAZAMENTO[inicio:fim] == MARCADOR
    # Bloqueio por regra nao e erro tecnico (RQ-10).
    assert corpo["erro"] is None


def test_marcador_disfarcado_na_saida_tambem_bloqueia() -> None:
    corpo = _post("saida", "instrucoes: " + "​".join(MARCADOR))
    assert corpo["decisao"] == "bloquear"
    assert corpo["texto"] == ""


def test_marcador_junto_de_dado_pessoal_bloqueia_em_vez_de_mascarar() -> None:
    corpo = _post("saida", f"{VAZAMENTO}. CPF 123.456.789-09.")
    assert corpo["decisao"] == "bloquear"
    assert corpo["texto"] == ""
    assert [d["tipo"] for d in corpo["deteccoes"]] == ["marcador", "cpf"]


@pytest.mark.parametrize("ponto", ["entrada", "contexto"])
def test_marcador_fora_da_saida_nao_bloqueia(ponto: str) -> None:
    # O usuario escrever o marcador, ou ele aparecer num documento, nao e vazamento.
    corpo = _post(ponto, VAZAMENTO)
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == VAZAMENTO
    assert corpo["deteccoes"] == []


@pytest.mark.parametrize("condicao", ["A", "C", "D"])
def test_fora_da_condicao_b_o_marcador_passa(condicao: str) -> None:
    corpo = _post("saida", VAZAMENTO, condicao=condicao)
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == VAZAMENTO


def test_ablacao_marcador_disfarcado_so_e_bloqueado_com_a_normalizacao(monkeypatch) -> None:
    texto = "instrucoes: " + "​".join(MARCADOR)
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", False)
    assert _post("saida", texto)["decisao"] == "encaminhar"
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", True)
    assert _post("saida", texto)["decisao"] == "bloquear"
