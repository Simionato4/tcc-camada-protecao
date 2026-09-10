# A tag e mutavel. Depois da primeira construcao, registre o digest em
# docs/versoes.md e troque a tag pelo digest, como nas imagens de servico.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8100

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
