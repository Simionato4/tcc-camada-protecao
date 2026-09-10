# Imagem base fixada por digest, coletado em 10/09/2026. A tag `3.12-slim` e
# mutavel: aponta para outra imagem a cada correcao de seguranca do Debian.
FROM python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# O modelo de embeddings e baixado na CONSTRUCAO, e nao em tempo de execucao
# (ADR-0011). Assim o ambiente continua subindo por um comando e a versao baixada
# fica fixada pelo digest da imagem. Baixar na primeira chamada deixaria a imagem
# leve, mas o modelo passaria a vir da internet no momento da execucao, sem digest,
# e um ambiente reconstruido meses depois poderia receber outro arquivo.
ENV CACHE_MODELOS=/opt/modelos
RUN python -c "from fastembed import TextEmbedding; \
    TextEmbedding(model_name='sentence-transformers/paraphrase-multilingual-mpnet-base-v2', \
                  cache_dir='/opt/modelos')"

COPY app ./app

EXPOSE 8100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]