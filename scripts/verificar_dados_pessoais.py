"""RQ-17 - procura dado pessoal nos casos dos conjuntos publicos que entram no teste.

Os conjuntos publicos sao prompts reais publicados (constituicao, principio II): o que a
regra proibe e dado pessoal real, nao texto de origem real. Este script varre os casos
selecionados - 939 do Do-Not-Answer, 75 cargas do BIPIA e 50 do HackAPrompt (40 do INJ-05
e 10 do CTX-02) - procurando identificadores estruturados e candidatos a nome de pessoa.

Achado de padrao nao e conclusao: cada ocorrencia e examinada a mao, e a decisao fica na
ADR. O terminal mostra so identificador do caso, tipo e contagem; o trecho encontrado,
que pode conter material do ataque, vai para `conjunto_teste/revisao/`, fora do
versionamento (ADR-0016).

Uso:  python scripts/verificar_dados_pessoais.py
"""

from __future__ import annotations

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
SAIDA = RAIZ / "conjunto_teste" / "revisao" / "dados_pessoais_publicos.json"

_spec = importlib.util.spec_from_file_location("gerar_corpus_pii", RAIZ / "scripts" / "gerar_corpus_pii.py")
pii = importlib.util.module_from_spec(_spec)
sys.modules["gerar_corpus_pii"] = pii
_spec.loader.exec_module(pii)

PADROES = {
    "email": re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
    "ssn_eua": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    "telefone": re.compile(r"(?<![\w-])\+?\(?\d{1,3}\)?[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}(?![\w-])"),
    "ipv4": re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"),
    "url": re.compile(r"https?://\S+|www\.\S+"),
}
SEQUENCIA = re.compile(r"\d[\d .\-/]{8,}\d")
# Candidato a nome: duas ou tres palavras com inicial maiuscula seguidas, fora do inicio.
NOME = re.compile(r"(?<=[a-z,;:] )(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})")


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def luhn(digitos: str) -> bool:
    soma, dobrar = 0, False
    for d in reversed(digitos):
        n = int(d) * (2 if dobrar else 1)
        soma += n - 9 if n > 9 else n
        dobrar = not dobrar
    return soma % 10 == 0


def casos() -> list[tuple[str, str]]:
    saida = []
    with (ORIGEM / "do-not-answer" / "data_en.csv").open(encoding="utf-8") as arquivo:
        for l in csv.DictReader(arquivo):
            saida.append((f"dna-{int(l['id']):04d}", l["question"]))
    dados = json.loads((ORIGEM / "bipia" / "benchmark" / "text_attack_test.json").read_text(encoding="utf-8"))
    for categoria, cargas in dados.items():
        for i, carga in enumerate(cargas):
            slug = re.sub(r"[^a-z0-9]+", "-", categoria.lower()).strip("-")
            saida.append((f"bipia-{slug}-{i}", carga))
    import pandas as pd  # so aqui: o resto do script nao depende do parquet

    alvo = {}
    for nome, prefixo in (("hackaprompt.json", "hackaprompt-inj"), ("hackaprompt_ctx.json", "hackaprompt-ctx")):
        for c in json.loads((SELECAO / nome).read_text(encoding="utf-8"))["selecionados"]:
            alvo[c["sha256_user_input"]] = f"{prefixo}-{int(c['ordem']):02d}"
    tabela = pd.read_parquet(ORIGEM / "hackaprompt" / "hackaprompt.parquet", columns=["user_input"])
    achados = {}
    for texto in tabela["user_input"].astype(str).str.strip():  # mesmo texto da amostragem
        h = sha256(texto)
        if h in alvo and h not in achados:
            achados[h] = texto
    faltando = set(alvo) - set(achados)
    if faltando:
        raise RuntimeError(f"{len(faltando)} casos do HackAPrompt nao encontrados no parquet")
    saida += [(alvo[h], t) for h, t in achados.items()]
    return saida


def examinar(texto: str) -> list[tuple[str, str]]:
    achados = [(tipo, m.group(0)) for tipo, p in PADROES.items() for m in p.finditer(texto)]
    for m in SEQUENCIA.finditer(texto):
        d = re.sub(r"\D", "", m.group(0))
        if 13 <= len(d) <= 19 and luhn(d):
            achados.append(("cartao_luhn", m.group(0)))
        if not pii.negativo_aceitavel(d):
            achados.append(("documento_brasileiro_ou_celular", m.group(0)))
    achados += [("candidato_nome", m.group(0)) for m in NOME.finditer(texto)]
    return achados


def main() -> int:
    todos = casos()
    por_tipo = collections.Counter()
    casos_por_tipo = collections.defaultdict(set)
    registro = []
    for caso_id, texto in todos:
        for tipo, trecho in examinar(texto):
            por_tipo[tipo] += 1
            casos_por_tipo[tipo].add(caso_id)
            registro.append({"caso_id": caso_id, "tipo": tipo, "trecho": trecho})
    conjuntos = collections.Counter(c.split("-")[0] for c, _ in todos)
    print(f"casos examinados: {len(todos)}  {dict(conjuntos)}")
    for tipo in sorted(casos_por_tipo):
        ids = sorted(casos_por_tipo[tipo])
        print(f"  {tipo:<32} {por_tipo[tipo]:>4} ocorrencias em {len(ids):>4} casos")
        print(f"      {', '.join(ids[:12])}{' ...' if len(ids) > 12 else ''}")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\ntrechos para exame manual: {SAIDA.relative_to(RAIZ)} (fora do versionamento)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
