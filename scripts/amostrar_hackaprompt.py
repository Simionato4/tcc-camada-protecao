"""Tarefa 3.3 — amostragem estratificada do HackAPrompt (ADR-0017).

Universo: submissoes bem-sucedidas, sem duplicatas de texto.
Classificacao: regra objetiva (`classificar_codificacao.py`) mais revisao manual.
Amostragem: alocacao igual por estrato, semente fixa.

**Nada do texto dos ataques e versionado** (ADR-0016). A selecao versionada guarda
identificador de origem, nivel, hash do texto e classe. O arquivo de revisao, que
contem o texto, fica fora do versionamento.

Fluxo:
    python scripts/amostrar_hackaprompt.py                 # classifica e amostra
    # revise conjunto_teste/revisao/hackaprompt_revisao.csv, coluna `classe_revisada`
    python scripts/amostrar_hackaprompt.py --aplicar-revisao
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import random
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "conjunto_teste" / "origem" / "hackaprompt"
SELECAO = RAIZ / "conjunto_teste" / "selecao"
REVISAO = RAIZ / "conjunto_teste" / "revisao"
TAMANHO_AMOSTRA = 40

_spec = importlib.util.spec_from_file_location(
    "classificar_codificacao", RAIZ / "scripts" / "classificar_codificacao.py"
)
clf = importlib.util.module_from_spec(_spec)
sys.modules["classificar_codificacao"] = clf
_spec.loader.exec_module(clf)


def escrever_texto(caminho: Path, conteudo: str, codificacao: str = "utf-8") -> None:
    """Escrita atomica: arquivo temporario ao lado, depois substituicao.

    Em 11/09/2026 uma execucao quebrou no meio de `escrever` porque o CSV estava aberto
    no Excel, que mantem trava exclusiva. O JSON ja havia sido reescrito e o CSV nao:
    selecao e revisao passaram a descrever amostras diferentes. `os.replace` e atomico
    nos dois sistemas; ou os dois arquivos trocam, ou nenhum troca.
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    with temporario.open("w", encoding=codificacao, newline="") as arquivo:
        arquivo.write(conteudo)
    os.replace(temporario, caminho)


def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def carregar_universo():
    import pandas as pd

    arquivos = sorted(ORIGEM.rglob("*.parquet"), key=lambda p: -p.stat().st_size)
    if not arquivos:
        raise FileNotFoundError(f"nenhum parquet em {ORIGEM}")
    quadro = pd.read_parquet(arquivos[0])
    total = len(quadro)

    quadro = quadro[quadro["correct"] == True]  # noqa: E712
    bem_sucedidas = len(quadro)

    # Normalizacao apenas das extremidades. Remover invisiveis ou decodificar antes
    # de deduplicar descartaria exatamente as variantes que interessam (ADR-0017).
    quadro = quadro.assign(_texto=quadro["user_input"].astype(str).str.strip())
    quadro = quadro[quadro["_texto"].str.len() > 0]
    if "timestamp" in quadro.columns:
        quadro = quadro.sort_values("timestamp")
    quadro = quadro.drop_duplicates(subset="_texto", keep="first")

    return quadro, total, bem_sucedidas


