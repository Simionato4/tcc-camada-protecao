# Imagem base fixada por digest, coletado em 10/09/2026. A tag `3.12-slim` e
# mutavel: aponta para outra imagem a cada correcao de seguranca do Debian.
FROM python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]