"""Configuracao da condicao C: Presidio com adaptacao minima para portugues (ADR-0022).

Confere, sem subir conteiner, que a configuracao versionada continua sendo a decidida
antes de qualquer execucao: so portugues, limiar 0, os nove reconhecedores ativos sem
pais e nenhum outro, nenhum contexto proprio, o mapeamento de entidades identico ao
original da imagem e o modelo instalado pela URL oficial com hash conferido.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "presidio-analyzer"

RECONHECEDORES_PT = {
    "CreditCardRecognizer",
    "CryptoRecognizer",
    "DateRecognizer",
    "EmailRecognizer",
    "IbanRecognizer",
    "IpRecognizer",
    "MacAddressRecognizer",
    "PhoneRecognizer",
    "UrlRecognizer",
}

# Copiado de presidio_analyzer/conf/default.yaml da imagem fixada (analyzer 2.2.364).
MAPEAMENTO_ORIGINAL = {
    "PER": "PERSON",
    "PERSON": "PERSON",
    "NORP": "NRP",
    "FAC": "LOCATION",
    "LOC": "LOCATION",
    "GPE": "LOCATION",
    "LOCATION": "LOCATION",
    "ORG": "ORGANIZATION",
    "ORGANIZATION": "ORGANIZATION",
    "DATE": "DATE_TIME",
    "TIME": "DATE_TIME",
}
IGNORADOS_ORIGINAL = [
    "ORGANIZATION", "CARDINAL", "EVENT", "LANGUAGE", "LAW", "MONEY",
    "ORDINAL", "PERCENT", "PRODUCT", "QUANTITY", "WORK_OF_ART",
]


def _ler(nome: str) -> dict:
    return yaml.safe_load((PASTA / "conf" / nome).read_text(encoding="utf-8"))


def test_analisador_so_portugues_e_limiar_zero():
    conf = _ler("analyzer_pt.yaml")
    assert conf["supported_languages"] == ["pt"]
    assert conf["default_score_threshold"] == 0


def test_nlp_so_modelo_portugues_e_mapeamento_original():
    conf = _ler("nlp_pt.yaml")
    assert conf["nlp_engine_name"] == "spacy"
    assert conf["models"] == [{"lang_code": "pt", "model_name": "pt_core_news_lg"}]
    ner = conf["ner_model_configuration"]
    assert ner["model_to_presidio_entity_mapping"] == MAPEAMENTO_ORIGINAL
    assert ner["low_confidence_score_multiplier"] == 0.4
    assert ner["labels_to_ignore"] == IGNORADOS_ORIGINAL


def test_reconhecedores_exatamente_os_nove_sem_pais_e_sem_contexto():
    conf = _ler("recognizers_pt.yaml")
    assert conf["supported_languages"] == ["pt"]
    nomes = [r["name"] for r in conf["recognizers"]]
    assert len(nomes) == len(set(nomes))
    assert set(nomes) == RECONHECEDORES_PT
    for rec in conf["recognizers"]:
        assert rec["type"] == "predefined", rec
        assert "country_code" not in rec, rec
        assert rec.get("enabled", True) is True, rec
        for idioma in rec["supported_languages"]:
            if isinstance(idioma, dict):
                assert idioma == {"language": "pt"}, rec  # sem context proprio
            else:
                assert idioma == "pt", rec


def test_modelo_instalado_pela_url_oficial_com_hash():
    dockerfile = (PASTA / "Dockerfile").read_text(encoding="utf-8")
    url = re.search(r"https://\S+?\.whl#sha256=([0-9a-f]{64})", dockerfile)
    assert url, "a wheel do modelo precisa vir com #sha256= para o pip conferir"
    assert url.group(0).startswith(
        "https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.8.0/"
    )
    assert url.group(1) == "2561c9a72a938d37141e9694e1a36d25061a44ce7e4f3bad2d3fa3bb836191af"
    for variavel, arquivo in (
        ("ANALYZER_CONF_FILE", "analyzer_pt.yaml"),
        ("RECOGNIZER_REGISTRY_CONF_FILE", "recognizers_pt.yaml"),
        ("NLP_CONF_FILE", "nlp_pt.yaml"),
    ):
        assert f"{variavel}=presidio_analyzer/conf/tcc/{arquivo}" in dockerfile
    assert re.search(r"^USER 1001\s*$", dockerfile, re.M), "devolver o usuario original"
