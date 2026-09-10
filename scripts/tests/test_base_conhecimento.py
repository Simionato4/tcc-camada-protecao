"""Testes do gerador da base de conhecimento.

Cada teste aqui protege uma propriedade da qual uma decisao registrada depende. Um
gerador de dados sinteticos que "parece certo" mas viola uma dessas propriedades
produz um experimento invalido cuja causa so apareceria na analise final.
"""

import importlib.util
import sys
from pathlib import Path

import pytest
from validate_docbr import CNPJ, CPF

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "gerar_base", RAIZ / "scripts" / "gerar_base_conhecimento.py"
)
gerar_base = importlib.util.module_from_spec(_spec)
sys.modules["gerar_base"] = gerar_base
_spec.loader.exec_module(gerar_base)

SEMENTE = 20260829


@pytest.fixture(scope="module")
def base():
    return gerar_base.gerar(SEMENTE)


def test_quantidade_e_identificadores_unicos(base) -> None:
    documentos, _ = base
    assert len(documentos) == gerar_base.QUANTIDADE
    ids = [d["id_documento"] for d in documentos]
    assert len(set(ids)) == len(ids)


def test_numero_de_pedido_e_unico(base) -> None:
    """O pareamento pergunta-documento do ADR-0002 depende disso."""
    documentos, _ = base
    numeros = [d["numero_pedido"] for d in documentos]
    assert len(set(numeros)) == len(numeros)


def test_numero_de_pedido_aparece_em_um_unico_documento(base) -> None:
    """Se o pedido 10001 fosse citado tambem no doc-005, a pergunta pareada
    recuperaria dois documentos e a recuperacao deixaria de ser deterministica.
    """
    documentos, _ = base
    for documento in documentos:
        numero = documento["numero_pedido"]
        contendo = [d["id_documento"] for d in documentos if numero in d["texto"]]
        assert contendo == [documento["id_documento"]], (
            f"pedido {numero} aparece em {contendo}"
        )


def test_posicoes_do_gabarito_apontam_para_o_valor_correto(base) -> None:
    """RQ-07. Este e o teste mais importante do arquivo.

    Se as posicoes nao baterem com o texto original, o mascaramento recai no lugar
    errado e precisao e revocacao ficam incorretas — e o defeito so apareceria
    depois da execucao do protocolo, quando nao ha conserto.
    """
    documentos, _ = base
    for documento in documentos:
        texto = documento["texto"]
        for ocorrencia in documento["ocorrencias_dado_pessoal"]:
            trecho = texto[ocorrencia["inicio"]:ocorrencia["fim"]]
            assert trecho == ocorrencia["valor"], (
                f"{documento['id_documento']}: esperado {ocorrencia['valor']!r}, "
                f"encontrado {trecho!r}"
            )


def test_ocorrencias_nao_se_sobrepoem(base) -> None:
    documentos, _ = base
    for documento in documentos:
        intervalos = sorted(
            (o["inicio"], o["fim"]) for o in documento["ocorrencias_dado_pessoal"]
        )
        for (_, fim_anterior), (inicio, _) in zip(intervalos, intervalos[1:]):
            assert inicio >= fim_anterior, documento["id_documento"]


def test_cpf_e_cnpj_passam_no_digito_verificador(base) -> None:
    """A camada validara digito verificador. Documento sintetico invalido viraria
    falso negativo do detector sem que a regra tivesse falhado.
    """
    documentos, _ = base
    validadores = {"CPF": CPF(), "CNPJ": CNPJ()}
    encontrados = {"CPF": 0, "CNPJ": 0}
    for documento in documentos:
        for ocorrencia in documento["ocorrencias_dado_pessoal"]:
            if ocorrencia["tipo"] in validadores:
                assert validadores[ocorrencia["tipo"]].validate(ocorrencia["valor"]), (
                    f"{documento['id_documento']}: {ocorrencia['tipo']} invalido"
                )
                encontrados[ocorrencia["tipo"]] += 1
    assert encontrados == {"CPF": 30, "CNPJ": 30}


def test_cnpj_e_marcado_como_pessoa_juridica(base) -> None:
    """RQ-03: CNPJ nao e, por si, dado pessoal de pessoa natural."""
    documentos, _ = base
    for documento in documentos:
        for ocorrencia in documento["ocorrencias_dado_pessoal"]:
            esperada = "pessoa_juridica" if ocorrencia["tipo"] == "CNPJ" else "pessoa_natural"
            assert ocorrencia["natureza"] == esperada


def test_tamanho_dentro_da_faixa_do_adr_0007(base) -> None:
    documentos, _ = base
    for documento in documentos:
        assert (
            gerar_base.MIN_CARACTERES
            <= documento["caracteres"]
            <= gerar_base.MAX_CARACTERES
        ), f"{documento['id_documento']}: {documento['caracteres']} caracteres"


def test_geracao_e_reproduzivel() -> None:
    primeira, _ = gerar_base.gerar(SEMENTE)
    segunda, _ = gerar_base.gerar(SEMENTE)
    assert primeira == segunda


def test_sementes_diferentes_produzem_bases_diferentes() -> None:
    primeira, _ = gerar_base.gerar(SEMENTE)
    outra, _ = gerar_base.gerar(SEMENTE + 1)
    assert primeira != outra


def test_toda_pergunta_pareada_cita_o_pedido_do_seu_documento(base) -> None:
    documentos, perguntas = base
    assert len(perguntas) == len(documentos)
    por_id = {d["id_documento"]: d for d in documentos}
    for pergunta in perguntas:
        documento = por_id[pergunta["id_documento"]]
        assert documento["numero_pedido"] in pergunta["pergunta"]
