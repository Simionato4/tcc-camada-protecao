"""Tarefa 3.8 - converte e confere as 100 mensagens legitimas (ADR-0023).

Le `conjunto_teste/legitimas/mensagens.txt`, redigido a mao pelo autor conforme
`docs/guia-mensagens-legitimas.md`, e grava `conjunto_teste/legitimas/mensagens.jsonl`,
um registro por mensagem: id, bloco, numero na redacao e texto exatamente como escrito.

Antes de gravar, confere as regras OBJETIVAS do guia (secao 5). Nao avalia estilo nem
conteudo, e nao altera nenhum texto: se uma regra falha, o script para e aponta a
mensagem, e quem reescreve e o autor.

- 5 blocos de 20, numeracao 1 a 100 sem lacuna, nenhuma mensagem vazia ou repetida;
- nenhum endereco eletronico;
- nenhuma sequencia de 10 ou mais digitos, com ou sem pontuacao entre eles;
- nenhum numero que feche a conta de documento ou seja celular valido (mesma regra de
  colisao do corpus de PII, ADR-0015);
- pedido citado so de 10001 a 10030 (numeros 100NN);
- nenhum texto igual a caso do conjunto de teste ou do conjunto de desenvolvimento.

Uso:
    python scripts/gerar_legitimas.py --conferir   # so confere; nao grava
    python scripts/gerar_legitimas.py              # confere, grava e imprime o sha256
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "conjunto_teste" / "legitimas" / "mensagens.txt"
SAIDA = RAIZ / "conjunto_teste" / "legitimas" / "mensagens.jsonl"
MAPEAMENTO = RAIZ / "conjunto_teste" / "selecao" / "mapeamento_rotulos.json"
DESENVOLVIMENTO = RAIZ / "conjunto_desenvolvimento"

_spec = importlib.util.spec_from_file_location("gerar_corpus_pii", RAIZ / "scripts" / "gerar_corpus_pii.py")
pii = importlib.util.module_from_spec(_spec)
sys.modules["gerar_corpus_pii"] = pii
_spec.loader.exec_module(pii)

BLOCOS = 5
POR_BLOCO = 20
CABECALHO = re.compile(r"^##\s*Bloco\s+(\d)\b\s*[-—–:]?\s*(.*)$", re.I)
ITEM = re.compile(r"^(\d{1,3})\.\s+(.*\S)\s*$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
# Sequencia de digitos com separadores de documento ou telefone entre eles.
SEQUENCIA = re.compile(r"\+?\d[\d.\-/() ]*\d")
PEDIDO = re.compile(r"(?<!\d)100\d\d(?!\d)")


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def ler(fonte: Path = FONTE) -> list[dict]:
    mensagens, bloco, nome = [], None, None
    for numero_linha, linha in enumerate(fonte.read_text(encoding="utf-8").splitlines(), 1):
        if m := CABECALHO.match(linha.strip()):
            bloco, nome = int(m.group(1)), m.group(2).strip()
            continue
        if m := ITEM.match(linha.strip()):
            if bloco is None:
                raise ValueError(f"linha {numero_linha}: mensagem antes do primeiro bloco")
            mensagens.append({"numero": int(m.group(1)), "bloco": bloco, "nome_bloco": nome, "texto": m.group(2)})
    return mensagens


def problemas(mensagens: list[dict]) -> list[str]:
    erros = []
    numeros = [m["numero"] for m in mensagens]
    if numeros != list(range(1, BLOCOS * POR_BLOCO + 1)):
        erros.append(f"numeracao deve ser 1 a {BLOCOS * POR_BLOCO} sem lacuna; veio {len(numeros)} itens")
    for b in range(1, BLOCOS + 1):
        n = sum(1 for m in mensagens if m["bloco"] == b)
        if n != POR_BLOCO:
            erros.append(f"bloco {b}: {n} mensagens, esperado {POR_BLOCO}")
    vistos: dict[str, int] = {}
    for m in mensagens:
        n, t = m["numero"], m["texto"]
        chave = " ".join(t.lower().split())
        if chave in vistos:
            erros.append(f"{n}: repete a {vistos[chave]}")
        vistos[chave] = n
        if EMAIL.search(t):
            erros.append(f"{n}: contem endereco eletronico")
        for s in SEQUENCIA.finditer(t):
            digitos = re.sub(r"\D", "", s.group(0))
            if len(digitos) >= 10:
                erros.append(f"{n}: sequencia de {len(digitos)} digitos ({s.group(0)!r})")
            elif digitos and not pii.negativo_aceitavel(digitos):
                erros.append(f"{n}: {s.group(0)!r} e valido como documento ou celular")
        for p in PEDIDO.findall(t):
            if not 10001 <= int(p) <= 10030:
                erros.append(f"{n}: pedido {p} fora de 10001 a 10030")
    return erros


def hashes_existentes() -> dict[str, str]:
    """sha256 de todo texto ja presente no teste (pelo mapeamento) e no desenvolvimento."""
    saida = {}
    if MAPEAMENTO.exists():
        for r in json.loads(MAPEAMENTO.read_text(encoding="utf-8"))["registros"]:
            if r["conjunto"] != "legitimas":
                saida[r["sha256_texto"]] = f"teste:{r['caso_id']}"
    for arquivo in sorted(DESENVOLVIMENTO.rglob("*.jsonl")):
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                r = json.loads(linha)
                saida[sha256(r["texto"])] = f"desenvolvimento:{r['id']}"
    return saida


def registros(mensagens: list[dict]) -> list[dict]:
    return [
        {
            "id": f"leg-{m['numero']:03d}",
            "bloco": m["bloco"],
            "nome_bloco": m["nome_bloco"],
            "numero_redacao": m["numero"],
            "texto": m["texto"],
        }
        for m in mensagens
    ]


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--conferir", action="store_true")
    argumentos = analisador.parse_args()

    mensagens = ler()
    erros = problemas(mensagens)
    existentes = hashes_existentes()
    for m in mensagens:
        if (onde := existentes.get(sha256(m["texto"]))):
            erros.append(f"{m['numero']}: texto igual a {onde}")

    print(f"fonte: {FONTE.relative_to(RAIZ)}  sha256 {hashlib.sha256(FONTE.read_bytes()).hexdigest()}")
    print(f"mensagens: {len(mensagens)}")
    for b in range(1, BLOCOS + 1):
        do_bloco = [m for m in mensagens if m["bloco"] == b]
        if do_bloco:
            tamanhos = sorted(len(m["texto"]) for m in do_bloco)
            print(f"  bloco {b}: {len(do_bloco):>3}  {do_bloco[0]['nome_bloco']}"
                  f"  (caracteres: min {tamanhos[0]}, mediana {tamanhos[len(tamanhos) // 2]}, max {tamanhos[-1]})")
    if erros:
        print(f"\n{len(erros)} problema(s); nada gravado:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print("\nTodas as regras objetivas do guia conferem.")
    if argumentos.conferir:
        print("Nenhum arquivo gravado (--conferir).")
        return 0

    temporario = SAIDA.with_suffix(".tmp")
    with temporario.open("w", encoding="utf-8", newline="\n") as arquivo:
        for r in registros(mensagens):
            arquivo.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    temporario.replace(SAIDA)
    print(f"gravado: {SAIDA.relative_to(RAIZ)}")
    print(f"sha256: {hashlib.sha256(SAIDA.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
