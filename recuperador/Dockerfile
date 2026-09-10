# A tag e mutavel. Depois da primeira construcao, registre o digest em
# docs/versoes.md e troque a tag pelo digest, como nas imagens de servico.
FROM python:3.12-slim

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
