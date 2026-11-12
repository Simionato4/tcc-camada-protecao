"""Estagio 3 da camada: decisao e mascaramento (Etapa 4, T017; RF-005, `PII-01`, `PII-02`).

Decisoes do autor (12/11/2026):
- no lugar do dado entra o rotulo do tipo, entre colchetes: `[CPF]`, `[EMAIL]`...;
- mascara-se no `contexto` e na `saida`. Na `entrada` a camada detecta e devolve as
  deteccoes, mas encaminha o texto sem alterar: o cliente esta informando o proprio dado;
- as regras valem so na condicao B. Nas condicoes A, C e D a camada encaminha (o modo da
  condicao D no `/entrada` e a tarefa T026).

Textos e numeros escritos para este arquivo; os numeros validos sao os de
`test_documentos.py`.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from camada.app import main
from camada.app.contrato import Deteccao
from camada.app.decisao import MARCAS, decidir, mascarar

cliente = TestClient(main.app)


def _deteccao(tipo: str, inicio: int, fim: int) -> Deteccao:
    return Deteccao(tipo=tipo, posicao=(inicio, fim), valido=True)


# --- mascarar -------------------------------------------------------------------------


def test_cada_um_dos_sete_tipos_tem_marca() -> None:
    assert MARCAS == {
        "cpf": "[CPF]",
        "cnpj": "[CNPJ]",
        "pis": "[PIS]",
        "cns": "[CNS]",
        "titulo": "[TITULO]",
        "telefone": "[TELEFONE]",
        "email": "[EMAIL]",
    }


def test_mascara_substitui_o_trecho_inteiro_e_preserva_o_resto() -> None:
    texto = "CPF 123.456.789-09, ok"
    assert mascarar(texto, [_deteccao("cpf", 4, 18)]) == "CPF [CPF], ok"


def test_mascara_varios_trechos() -> None:
    texto = "a 12345678909 b fulano@example.com c"
    deteccoes = [_deteccao("cpf", 2, 13), _deteccao("email", 16, 34)]
    assert mascarar(texto, deteccoes) == "a [CPF] b [EMAIL] c"


def test_mascara_no_inicio_e_no_fim_do_texto() -> None:
    assert mascarar("12345678909", [_deteccao("cpf", 0, 11)]) == "[CPF]"


def test_sem_deteccao_o_texto_nao_muda() -> None:
    assert mascarar("nada aqui", []) == "nada aqui"


def test_tipo_sem_marca_e_erro() -> None:
    # Tipo desconhecido nao pode passar em claro por falta de marca.
    with pytest.raises(KeyError):
        mascarar("abc", [_deteccao("desconhecido", 0, 3)])


# --- decidir --------------------------------------------------------------------------


@pytest.mark.parametrize("ponto", ["contexto", "saida"])
def test_dado_pessoal_no_contexto_e_na_saida_e_mascarado(ponto: str) -> None:
    texto = "CPF 123.456.789-09"
    deteccoes = [_deteccao("cpf", 4, 18)]
    resultado = decidir(ponto, texto, deteccoes)
    assert resultado.decisao == "mascarar"
    assert resultado.texto == "CPF [CPF]"
    assert resultado.deteccoes == deteccoes


def test_dado_pessoal_na_entrada_e_encaminhado_com_as_deteccoes() -> None:
    texto = "meu CPF e 123.456.789-09"
    deteccoes = [_deteccao("cpf", 10, 24)]
    resultado = decidir("entrada", texto, deteccoes)
    assert resultado.decisao == "encaminhar"
    assert resultado.texto == texto
    assert resultado.deteccoes == deteccoes


@pytest.mark.parametrize("ponto", ["entrada", "contexto", "saida"])
def test_sem_deteccao_encaminha_o_texto_identico(ponto: str) -> None:
    resultado = decidir(ponto, "Qual o prazo de entrega?", [])
    assert resultado.decisao == "encaminhar"
    assert resultado.texto == "Qual o prazo de entrega?"
    assert resultado.deteccoes == []


# --- Pela interface HTTP: normalizacao, deteccao e decisao ligadas ---------------------


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


TEXTO = "O CPF do cliente e 123.456.789-09 e o e-mail e fulano@example.com."
MASCARADO = "O CPF do cliente e [CPF] e o e-mail e [EMAIL]."


@pytest.mark.parametrize("ponto", ["contexto", "saida"])
def test_condicao_b_mascara_no_contexto_e_na_saida(ponto: str) -> None:
    corpo = _post(ponto, TEXTO)
    assert corpo["decisao"] == "mascarar"
    assert corpo["texto"] == MASCARADO
    assert [d["tipo"] for d in corpo["deteccoes"]] == ["cpf", "email"]
    # Posicao no texto ORIGINAL (RQ-07).
    trechos = [TEXTO[d["posicao"][0] : d["posicao"][1]] for d in corpo["deteccoes"]]
    assert trechos == ["123.456.789-09", "fulano@example.com"]


def test_condicao_b_na_entrada_encaminha_e_informa_as_deteccoes() -> None:
    corpo = _post("entrada", TEXTO)
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == TEXTO
    assert [d["tipo"] for d in corpo["deteccoes"]] == ["cpf", "email"]


@pytest.mark.parametrize("condicao", ["A", "C", "D"])
@pytest.mark.parametrize("ponto", ["entrada", "contexto", "saida"])
def test_fora_da_condicao_b_a_camada_so_encaminha(ponto: str, condicao: str) -> None:
    corpo = _post(ponto, TEXTO, condicao=condicao)
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == TEXTO
    assert corpo["deteccoes"] == []


def test_digito_verificador_invalido_nao_e_mascarado() -> None:
    texto = "O numero 123.456.789-08 nao e CPF."
    corpo = _post("saida", texto)
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == texto
    assert corpo["deteccoes"] == []


def test_texto_sem_dado_pessoal_sai_identico() -> None:
    texto = "Seu pedido 10001 sai amanha, entrega das 09:30-15:30. Total: R$ 1.234,56."
    corpo = _post("saida", texto)
    assert corpo["decisao"] == "encaminhar"
    assert corpo["texto"] == texto


def test_dado_disfarcado_e_mascarado_por_inteiro_invisiveis_incluidos() -> None:
    disfarcado = "​".join("12345678909")
    corpo = _post("saida", f"CPF: {disfarcado}.")
    assert corpo["decisao"] == "mascarar"
    assert corpo["texto"] == "CPF: [CPF]."
    assert "​" not in corpo["texto"]


def test_o_resto_do_texto_mascarado_e_o_original_nao_o_normalizado() -> None:
    # A ligadura e o invisivel fora do dado continuam como vieram: a camada so troca o
    # trecho do dado.
    texto = "conﬁrma​do: 123.456.789-09"
    corpo = _post("saida", texto)
    assert corpo["texto"] == "conﬁrma​do: [CPF]"


def test_ablacao_o_dado_disfarcado_so_e_mascarado_com_a_normalizacao(monkeypatch) -> None:
    texto = "CPF: " + "​".join("12345678909")
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", False)
    sem = _post("saida", texto)
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", True)
    com = _post("saida", texto)
    assert sem["decisao"] == "encaminhar" and sem["texto"] == texto
    assert com["decisao"] == "mascarar" and com["texto"] == "CPF: [CPF]"


def test_ablacao_dado_sem_disfarce_tem_o_mesmo_resultado(monkeypatch) -> None:
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", False)
    sem = _post("saida", TEXTO)
    monkeypatch.setattr(main, "NORMALIZACAO_ATIVA", True)
    com = _post("saida", TEXTO)
    for corpo in (sem, com):
        corpo.pop("tempo_ms")
    assert sem == com
