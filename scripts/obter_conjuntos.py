"""Tarefa 3.1 — obtem os conjuntos publicos e registra procedencia.

**Nao redistribui nada** (ADR-0016). Os arquivos vao para `conjunto_teste/origem/`,
excluido do versionamento. O que fica versionado e o registro: repositorio, versao,
data de obtencao, hash de cada arquivo e licenca.

Um terceiro reconstroi o conjunto exato rodando este script e conferindo os hashes.

Uso:
    python scripts/obter_conjuntos.py
    python scripts/obter_conjuntos.py --conferir   # nao baixa; so confere hashes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "conjunto_teste" / "origem"
REGISTRO = RAIZ / "conjunto_teste" / "ORIGEM.md"

# Licencas conferidas em 11/09/2026. O script nao as verifica automaticamente: ele
# imprime o que precisa ser confirmado na pagina de cada fonte no dia do download.
CONJUNTOS_HF = [
    {
        "nome": "do-not-answer",
        "repo": "LibrAI/do-not-answer",
        "licenca": "CC BY-NC-SA 4.0 (dados) / Apache-2.0 (codigo)",
        "papel": "Solicitacoes nocivas — grupo NOC; area de vazamento como atributo secundario (ADR-0018)",
    },
    {
        "nome": "hackaprompt",
        "repo": "hackaprompt/hackaprompt-dataset",
        "licenca": "MIT",
        "papel": "Injecao direta — grupo INJ",
        # Repositorio restrito: exige conta no Hugging Face e aceite explicito das
        # condicoes de acesso na pagina do conjunto. Registrado porque quem for
        # reproduzir o trabalho precisara solicitar o mesmo acesso.
        "acesso": "restrito — exige aceite das condicoes e token de leitura",
    },
]

CONJUNTO_GIT = {
    "nome": "bipia",
    "url": "https://github.com/microsoft/BIPIA.git",
    "licenca": "confirmar no arquivo LICENSE do repositorio",
    "papel": "Injecao indireta — grupo INJ",
}


def sha256(caminho: Path) -> str:
    resumo = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(65536), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def arquivos_de(pasta: Path) -> list[Path]:
    return sorted(
        p for p in pasta.rglob("*")
        if p.is_file() and ".git" not in p.parts and ".cache" not in p.parts
    )


def token_hf() -> str | None:
    """Le o token do ambiente ou do .env. Nunca e impresso nem registrado."""
    if os.getenv("HF_TOKEN"):
        return os.getenv("HF_TOKEN")
    arquivo = RAIZ / ".env"
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.startswith("HF_TOKEN="):
                valor = linha.split("=", 1)[1].strip()
                return valor or None
    return None


def baixar_hf(conjunto: dict) -> dict:
    from huggingface_hub import dataset_info, snapshot_download

    destino = ORIGEM / conjunto["nome"]
    print(f"[{conjunto['nome']}] baixando {conjunto['repo']}...")
    token = token_hf()
    informacao = dataset_info(conjunto["repo"], token=token)
    snapshot_download(
        repo_id=conjunto["repo"],
        repo_type="dataset",
        local_dir=destino,
        token=token,
    )
    return {**conjunto, "versao": informacao.sha, "pasta": destino}


def baixar_git(conjunto: dict) -> dict:
    destino = ORIGEM / conjunto["nome"]
    if not destino.exists():
        print(f"[{conjunto['nome']}] clonando {conjunto['url']}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", conjunto["url"], str(destino)], check=True
        )
    else:
        print(f"[{conjunto['nome']}] ja presente; usando o clone existente")
    commit = subprocess.run(
        ["git", "-C", str(destino), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return {**conjunto, "versao": commit, "pasta": destino}


def inventariar(conjunto: dict) -> dict:
    arquivos = arquivos_de(conjunto["pasta"])
    return {
        "nome": conjunto["nome"],
        "origem": conjunto.get("repo") or conjunto["url"],
        "versao": conjunto["versao"],
        "licenca": conjunto["licenca"],
        "acesso": conjunto.get("acesso", "publico"),
        "papel": conjunto["papel"],
        "data_obtencao": date.today().isoformat(),
        "arquivos": [
            {
                "caminho": str(a.relative_to(conjunto["pasta"])).replace("\\", "/"),
                "bytes": a.stat().st_size,
                "sha256": sha256(a),
            }
            for a in arquivos
        ],
    }


def escrever_texto(caminho: Path, conteudo: str) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(conteudo)


def escrever_registro(inventarios: list[dict]) -> None:
    escrever_texto(
        ORIGEM.parent / "origem.json",
        json.dumps(inventarios, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )

    blocos = []
    for inv in inventarios:
        grandes = sorted(inv["arquivos"], key=lambda a: -a["bytes"])[:15]
        linhas = "\n".join(
            f"| `{a['caminho']}` | {a['bytes']:,} | `{a['sha256'][:16]}...` |" for a in grandes
        )
        blocos.append(f"""## {inv['nome']}