def alocar(estratos: dict[str, list], total: int) -> dict[str, int]:
    """Alocacao igual por estrato, limitada pelo tamanho, com excedente redistribuido.

    Igual, e nao proporcional: o criterio INJ-05 le o resultado **por tecnica**, e um
    estrato com dois casos nao sustenta leitura alguma.
    """
    restantes = {c: len(v) for c, v in estratos.items() if v}
    alocacao = {c: 0 for c in restantes}
    faltam = total
    while faltam > 0 and restantes:
        cota = max(1, faltam // len(restantes))
        for classe in sorted(restantes):
            if faltam == 0:
                break
            disponivel = restantes[classe] - alocacao[classe]
            leva = min(cota, disponivel, faltam)
            alocacao[classe] += leva
            faltam -= leva
        restantes = {
            c: n for c, n in restantes.items() if n > alocacao[c]
        }
    return {c: n for c, n in alocacao.items() if n}


def amostrar(semente: int) -> dict:
    quadro, total, bem_sucedidas = carregar_universo()
    registros = quadro.to_dict("records")

    estratos: dict[str, list] = {c: [] for c in clf.CLASSES}
    for registro in registros:
        estratos[clf.classificar(registro["_texto"])].append(registro)

    sorteio = random.Random(semente)
    alocacao = alocar(estratos, TAMANHO_AMOSTRA)

    selecionados = []
    for classe in sorted(alocacao):
        candidatos = sorted(estratos[classe], key=lambda r: sha256(r["_texto"]))
        for registro in sorteio.sample(candidatos, alocacao[classe]):
            selecionados.append(
                {
                    "ordem": len(selecionados) + 1,
                    "session_id": str(registro.get("session_id", "")),
                    "level": int(registro.get("level", -1)),
                    "sha256_user_input": sha256(registro["_texto"]),
                    "caracteres": len(registro["_texto"]),
                    "classe_automatica": classe,
                    "classe_revisada": "",
                    "_texto": registro["_texto"],
                }
            )

    return {
        "semente": semente,
        "data": date.today().isoformat(),
        "universo": {
            "submissoes_totais": total,
            "bem_sucedidas": bem_sucedidas,
            "apos_deduplicacao": len(registros),
        },
        "estratos": {c: len(v) for c, v in estratos.items()},
        "alocacao": alocacao,
        "selecionados": selecionados,
    }


def escrever(resultado: dict) -> None:
    # Versionado: sem o texto do ataque (ADR-0016).
    versionavel = {
        **{k: v for k, v in resultado.items() if k != "selecionados"},
        "selecionados": [
            {k: v for k, v in item.items() if k != "_texto"}
            for item in resultado["selecionados"]
        ],
    }
    conteudo_json = json.dumps(
        versionavel, indent=2, ensure_ascii=False, sort_keys=True
    ) + "\n"

    # Nao versionado: contem o texto, para a revisao manual.
    buffer = io.StringIO(newline="")
    escritor = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
    escritor.writerow(
        ["ordem", "level", "classe_automatica", "classe_revisada", "user_input"]
    )
    for item in resultado["selecionados"]:
        escritor.writerow(
            [item["ordem"], item["level"], item["classe_automatica"], "",
             item["_texto"].replace("\n", "\\n")]
        )

    # O CSV troca primeiro: e o arquivo que o Excel costuma estar segurando. Se a
    # substituicao dele falhar, o JSON permanece intacto e os dois seguem coerentes.
    escrever_texto(REVISAO / "hackaprompt_revisao.csv", buffer.getvalue(), "utf-8-sig")
    escrever_texto(SELECAO / "hackaprompt.json", conteudo_json)


def impedir_descarte_de_revisao(refazer: bool) -> str | None:
    """Recusa sobrescrever uma selecao que ja recebeu revisao manual.

    Em 11/09/2026 uma reexecucao apagou em silencio nove decisoes de classificacao
    feitas a mao. A revisao manual e trabalho humano registrado, exigido pela ADR-0017
    e pelo RQ-04: destrui-la sem aviso e perda de registro, nao inconveniencia.
    """
    caminho = SELECAO / "hackaprompt.json"
    if refazer or not caminho.exists():
        return None
    try:
        selecao = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    revisao = selecao.get("revisao")
    if not revisao:
        return None
    return (
        f"a selecao em {caminho} ja tem revisao manual aplicada "
        f"({revisao.get('casos_revistos', '?')} casos revistos, "
        f"{revisao.get('divergencias_da_regra', '?')} divergencias, "
        f"data {revisao.get('data', '?')}).\n"
        "Reamostrar apagaria esse trabalho. Arquive a selecao e o CSV de revisao, "
        "commite o arquivamento, e so entao rode de novo com --refazer."
    )


def aplicar_revisao(concordancia_total: bool = False) -> int:
    """Aplica a revisao manual a selecao vigente.

    Coluna `classe_revisada` em branco significa concordar com a regra. Isso e comodo
    para quem revisou e nao discordou, e indistinguivel de quem nao abriu o arquivo —
    em 11/09 e em 17/09 a segunda coisa aconteceu, e o registro passou a declarar uma
    revisao inexistente. Quando nenhuma linha esta preenchida, a concordancia precisa
    ser um ato afirmativo (`--concordancia-total`), nao o silencio.
    """
    caminho_selecao = SELECAO / "hackaprompt.json"
    caminho_revisao = REVISAO / "hackaprompt_revisao.csv"
    if not caminho_selecao.exists() or not caminho_revisao.exists():
        print("amostre primeiro: python scripts/amostrar_hackaprompt.py")
        return 1

    selecao = json.loads(caminho_selecao.read_text(encoding="utf-8"))
    por_ordem = {item["ordem"]: item for item in selecao["selecionados"]}

    with caminho_revisao.open(encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=";"))

    alteradas = 0
    invalidas = []
    for linha in linhas:
        revisada = (linha.get("classe_revisada") or "").strip()
        if not revisada:
            continue
        if revisada not in clf.CLASSES:
            invalidas.append(f"linha {linha['ordem']}: '{revisada}'")
            continue
        item = por_ordem[int(linha["ordem"])]
        if revisada != item["classe_automatica"]:
            alteradas += 1
        item["classe_revisada"] = revisada

    if invalidas:
        print(f"classes invalidas ({len(invalidas)}): {', '.join(invalidas[:5])}")
        print(f"validas: {', '.join(clf.CLASSES)}")
        return 1

    preenchidas = sum(1 for l in linhas if (l.get("classe_revisada") or "").strip())
    if preenchidas == 0 and not concordancia_total:
        print(
            f"nenhuma linha de {caminho_revisao} tem `classe_revisada` preenchida.\n"
            "Isso tanto pode significar que voce revisou os 40 e concordou com todos "
            "quanto que o arquivo nao foi aberto. A ADR-0017 e o RQ-04 exigem revisao "
            "caso a caso com autoria registrada, e o registro nao pode ficar ambiguo.\n"
            "Se revisou e concorda com todos, declare: "
            "python scripts/amostrar_hackaprompt.py --aplicar-revisao --concordancia-total",
            file=sys.stderr,
        )
        return 1

    for item in selecao["selecionados"]:
        item["classe_final"] = item["classe_revisada"] or item["classe_automatica"]

    selecao["revisao"] = {
        "data": date.today().isoformat(),
        "classificador": "autor (classificador unico, sem medida de concordancia)",
        "casos_revistos": len(linhas),
        "casos_com_rotulo_alterado": sum(
            1 for i in selecao["selecionados"] if i["classe_revisada"]
        ),
        "divergencias_da_regra": alteradas,
        "forma": (
            "caso a caso, com divergencias anotadas"
            if preenchidas
            else "caso a caso, concordancia total declarada pelo autor"
        ),
    }

    distribuicao: dict[str, int] = {}
    for item in selecao["selecionados"]:
        distribuicao[item["classe_final"]] = distribuicao.get(item["classe_final"], 0) + 1
    selecao["distribuicao_final"] = distribuicao

    escrever_texto(
        caminho_selecao,
        json.dumps(selecao, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )
    print(f"revisao aplicada: {alteradas} divergencias da regra automatica")
    for classe, quantidade in sorted(distribuicao.items()):
        print(f"  {quantidade:>3}  {classe}")
    return 0


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--aplicar-revisao", action="store_true")
    analisador.add_argument(
        "--concordancia-total",
        action="store_true",
        help="declara ter revisto os 40 casos sem discordar de nenhum",
    )
    analisador.add_argument("--semente", type=int, default=None)
    analisador.add_argument(
        "--refazer",
        action="store_true",
        help="reamostra mesmo que a selecao atual ja tenha revisao manual aplicada",
    )
    argumentos = analisador.parse_args()

    if argumentos.aplicar_revisao:
        return aplicar_revisao(argumentos.concordancia_total)

    impedimento = impedir_descarte_de_revisao(argumentos.refazer)
    if impedimento:
        print(impedimento, file=sys.stderr)
        return 1

    semente = argumentos.semente or int(os.getenv("SEMENTE_MESTRA", "20260829"))
    resultado = amostrar(semente)
    escrever(resultado)

    u = resultado["universo"]
    print(f"semente: {semente}")
    print(f"submissoes totais:   {u['submissoes_totais']:,}")
    print(f"bem-sucedidas:       {u['bem_sucedidas']:,}")
    print(f"apos deduplicacao:   {u['apos_deduplicacao']:,}")
    print()
    print("Estratos no universo:")
    for classe, quantidade in sorted(resultado["estratos"].items()):
        print(f"  {quantidade:>8,}  {classe}")
    print()
    print("Alocacao da amostra de 40:")
    for classe, quantidade in sorted(resultado["alocacao"].items()):
        print(f"  {quantidade:>3}  {classe}")
    print()
    print(f"selecao versionada:  {SELECAO / 'hackaprompt.json'}  (sem o texto)")
    print(f"para revisao manual: {REVISAO / 'hackaprompt_revisao.csv'}  (fora do Git)")
    print()
    print("Revise a coluna `classe_revisada` e rode --aplicar-revisao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
