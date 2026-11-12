"""Tarefa 3.11 - gera `conjunto_teste/CONGELADO.md` (constituicao, principio I).

Sem argumento, so mostra o conteudo que seria gravado e confere as pre-condicoes; nao
grava nada. Com `--gravar`, grava o arquivo. O congelamento so e feito depois da revisao
do orientador (orientacao de 21/10/2026).

Pre-condicoes conferidas, nesta ordem (qualquer falha impede gravar):
- `normalizacao.py`, `deteccao.py` e `decisao.py` nao existem no repositorio;
- `CONGELADO.md` ainda nao existe (o congelamento e unico);
- arvore de trabalho limpa: todo arquivo congelado esta commitado, e o hash registrado e
  o do commit indicado;
- os arquivos de origem dos conjuntos publicos conferem com `origem.json`.

Depois de gravado, `scripts/tests/test_congelado.py` falha se qualquer arquivo listado
mudar. E isso que torna o congelamento verificavel.

Uso:
    python scripts/congelar.py            # pre-visualizacao
    python scripts/congelar.py --gravar   # congela
"""

from __future__ import annotations

import argparse
import collections
import platform
import re
import unicodedata
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "conjunto_teste" / "CONGELADO.md"
MODULOS_PROIBIDOS = ("normalizacao.py", "deteccao.py", "decisao.py")

# Arquivos congelados: o que define os casos, o gabarito e o metodo de calculo.
CONGELADOS = [
    ("conjunto_teste/selecao/mapeamento_rotulos.json", "todos os casos do teste, grupo e rotulo (RQ-04)"),
    ("conjunto_teste/selecao/hackaprompt.json", "amostra do INJ-05 (40), ADR-0017"),
    ("conjunto_teste/selecao/hackaprompt_ctx.json", "subamostra do CTX-02 (10), ADR-0018"),
    ("conjunto_teste/selecao/rotulos.json", "livro de rotulos da classificacao R1, ADR-0017"),
    ("conjunto_teste/selecao/bipia_cenarios.json", "75 cenarios de injecao indireta, ADR-0014"),
    ("conjunto_teste/pii/corpus.jsonl", "corpus de documentos com gabarito, ADR-0015"),
    ("conjunto_teste/legitimas/mensagens.txt", "mensagens legitimas como redigidas, ADR-0023"),
    ("conjunto_teste/legitimas/mensagens.jsonl", "100 mensagens legitimas, ADR-0023"),
    ("conjunto_teste/origem.json", "procedencia e hash dos conjuntos publicos (RQ-05)"),
    ("conjunto_teste/ORIGEM.md", "procedencia legivel e licencas"),
    ("base_conhecimento/perguntas_pareadas.json", "perguntas dos cenarios do BIPIA, ADR-0012"),
    ("assistente/prompt_sistema.md", "prompt de sistema, variavel de controle"),
    # So as secoes FECHADAS (1, 2, 3 e 8): as secoes 4 a 7 fecham nas Etapas 5 e 6, e
    # completa-las depois e detalhe operacional permitido (RQ-19), nao mudanca de metodo.
    ("docs/protocolo.md#fechadas", "secoes FECHADAS do protocolo: repeticoes, tempo, piloto e formulas (RQ-19)"),
    ("docs/mapeamento-rotulos.md", "criterio textual do mapeamento (RQ-04)"),
    ("docs/guia-mensagens-legitimas.md", "regras de redacao das legitimas"),
    ("presidio-analyzer/conf/nlp_pt.yaml", "condicao C, ADR-0022"),
    ("presidio-analyzer/conf/analyzer_pt.yaml", "condicao C, ADR-0022"),
    ("presidio-analyzer/conf/recognizers_pt.yaml", "condicao C, ADR-0022"),
]
DOCUMENTOS_BASE = "base_conhecimento/documentos"
HISTORICOS = [
    "conjunto_teste/selecao/hackaprompt-v1-regra-com-defeito.json",
    "conjunto_teste/selecao/hackaprompt-v2-regra-rev2.json",
    "conjunto_teste/selecao/hackaprompt-v3-regra-rev3.json",
]
ARQUIVOS_PUBLICOS_USADOS = {
    "do-not-answer": "data_en.csv",
    "bipia": "benchmark/text_attack_test.json",
    "hackaprompt": "hackaprompt.parquet",
}


def sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def secoes_fechadas(caminho: Path) -> str:
    """Texto das secoes de nivel 2 cujo titulo contem FECHADO, na ordem do arquivo."""
    partes, atual = [], None
    for linha in caminho.read_text(encoding="utf-8").splitlines(keepends=True):
        if linha.startswith("## "):
            atual = [] if "FECHADO" in linha else None
            if atual is not None:
                partes.append(atual)
        if atual is not None:
            atual.append(linha)
    return "".join("".join(p) for p in partes)


def hash_registrado(caminho: str) -> str:
    """Hash de um item da lista de congelados, como registrado no CONGELADO.md."""
    if caminho.endswith("#fechadas"):
        texto = secoes_fechadas(RAIZ / caminho.removesuffix("#fechadas"))
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()
    alvo = RAIZ / caminho.rstrip("/")
    if alvo.is_dir():
        return hashlib.sha256("".join(sha(p) for p in sorted(alvo.glob("*.json"))).encode()).hexdigest()
    return sha(alvo)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def modulos_de_regra() -> list[str]:
    """Arquivos de regra no repositorio, versionados ou nao (ignorados pelo .gitignore ficam de fora)."""
    arquivos = git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    return [a for a in arquivos if Path(a).name in MODULOS_PROIBIDOS]


# A classificacao R1 depende da tabela Unicode (ADR-0017). Congelar com outro Python
# registraria um ambiente diferente do que produziu os rotulos.
UNIDATA_ESPERADA = "15.1.0"


def precondicoes(gravar: bool) -> list[str]:
    erros = []
    if unicodedata.unidata_version != UNIDATA_ESPERADA:
        erros.append(
            f"tabela Unicode {unicodedata.unidata_version} neste Python; a R1 usa {UNIDATA_ESPERADA} "
            "(ADR-0017): rode no ambiente virtual do experimento"
        )
    for nome in MODULOS_PROIBIDOS:
        achados = [c for c in modulos_de_regra() if Path(c).name == nome]
        if achados:
            erros.append(f"{nome} ja existe ({', '.join(achados)}): o congelamento tem de vir antes")
    if DESTINO.exists():
        erros.append("CONGELADO.md ja existe: o congelamento e unico")
    sujos = git("status", "--porcelain")
    if sujos and gravar:
        erros.append("arvore de trabalho com alteracoes nao commitadas:\n" + sujos)
    for caminho, _ in CONGELADOS:
        if not (RAIZ / caminho.removesuffix("#fechadas")).exists():
            erros.append(f"arquivo congelado ausente: {caminho}")
    origem = json.loads((RAIZ / "conjunto_teste" / "origem.json").read_text(encoding="utf-8"))
    for inv in origem:
        for a in inv["arquivos"]:
            p = RAIZ / "conjunto_teste" / "origem" / inv["nome"] / a["caminho"]
            if not p.exists() or sha(p) != a["sha256"]:
                erros.append(f"origem diverge de origem.json: {inv['nome']}/{a['caminho']}")
                break
    return erros


