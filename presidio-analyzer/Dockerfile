# Presidio analyzer com adaptacao minima para portugues (condicao C, ADR-0022, RQ-11).
#
# Parte da imagem fixada por digest e muda so o necessario para aceitar language="pt":
#   1. instala o modelo spaCy pt_core_news_lg 3.8.0, pela URL do release oficial e
#      conferido pelo sha256 (pip recusa a instalacao se o hash nao bater);
#   2. copia os tres arquivos de configuracao de conf/;
#   3. aponta as tres variaveis *_CONF_FILE para eles.
# Usuario, diretorio de trabalho e comando de inicio continuam os da imagem original
# (1001, /app, ./entrypoint.sh). O modelo en_core_web_lg permanece instalado e nao e
# usado: remove-lo seria uma alteracao a mais na imagem, sem efeito na condicao C.
FROM ghcr.io/data-privacy-stack/presidio-analyzer@sha256:ae8f6f111ac2f04e3fec552f7f80edd0dcbfa2dd69ee1b9e030475be31669885

USER root

# --no-deps: o modelo exige spacy >=3.8.0,<3.9.0, ja satisfeito pelo 3.8.13 da imagem;
# nenhuma outra biblioteca da imagem e alterada.
RUN pip install --no-cache-dir --no-deps \
    "pt_core_news_lg @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.8.0/pt_core_news_lg-3.8.0-py3-none-any.whl#sha256=2561c9a72a938d37141e9694e1a36d25061a44ce7e4f3bad2d3fa3bb836191af"

COPY conf/ /app/presidio_analyzer/conf/tcc/

ENV ANALYZER_CONF_FILE=presidio_analyzer/conf/tcc/analyzer_pt.yaml \
    RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/tcc/recognizers_pt.yaml \
    NLP_CONF_FILE=presidio_analyzer/conf/tcc/nlp_pt.yaml

USER 1001
