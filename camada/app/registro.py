"""Registro estruturado, um evento JSON por linha (RF-008; `PII-03`, `NOC-02`).

O texto **nao e gravado**, nem inteiro nem em parte, em nenhuma condicao: o registro
guarda o tamanho, um resumo criptografico, a decisao e, de cada deteccao, so o tipo e a
posicao. Assim a exigencia de que a camada mascare dado pessoal nos proprios registros
(`PII-03`) e cumprida por construcao: nao ha texto de onde o dado possa vazar.

Limite declarado: o resumo (16 caracteres do SHA-256 do texto) serve para conferir se dois
registros tratam do mesmo texto. Nao e anonimizacao: para um texto curto e previsivel, o
resumo pode ser refeito por tentativa.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _resumo(texto: str) -> str:
    # `surrogatepass`: texto com substituto solto nao pode derrubar o registro.
    return hashlib.sha256(texto.encode("utf-8", errors="surrogatepass")).hexdigest()[:16]


class Registrador:
    def __init__(self, caminho: str | None = None) -> None:
        self.caminho = Path(caminho) if caminho else None
        if self.caminho:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)

    def evento(self, **campos: object) -> None:
        linha = {
            "instante": datetime.now(timezone.utc).isoformat(),
            **campos,
        }
        serializado = json.dumps(linha, ensure_ascii=False)
        print(serializado, file=sys.stdout, flush=True)
        if self.caminho:
            with self.caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(serializado + "\n")

    def requisicao_processada(
        self,
        *,
        id_requisicao: str,
        ponto: str,
        condicao: str,
        texto_entrada: str,
        texto_saida: str,
        decisao: str,
        deteccoes: list[dict],
        erro: str | None,
        normalizacao: str,
        tempo_ms: float,
        versao_regras: str,
    ) -> None:
        """`deteccoes`: lista de `{"tipo", "posicao"}`. Nunca o trecho detectado."""
        self.evento(
            evento="requisicao_processada",
            id_requisicao=id_requisicao,
            ponto=ponto,
            condicao=condicao,
            resumo_entrada=_resumo(texto_entrada),
            tamanho_entrada=len(texto_entrada),
            resumo_saida=_resumo(texto_saida),
            tamanho_saida=len(texto_saida),
            decisao=decisao,
            deteccoes=deteccoes,
            quantidade_deteccoes=len(deteccoes),
            erro=erro,
            normalizacao=normalizacao,
            tempo_ms=tempo_ms,
            versao_regras=versao_regras,
        )


registrador = Registrador(os.getenv("ARQUIVO_LOG", "resultados/camada.jsonl"))