| Item | Valor |
|---|---|
| Origem | `{inv['origem']}` |
| Versao | `{inv['versao']}` |
| Data de obtencao | {inv['data_obtencao']} |
| Licenca | {inv['licenca']} |
| Acesso | {inv.get('acesso', 'publico')} |
| Papel no experimento | {inv['papel']} |
| Arquivos | {len(inv['arquivos'])} |

Maiores arquivos (hash completo em `origem.json`):

| Arquivo | Bytes | SHA-256 |
|---|---|---|
{linhas}
""")

    escrever_texto(REGISTRO, f"""# Procedencia dos conjuntos publicos

Gerado por `scripts/obter_conjuntos.py`. **Os conjuntos nao sao redistribuidos neste
repositorio** (ADR-0016): os arquivos ficam em `conjunto_teste/origem/`, fora do
versionamento. O que fica versionado e este registro e o `origem.json`, com o hash de
cada arquivo.

Para reconstruir:

```
python scripts/obter_conjuntos.py
python scripts/obter_conjuntos.py --conferir
```

O hash por arquivo tambem detecta se a fonte alterou o conteudo depois do
congelamento: a divergencia aparece na conferencia, em vez de passar despercebida.

{chr(10).join(blocos)}
## Licencas

Confirme na pagina de cada fonte, no dia do download. A restricao nao comercial do
Do-Not-Answer acompanha o uso e precisa ser declarada na monografia, junto a
referencia do conjunto.
""")


def conferir(inventarios_salvos: list[dict]) -> int:
    divergentes = []
    ausentes = []
    for inv in inventarios_salvos:
        pasta = ORIGEM / inv["nome"]
        for arquivo in inv["arquivos"]:
            caminho = pasta / arquivo["caminho"]
            if not caminho.exists():
                ausentes.append(f"{inv['nome']}/{arquivo['caminho']}")
            elif sha256(caminho) != arquivo["sha256"]:
                divergentes.append(f"{inv['nome']}/{arquivo['caminho']}")
    if ausentes:
        print(f"AUSENTES ({len(ausentes)}): {', '.join(ausentes[:5])}")
    if divergentes:
        print(f"DIVERGENTES ({len(divergentes)}): {', '.join(divergentes[:5])}")
    if not ausentes and not divergentes:
        total = sum(len(i["arquivos"]) for i in inventarios_salvos)
        print(f"integridade confirmada: {total} arquivos conferem")
        return 0
    return 1


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--conferir", action="store_true")
    argumentos = analisador.parse_args()

    caminho_json = ORIGEM.parent / "origem.json"

    if argumentos.conferir:
        if not caminho_json.exists():
            print("registro ainda nao existe; rode sem --conferir primeiro")
            return 1
        return conferir(json.loads(caminho_json.read_text(encoding="utf-8")))

    ORIGEM.mkdir(parents=True, exist_ok=True)
    inventarios = []
    pendentes = []

    # Falha em um conjunto nao aborta os demais: um repositorio restrito depende de
    # passo manual, e nao ha razao para perder o que ja foi obtido.
    for conjunto in CONJUNTOS_HF:
        try:
            inventarios.append(inventariar(baixar_hf(conjunto)))
        except Exception as erro:  # noqa: BLE001
            pendentes.append((conjunto["nome"], f"{type(erro).__name__}: {erro}"))
            print(f"[{conjunto['nome']}] PENDENTE — {type(erro).__name__}")
    try:
        inventarios.append(inventariar(baixar_git(CONJUNTO_GIT)))
    except Exception as erro:  # noqa: BLE001
        pendentes.append((CONJUNTO_GIT["nome"], f"{type(erro).__name__}: {erro}"))
        print(f"[{CONJUNTO_GIT['nome']}] PENDENTE — {type(erro).__name__}")

    if inventarios:
        escrever_registro(inventarios)

    print()
    for inv in inventarios:
        print(f"[ok]       {inv['nome']:16} versao {inv['versao'][:12]}  "
              f"{len(inv['arquivos'])} arquivos  licenca: {inv['licenca']}")
    for nome, motivo in pendentes:
        print(f"[pendente] {nome:16} {motivo[:110]}")

    print()
    if inventarios:
        print(f"registro: {REGISTRO}")
        print(f"origem:   {ORIGEM}  (fora do versionamento)")
    if pendentes:
        print()
        print("Conjunto restrito exige conta no Hugging Face, aceite das condicoes na")
        print("pagina do conjunto e HF_TOKEN no .env. O registro so estara completo")
        print("quando todos os conjuntos constarem — o congelamento depende disso.")
        return 1

    print()
    print("CONFIRME na pagina de cada fonte, hoje, que a licenca registrada confere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
