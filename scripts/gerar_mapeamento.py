"""Gera `conjunto_teste/selecao/mapeamento_rotulos.json` (tarefa 3.4, RQ-04, ADR-0018).

Um registro por caso, sem texto (ADR-0016): identificador, hash do texto, conjunto,
papel, grupo primario, natureza do rotulo, rotulo de origem e atributos secundarios.
O criterio textual de cada rotulo esta em `docs/mapeamento-rotulos.md`.

Fontes lidas: `data_en.csv` do Do-Not-Answer, `text_attack_test.json` do BIPIA, e as
duas selecoes versionadas do HackAPrompt (`hackaprompt.json` e `hackaprompt_ctx.json`).
Nao precisa do parquet.

Inclui o corpus de documentos (tarefa 3.6, ADR-0015) e as mensagens legitimas (tarefa
3.8, ADR-0023), lidos dos arquivos versionados em `conjunto_teste/`.

Uso:
    python scripts/gerar_mapeamento.py                 # grava e imprime o sha256
    python scripts/gerar_mapeamento.py --apenas-contar # nao grava nada
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "conjunto_teste" / "origem"
SELECAO = RAIZ / "conjunto_teste" / "selecao"
SAIDA = SELECAO / "mapeamento_rotulos.json"

_spec = importlib.util.spec_from_file_location(
    "classificar_codificacao", RAIZ / "scripts" / "classificar_codificacao.py"
)
clf = importlib.util.module_from_spec(_spec)
sys.modules["classificar_codificacao"] = clf
_spec.loader.exec_module(clf)

AREA_VAZAMENTO = "Information Hazards"
EIXO_VAZAMENTO = {
    "Risks from leaking or inferring sensitive information (organization/gov)":
        "organizacao_governo",
    "Compromise privacy by leaking or inferring private information (person/individual)":
        "privacidade_individuo",
}


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def eixo_vazamento(area: str, tipo: str) -> str | None:
    """Atributo secundario das 248 da area de vazamento (ADR-0018). Falha se o rotulo
    de origem for desconhecido, em vez de silenciar."""
    if area != AREA_VAZAMENTO:
        return None
    return EIXO_VAZAMENTO[tipo]


def do_not_answer() -> list[dict]:
    with (ORIGEM / "do-not-answer" / "data_en.csv").open(encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    registros = []
    for l in linhas:
        atributos = {}
        eixo = eixo_vazamento(l["risk_area"], l["types_of_harm"])
        if eixo:
            atributos["eixo_vazamento"] = eixo
        registros.append({
            "caso_id": f"dna-{int(l['id']):04d}",
            "conjunto": "do-not-answer",
            "sha256_texto": sha256(l["question"]),
            "papel": "caso_de_risco",
            "grupo_primario": "NOC",
            "origem_rotulo": "externa",
            "rotulo_origem": {
                "risk_area": l["risk_area"],
                "types_of_harm": l["types_of_harm"],
                "specific_harms": l["specific_harms"],
            },
            "atributos": atributos,
        })
    return registros


def bipia() -> list[dict]:
    caminho = ORIGEM / "bipia" / "benchmark" / "text_attack_test.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    registros = []
    for categoria, cargas in dados.items():
        for indice, carga in enumerate(cargas):
            registros.append({
                "caso_id": f"bipia-{slug(categoria)}-{indice}",
                "conjunto": "bipia",
                "sha256_texto": sha256(carga),
                "papel": "caso_de_risco",
                "grupo_primario": "INJ",
                "origem_rotulo": "externa",
                "rotulo_origem": {"categoria": categoria, "indice": indice},
                # A categoria do BIPIA nao descreve a forma da carga: registra-se a
                # representacao pela R1, para que isso seja verificavel.
                "atributos": {"representacao_r1": clf.classificar(carga)},
            })
    return registros


def hackaprompt_inj() -> list[dict]:
    selecao = json.loads((SELECAO / "hackaprompt.json").read_text(encoding="utf-8"))
    registros = []
    for c in selecao["selecionados"]:
        atributos = {"estrato_codificacao": c["classe_final"]}
        if int(c["level"]) == 2:
            atributos["objetivo_extracao"] = True
        registros.append({
            "caso_id": f"hackaprompt-inj-{int(c['ordem']):02d}",
            "conjunto": "hackaprompt",
            "sha256_texto": c["sha256_user_input"],
            "papel": "caso_de_risco",
            "grupo_primario": "INJ",
            "origem_rotulo": "mista",
            "rotulo_origem": {"level": int(c["level"])},
            "atributos": atributos,
        })
    return registros


def hackaprompt_ctx() -> list[dict]:
    selecao = json.loads((SELECAO / "hackaprompt_ctx.json").read_text(encoding="utf-8"))
    return [
        {
            "caso_id": f"hackaprompt-ctx-{int(c['ordem']):02d}",
            "conjunto": "hackaprompt",
            "sha256_texto": c["sha256_user_input"],
            "papel": "caso_de_risco",
            "grupo_primario": "CTX",
            "origem_rotulo": "mista",
            "rotulo_origem": {"level": int(c["level"])},
            "atributos": {"classe_codificacao_automatica": c["classe_automatica"]},
        }
        for c in selecao["selecionados"]
    ]


CORPUS_PII = RAIZ / "conjunto_teste" / "pii" / "corpus.jsonl"


def corpus_pii() -> list[dict]:
    """Um registro por texto do corpus (unidade submetida a camada e ao Presidio). O
    gabarito por ocorrencia fica no proprio corpus; aqui vao contagens."""
    if not CORPUS_PII.exists():
        return []
    registros = []
    with CORPUS_PII.open(encoding="utf-8") as arquivo:
        for linha in arquivo:
            t = json.loads(linha)
            pol = collections.Counter(o["polaridade"] for o in t["ocorrencias"])
            registros.append({
                "caso_id": t["id"],
                "conjunto": "corpus-pii",
                "sha256_texto": sha256(t["texto"]),
                "papel": "caso_de_risco",
                "grupo_primario": "PII",
                "origem_rotulo": "propria",
                "rotulo_origem": None,
                "atributos": {
                    "ocorrencias_positivas": pol["positivo"],
                    "ocorrencias_negativas": pol["negativo"],
                    "tipos": sorted({o["tipo"] for o in t["ocorrencias"]}),
                },
            })
    return registros


LEGITIMAS = RAIZ / "conjunto_teste" / "legitimas" / "mensagens.jsonl"


def legitimas() -> list[dict]:
    """As 100 mensagens legitimas: controle de falso positivo, sem grupo (ADR-0018, ADR-0023)."""
    if not LEGITIMAS.exists():
        return []
    registros = []
    with LEGITIMAS.open(encoding="utf-8") as arquivo:
        for linha in arquivo:
            m = json.loads(linha)
            registros.append({
                "caso_id": m["id"],
                "conjunto": "legitimas",
                "sha256_texto": sha256(m["texto"]),
                "papel": "controle_legitimo",
                "grupo_primario": None,
                "origem_rotulo": "propria",
                "rotulo_origem": None,
                "atributos": {"bloco": m["bloco"]},
            })
    return registros


def montar() -> dict:
    pii = corpus_pii()
    leg = legitimas()
    registros = do_not_answer() + bipia() + hackaprompt_inj() + hackaprompt_ctx() + pii + leg
    registros.sort(key=lambda r: r["caso_id"])

    ids = [r["caso_id"] for r in registros]
    if len(ids) != len(set(ids)):
        raise ValueError("caso_id repetido")
    hashes = collections.Counter((r["conjunto"], r["sha256_texto"]) for r in registros)
    repetidos = {k: n for k, n in hashes.items() if n > 1}

    return {
        "descricao": (
            "Mapeamento dos rotulos de origem para os grupos da matriz (RQ-04, ADR-0018). "
            "Sem texto (ADR-0016). Criterio textual em docs/mapeamento-rotulos.md."
        ),
        "esquema": {
            "papel": ["caso_de_risco", "controle_legitimo"],
            "grupo_primario": ["INJ", "PII", "CTX", "NOC", None],
            "origem_rotulo": {
                "externa": "rotulo do proprio conjunto publico",
                "propria": "rotulo e o desenho deste trabalho",
                "mista": "rotulo de origem externo, com atributo de desenho proprio",
            },
        },
        "pendentes": (
            {} if pii else {"corpus_documentos": "tarefa 3.6 (grupo PII, origem_rotulo propria)"}
        ) | ({} if leg else {"mensagens_legitimas": "tarefa 3.8 (papel controle_legitimo, sem grupo)"}),
        "textos_repetidos_no_mesmo_conjunto": len(repetidos),
        "registros": registros,
    }


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--apenas-contar", action="store_true")
    argumentos = analisador.parse_args()

    mapa = montar()
    registros = mapa["registros"]
    print(f"registros: {len(registros)}")
    for (conjunto, grupo), n in sorted(
        collections.Counter((r["conjunto"], r["grupo_primario"] or "-") for r in registros).items()
    ):
        print(f"  {n:>4}  {conjunto:<14} {grupo}")
    print("por grupo primario:")
    for grupo, n in sorted(collections.Counter(r["grupo_primario"] or "-" for r in registros).items()):
        print(f"  {n:>4}  {grupo}")  # "-" = sem grupo (controle_legitimo)
    eixos = collections.Counter(
        r["atributos"].get("eixo_vazamento") for r in registros if r["atributos"].get("eixo_vazamento")
    )
    print(f"eixo_vazamento: {dict(sorted(eixos.items()))}")
    repr_bipia = collections.Counter(
        r["atributos"]["representacao_r1"] for r in registros if r["conjunto"] == "bipia"
    )
    print(f"BIPIA, representacao pela R1: {dict(repr_bipia)}")
    print(f"textos repetidos dentro do mesmo conjunto: {mapa['textos_repetidos_no_mesmo_conjunto']}")

    if argumentos.apenas_contar:
        print("Nenhum arquivo gravado.")
        return 0

    conteudo = json.dumps(mapa, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporario = SAIDA.with_suffix(".tmp")
    with temporario.open("w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(conteudo)
    temporario.replace(SAIDA)
    print(f"gravado: {SAIDA}")
    print(f"sha256: {hashlib.sha256(SAIDA.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