def conteudo() -> str:
    hoje = dt.date.today().isoformat()
    commit = git("rev-parse", "HEAD")
    mapa = json.loads((RAIZ / "conjunto_teste/selecao/mapeamento_rotulos.json").read_text(encoding="utf-8"))
    registros = mapa["registros"]
    por_conjunto = collections.Counter((r["conjunto"], r["grupo_primario"] or "-", r["papel"], r["origem_rotulo"]) for r in registros)
    origem = {i["nome"]: i for i in json.loads((RAIZ / "conjunto_teste/origem.json").read_text(encoding="utf-8"))}
    cenarios = json.loads((RAIZ / "conjunto_teste/selecao/bipia_cenarios.json").read_text(encoding="utf-8"))
    docs_base = sorted((RAIZ / DOCUMENTOS_BASE).glob("*.json"))

    l = []
    l.append("# Conjunto de teste congelado")
    l.append("")
    l.append(f"**Data do congelamento:** {hoje}  ")
    l.append(f"**Commit de referencia:** `{commit}` (todos os hashes abaixo sao deste commit)  ")
    l.append("**Gerado por:** `python scripts/congelar.py --gravar`")
    l.append("")
    l.append("A partir desta data, os arquivos listados nao mudam (constituicao, principio I). As")
    l.append("regras da camada (`normalizacao.py`, `deteccao.py`, `decisao.py`) so podem existir")
    l.append("depois deste arquivo, e sao desenvolvidas contra `conjunto_desenvolvimento/`, nunca")
    l.append("contra o conjunto abaixo. `scripts/tests/test_congelado.py` falha se qualquer hash")
    l.append("mudar. Desempenho ruim apos a execucao e resultado, nao defeito. Do protocolo, ficam")
    l.append("congeladas as secoes marcadas FECHADO; `#fechadas` indica o hash do texto dessas secoes.")
    l.append("")
    l.append("## 1. Composicao")
    l.append("")
    l.append("| Conjunto | Grupo | Papel | Origem do rotulo | Casos |")
    l.append("|---|---|---|---|---:|")
    for (conj, grupo, papel, orig), n in sorted(por_conjunto.items()):
        l.append(f"| {conj} | {grupo} | {papel} | {orig} | {n} |")
    l.append(f"| **Total** | | | | **{len(registros)}** |")
    l.append("")
    l.append(f"Textos repetidos dentro do mesmo conjunto: {mapa['textos_repetidos_no_mesmo_conjunto']} "
             "(Do-Not-Answer, mantido e declarado, ADR-0018).")
    l.append("")
    l.append("## 2. Arquivos congelados")
    l.append("")
    l.append("| Arquivo | Conteudo | SHA-256 |")
    l.append("|---|---|---|")
    for caminho, descricao in CONGELADOS:
        l.append(f"| `{caminho}` | {descricao} | `{hash_registrado(caminho)}` |")
    l.append(f"| `{DOCUMENTOS_BASE}/` | base de conhecimento, {len(docs_base)} arquivos; hash do encadeamento dos hashes por arquivo, em ordem de nome | `{hash_registrado(DOCUMENTOS_BASE + '/')}` |")
    l.append("")
    l.append(f"Colecao do Qdrant no estado limpo (hash lido do banco, RQ-18, ADR-0014): `{cenarios['hash_estado_limpo']}`.")
    l.append("")
    l.append("Arquivos historicos da amostragem do HackAPrompt, versionados como registro e **nao usados**:")
    for h in HISTORICOS:
        l.append(f"`{h}`;" if h != HISTORICOS[-1] else f"`{h}` (ADR-0017).")
    l.append("")
    l.append("## 3. Conjuntos publicos (RQ-05)")
    l.append("")
    l.append("Nao redistribuidos (ADR-0016). Arquivos usados; o hash de todos os arquivos obtidos esta em `origem.json`.")
    l.append("")
    l.append("| Conjunto | Origem | Versao | Obtido em | Arquivo usado | SHA-256 | Licenca |")
    l.append("|---|---|---|---|---|---|---|")
    for nome, arquivo in ARQUIVOS_PUBLICOS_USADOS.items():
        inv = origem[nome]
        h = next(a["sha256"] for a in inv["arquivos"] if a["caminho"] == arquivo)
        licenca = inv["licenca"].replace('ver "Licenca do BIPIA" abaixo', 'ver "Licenca do BIPIA" em `ORIGEM.md`')
        l.append(f"| {nome} | `{inv['origem']}` | `{inv['versao']}` | {inv['data_obtencao']} | `{arquivo}` | `{h}` | {licenca} |")
    l.append("")
    l.append("Dado pessoal: nenhum dado pessoal real nos 1.064 casos publicos (RQ-17, ADR-0024).")
    l.append("A restricao nao comercial do Do-Not-Answer acompanha o uso.")
    l.append("")
    l.append("## 4. Rotulacao (RQ-04)")
    l.append("")
    l.append("| Conjunto | Rotulo de origem | Mapeamento para o grupo | Autoria e data |")
    l.append("|---|---|---|---|")
    l.append("| Do-Not-Answer | `risk_area`, `types_of_harm` do proprio conjunto | NOC; nas 248 de *Information Hazards*, atributo `eixo_vazamento` | rotulo externo; mapeamento do autor, 08/10/2026 (ADR-0018) |")
    l.append("| BIPIA | categoria do proprio conjunto | INJ | rotulo externo; mapeamento do autor, 08/10/2026 |")
    l.append("| HackAPrompt, INJ-05 | `level` do proprio conjunto | INJ; estrato de codificacao pela R1 | estrato: classificacao do autor, rodadas 1 e 2 anotadas com assistencia de IA, quarta rodada sem divergencia, 08/10/2026 (ADR-0017) |")
    l.append("| HackAPrompt, CTX-02 | `level` 2 | CTX; criterio de extracao | desenho do autor, 08/10/2026 (ADR-0018) |")
    l.append("| Corpus de documentos | - | PII | desenho do autor; gerado em 28/10/2026 (ADR-0015) |")
    l.append("| Mensagens legitimas | - | sem grupo, `controle_legitimo` | redigidas a mao pelo autor, 29/10/2026 (ADR-0023) |")
    l.append("")
    l.append("Criterio textual: `docs/mapeamento-rotulos.md`. **Classificador unico:** toda classificacao")
    l.append("propria foi feita por um so classificador, o autor, sem medida de concordancia entre anotadores;")
    l.append("limitacao declarada.")
    l.append("")
    l.append("## 5. Recorte do CNPJ (RQ-03)")
    l.append("")
    l.append("O CNPJ identifica **pessoa juridica** e nao e, por si, dado pessoal de pessoa natural. Permanece")
    l.append("no corpus como identificador estruturado brasileiro, com o recorte declarado (atributo")
    l.append("`natureza = pessoa_juridica`). Formatos suportados: **numerico e alfanumerico** (25 positivos de")
    l.append("cada), conferidos por `scripts/tests/test_suporte_cnpj.py` e pela implementacao independente")
    l.append("dos digitos verificadores (ADR-0015).")
    l.append("")
    l.append("## 6. Metodo")
    l.append("")
    l.append("Formulas: `docs/protocolo.md`, secao 8 (ADR-0020, D1 a D13). Condicoes: A sem protecao, B camada,")
    l.append("C Presidio com adaptacao minima para portugues (ADR-0022), D moderacao OpenAI (ADR-0006).")
    l.append("Versoes dos componentes: `docs/versoes.md`.")
    l.append("")
    l.append("## 7. Fora da lista, e por que")
    l.append("")
    l.append("- `assistente/fluxo.json`: cada exportacao do n8n gera de novo os identificadores e as")
    l.append("  posicoes dos nos, e o hash mudaria sem mudanca de comportamento. O fluxo e variavel de")
    l.append("  controle: o hash do fluxo usado e registrado em cada execucao, como o da colecao do")
    l.append("  Qdrant (ADR-0014).")
    l.append("- `docs/matriz_criterios.md`: recebe a coluna de resultado na Etapa 7. Os criterios")
    l.append("  ficam fixados pelos ADRs e por este registro; nenhum criterio muda depois desta data.")
    l.append("")
    l.append("## 8. Ambiente de quem congelou")
    l.append("")
    fastembed = re.search(r"^fastembed==(\S+)", (RAIZ / "recuperador/requirements.txt").read_text(encoding="utf-8"), re.M)
    l.append(f"- Python {platform.python_version()}; tabela Unicode `{unicodedata.unidata_version}`")
    l.append("  (classificacao R1, ADR-0017).")
    l.append(f"- `fastembed` {fastembed.group(1) if fastembed else 'nao encontrado'} (recuperador; par modelo e versao")
    l.append("  da biblioteca como unidade de reproducao, ADR-0011).")
    l.append("")
    return "\n".join(l) + "\n"


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--gravar", action="store_true")
    argumentos = analisador.parse_args()

    erros = precondicoes(argumentos.gravar)
    texto = conteudo()
    if not argumentos.gravar:
        print(texto)
        print("-" * 72)
    if erros:
        print("PRE-CONDICOES NAO ATENDIDAS:")
        for e in erros:
            print(f"  - {e}")
        return 1
    if not argumentos.gravar:
        print("Pre-condicoes atendidas. Pre-visualizacao apenas: nada gravado.")
        print("Para congelar (ADR-0028): python scripts/congelar.py --gravar")
        return 0
    DESTINO.write_text(texto, encoding="utf-8", newline="\n")
    print(f"gravado: {DESTINO.relative_to(RAIZ)}  sha256 {sha(DESTINO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
