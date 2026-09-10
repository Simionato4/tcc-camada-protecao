# Contexto de construcao e a raiz do repositorio: o servico usa o mesmo
# `executor/cliente_modelo.py` que o executor, para que as chamadas do fluxo e as do
# executor passem pelo mesmo guarda de orcamento e entrem no mesmo livro-caixa.
#
# A tag e mutavel. Depois da primeira construcao, registre o digest em
# docs/versoes.md e troque a tag pelo digest.
FROM python:3.12-slim

WORKDIR /app

COPY modelo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY executor ./executor
COPY modelo/app ./app

EXPOSE 8200

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8200"]
