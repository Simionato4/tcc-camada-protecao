"""Pendencia (a) da ADR-0017: quantos casos do universo do HackAPrompt usam texto invertido.

LEITURA PURA. Nao grava arquivo algum. O criterio de inversao e a regra de decisao
foram fixados na ADR-0017 (bloco "Texto invertido", 08/10/2026) e commitados antes da
primeira execucao deste script. Alterar MINIMO_PALAVRA, MINIMO_FRASE ou LIMIAR_PCT
depois de ver o resultado seria ajuste orientado ao resultado.

Ordem de execucao, deliberada:
1. confere que o universo e os estratos sao os registrados na selecao vigente;
2. confere o controle positivo (ordem 18 da terceira amostra). Se o criterio nao o
   detectar, o script para ANTES de contar: o criterio nao captura a tecnica
   observada, e precisa ser revisto sem que numero algum tenha sido visto;
3. so entao conta, por estrato, e aplica a regra de decisao.

Nenhum texto de ataque e impresso: apenas contagens.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SELECAO_VIGENTE = RAIZ / "conjunto_teste" / "selecao" / "hackaprompt.json"

_spec = importlib.util.spec_from_file_location(
    "amostrar_hackaprompt", RAIZ / "scripts" / "amostrar_hackaprompt.py"
)
amostrar = importlib.util.module_from_spec(_spec)
sys.modules["amostrar_hackaprompt"] = amostrar
_spec.loader.exec_module(amostrar)
clf = amostrar.clf

# --- Parametros fixados na ADR-0017 antes da medicao --------------------------------
MINIMO_PALAVRA = 4      # palavras-alvo com menos letras nao contam
MINIMO_FRASE = 8        # frase-alvo contigua com menos letras nao conta
LIMIAR_PCT = 5          # regra de decisao: 5% do estrato
# Controle positivo: ordem 18 da terceira amostra (sha256 do user_input).
CONTROLE_POSITIVO = "fdfda262d32c4ab6dc1c1fbbe4ca33e21d72edd75cabcabc283c37b7df323996"

# Estratos de onde um caso migraria para codificacao se a inversao passasse a contar.
# Invisivel tem precedencia sobre codificacao em R1, e codificacao ja e o destino.
ORIGENS = (clf.TEXTO_SIMPLES, clf.ESCRITA_DISTINTA)
DESTINO = clf.CODIFICACAO


def tokens(texto: str) -> list[str]:
    """Palavras do texto apos NFKC e casefold, pela mesma definicao de palavra de R1."""
    return clf.PALAVRA.findall(unicodedata.normalize("NFKC", texto).casefold())


def palavras_alvo(alvo: str) -> set[str]:
    return {
        w for w in tokens(alvo) if len(w) >= MINIMO_PALAVRA and w != w[::-1]
    }


def mecanismos_de_inversao(texto: str, alvo: object) -> set[str]:
    """Devolve {'palavra', 'frase'} conforme o criterio da ADR-0017; vazio se nenhum.

    palavra: alguma palavra-alvo aparece, escrita de tras para frente, como palavra
             inteira do texto (e a forma invertida nao e ela propria palavra-alvo);
    frase:   a frase-alvo inteira, so letras, invertida, aparece como trecho contiguo
             das letras do texto, ignorando espacos e pontuacao.
    """
    if not isinstance(alvo, str) or not alvo.strip():
        return set()
    achados: set[str] = set()
    toks = tokens(texto)
    presentes = set(toks)
    alvos = palavras_alvo(alvo)
    if any(w[::-1] in presentes and w[::-1] not in alvos for w in alvos):
        achados.add("palavra")
    frase = "".join(tokens(alvo))
    if (
        len(frase) >= MINIMO_FRASE
        and frase != frase[::-1]
        and frase[::-1] in "".join(toks)
    ):
        achados.add("frase")
    return achados


def limiar(n_estrato: int) -> int:
    """Menor contagem que atinge LIMIAR_PCT do estrato (aritmetica inteira)."""
    return -(-n_estrato * LIMIAR_PCT // 100)


def main() -> int:
    vigente = json.loads(SELECAO_VIGENTE.read_text(encoding="utf-8"))
    quadro, _, _ = amostrar.carregar_universo()

    if "expected_completion" not in quadro.columns:
        print("coluna expected_completion ausente; nada medido.", file=sys.stderr)
        return 2
    if len(quadro) != vigente["universo"]["apos_deduplicacao"]:
        print(
            f"universo com {len(quadro)} casos, selecao vigente registra "
            f"{vigente['universo']['apos_deduplicacao']}; nada medido.",
            file=sys.stderr,
        )
        return 2

    registros = list(zip(quadro["_texto"], quadro["expected_completion"]))

    # 2. controle positivo, antes de qualquer contagem
    controle = [
        (t, a) for t, a in registros if amostrar.sha256(t) == CONTROLE_POSITIVO
    ]
    if len(controle) != 1:
        print("controle positivo nao encontrado no universo; nada medido.", file=sys.stderr)
        return 2
    mec_controle = mecanismos_de_inversao(*controle[0])
    if not mec_controle:
        print(
            "CONTROLE POSITIVO NAO DETECTADO: o criterio nao captura a tecnica da "
            "ordem 18. Contagem nao executada.",
            file=sys.stderr,
        )
        return 3
    print(f"controle positivo (ordem 18): detectado por {sorted(mec_controle)}")

    # 3. contagem
    n = {c: 0 for c in clf.CLASSES}
    inv = {c: 0 for c in clf.CLASSES}
    por_mecanismo = {"palavra": 0, "frase": 0, "ambos": 0}
    sem_alvo = 0
    for texto, alvo in registros:
        classe = clf.classificar(texto)
        n[classe] += 1
        if not isinstance(alvo, str) or not alvo.strip():
            sem_alvo += 1
            continue
        mec = mecanismos_de_inversao(texto, alvo)
        if mec:
            inv[classe] += 1
            if len(mec) == 2:
                por_mecanismo["ambos"] += 1
            else:
                por_mecanismo[next(iter(mec))] += 1

    registrados = vigente["estratos"]
    if n != registrados:
        print(
            f"estratos medidos {n} diferem dos registrados {registrados}; "
            "a regra de decisao nao se aplica.",
            file=sys.stderr,
        )
        return 2

    print(f"universo: {len(registros):,} casos; sem expected_completion: {sem_alvo:,}")
    print()
    print(f"{'estrato':<28}{'N':>8}{'com inversao':>14}{'%':>8}{'limiar':>8}")
    for classe in clf.CLASSES:
        pct = 100 * inv[classe] / n[classe] if n[classe] else 0.0
        print(f"{classe:<28}{n[classe]:>8,}{inv[classe]:>14,}{pct:>8.2f}{limiar(n[classe]):>8,}")
    print()
    print(
        "por mecanismo: "
        f"so palavra {por_mecanismo['palavra']:,}; "
        f"so frase {por_mecanismo['frase']:,}; ambos {por_mecanismo['ambos']:,}"
    )
    print()

    # Regra de decisao da ADR-0017
    gatilhos = []
    for classe in ORIGENS:
        if inv[classe] >= limiar(n[classe]):
            gatilhos.append(f"saida de {classe}: {inv[classe]} >= {limiar(n[classe])}")
    migram = sum(inv[c] for c in ORIGENS)
    if migram >= limiar(n[DESTINO]):
        gatilhos.append(f"entrada em {DESTINO}: {migram} >= {limiar(n[DESTINO])}")
    print(f"casos que migrariam para {DESTINO}: {migram:,}")
    if gatilhos:
        print("regra da ADR-0017 aponta: QUARTA RODADA")
        for g in gatilhos:
            print(f"  - {g}")
    else:
        print(
            "regra da ADR-0017 aponta: LIMITACAO DECLARADA "
            f"(pelo menos {migram:,} casos com a frase-alvo invertida fora de {DESTINO})"
        )
    print("Nenhum arquivo gravado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
