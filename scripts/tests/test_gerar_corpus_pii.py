"""Corpus de documentos (tarefa 3.6, ADR-0015): confere o corpus inteiro, ocorrencia
por ocorrencia, sem depender das assercoes internas do gerador."""

from __future__ import annotations

import collections
import importlib.util
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("gerar_corpus_pii", RAIZ / "scripts" / "gerar_corpus_pii.py")
g = importlib.util.module_from_spec(_spec)
sys.modules["gerar_corpus_pii"] = g
_spec.loader.exec_module(g)

SEMENTE = 20260829


@pytest.fixture(scope="module")
def textos():
    return g.montar(SEMENTE)


def _ocorrencias(textos):
    return [(t, o) for t in textos for o in t["ocorrencias"]]


def _nucleo(o) -> str:
    n = g._so_caracteres(o["valor"])
    if o["tipo"] == "telefone" and len(n) == 13 and n.startswith("55"):
        n = n[2:]
    return n


def test_geracao_e_deterministica(textos):
    a = json.dumps(textos, sort_keys=True, ensure_ascii=False)
    b = json.dumps(g.montar(SEMENTE), sort_keys=True, ensure_ascii=False)
    assert a == b


def test_contagens_por_tipo_e_classe(textos):
    c = collections.Counter((o["tipo"], o["polaridade"], o["classe_negativo"]) for _, o in _ocorrencias(textos))
    assert sum(c.values()) == 700
    assert sum(n for (_, p, _), n in c.items() if p == "positivo") == 350
    assert sum(n for (_, p, _), n in c.items() if p == "negativo") == 350
    for tipo in g.TIPOS:
        assert c[(tipo, "positivo", None)] == 50
        assert sum(c[(tipo, "negativo", k)] for k in g.CLASSES[tipo]) == 50


def test_posicao_no_texto_original(textos):
    for t, o in _ocorrencias(textos):
        assert t["texto"][o["inicio"]:o["fim"]] == o["valor"], (t["id"], o)


def test_um_a_tres_ocorrencias_por_texto_sem_sobreposicao(textos):
    for t in textos:
        assert 1 <= len(t["ocorrencias"]) <= 3
        trechos = sorted((o["inicio"], o["fim"]) for o in t["ocorrencias"])
        assert all(a[1] <= b[0] for a, b in zip(trechos, trechos[1:]))


def test_positivos_validos_so_no_proprio_tipo(textos):
    for _, o in _ocorrencias(textos):
        if o["polaridade"] == "positivo" and o["tipo"] != "email":
            assert g.positivo_aceitavel(o["tipo"], _nucleo(o)), o


def test_negativos_numericos_invalidos_em_todos_os_tipos_do_comprimento(textos):
    for _, o in _ocorrencias(textos):
        if o["polaridade"] == "negativo" and o["tipo"] in g.DOCUMENTOS + ("telefone",):
            assert g.negativo_aceitavel(_nucleo(o)), o
            # o valor como aparece no texto tambem nao pode fechar a conta de outro tipo
            assert g.negativo_aceitavel(g._so_caracteres(o["valor"])), o


def test_nenhum_numero_indefinido(textos):
    for _, o in _ocorrencias(textos):
        if o["tipo"] == "email":  # e-mail nao passa pela regra dos documentos
            continue
        for estado, _ in g.estados(_nucleo(o)).values():
            assert estado != g.dv.INDEFINIDO, o


def test_email_positivo_so_em_dominio_reservado(textos):
    for _, o in _ocorrencias(textos):
        if o["tipo"] == "email" and o["polaridade"] == "positivo":
            assert o["valor"].rsplit("@", 1)[1] in g.DOMINIOS


def test_telefone_positivo_com_ddd_da_anatel(textos):
    for _, o in _ocorrencias(textos):
        if o["tipo"] == "telefone" and o["polaridade"] == "positivo":
            assert g.telefone_valido(_nucleo(o)), o


def test_cnpj_metade_numerico_metade_alfanumerico(textos):
    formatos = collections.Counter(
        o["atributos"]["formato_cnpj"]
        for _, o in _ocorrencias(textos)
        if o["tipo"] == "cnpj" and o["polaridade"] == "positivo"
    )
    assert formatos == {"numerico": 25, "alfanumerico": 25}


def test_natureza(textos):
    for _, o in _ocorrencias(textos):
        assert o["natureza"] == ("pessoa_juridica" if o["tipo"] == "cnpj" else "pessoa_natural")


def test_prefixo_55_de_telefone_curto_e_conferido():
    """Defeito encontrado em 14/10/2026: o gerador conferia o numero antes do formato."""
    # "+55 33 988-9435" vira 55339889435, que fecha a conta de outro tipo de 11 digitos
    assert g.negativo_aceitavel("339889435")
    assert not g.valor_negativo_aceitavel("+55 33 988-9435")


def test_onze_noves_nao_e_negativo_de_cpf_porque_e_celular_valido():
    assert g.telefone_valido("99999999999")
    assert not g.negativo_aceitavel("99999999999")


# ------------------------------------------------- formato parcial (revisao de 28/10/2026)

def test_positivos_de_documento_em_tres_formatos_de_mascara(textos):
    c = collections.Counter(
        (o["tipo"], o["atributos"]["mascara"])
        for _, o in _ocorrencias(textos)
        if o["tipo"] in g.DOCUMENTOS and o["polaridade"] == "positivo"
    )
    for tipo in g.DOCUMENTOS:
        assert {f: c[(tipo, f)] for f in g.FORMATOS_MASCARA} == {"completa": 17, "ausente": 17, "parcial": 16}, tipo


def test_parcial_difere_da_completa_e_do_numero_sem_mascara(textos):
    vistos = 0
    for _, o in _ocorrencias(textos):
        if o["tipo"] in g.DOCUMENTOS and o["atributos"].get("mascara") == "parcial":
            nucleo = g._so_caracteres(o["valor"])
            completa = g.mascarar(o["tipo"], nucleo)
            assert o["valor"] != nucleo and o["valor"] != completa, o
            # so separadores da mascara oficial, ou espaco no lugar deles
            assert set(o["valor"]) - set(nucleo) <= set(completa) - set(nucleo) | {" "}, o
            vistos += 1
    assert vistos == 5 * (16 + g.N1_PARCIAIS)


def test_metade_da_n1_em_formato_parcial(textos):
    c = collections.Counter(
        (o["tipo"], o["atributos"]["mascara"])
        for _, o in _ocorrencias(textos)
        if o["classe_negativo"] == "N1"
    )
    for tipo in g.DOCUMENTOS:
        assert c[(tipo, "parcial")] == 5 and c[(tipo, "completa")] == 5, tipo


def test_telefone_positivo_em_cinco_formatos(textos):
    c = collections.Counter(
        o["atributos"]["formato"]
        for _, o in _ocorrencias(textos)
        if o["tipo"] == "telefone" and o["polaridade"] == "positivo"
    )
    assert c == {0: 10, 1: 10, 2: 10, 3: 10, 4: 10}


def test_mascara_parcial_mantem_e_remove_ao_menos_um_separador():
    import random

    r = random.Random(0)
    for _ in range(200):
        valor = g.mascarar_parcial(r, "cpf", "12345678909")
        separadores = [c for c in valor if not c.isalnum()]
        assert valor not in ("12345678909", "123.456.789-09")
        assert 1 <= len(separadores) <= 3
