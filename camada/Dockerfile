# A tag e mutavel: `3.12-slim` aponta para outra imagem a cada correcao de
# seguranca do Debian. Depois da primeira construcao, rode
# scripts/coletar_versoes.py, registre o digest em docs/versoes.md e troque a tag
# pelo digest, como ja feito com as quatro imagens de servico.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
