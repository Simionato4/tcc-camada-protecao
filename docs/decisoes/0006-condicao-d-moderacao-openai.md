# ADR-0006 - Condicao D usa a moderacao da OpenAI

## Contexto
A condicao D precisa de um servico de moderacao de conteudo atuando sobre a
mensagem de entrada. A proposta deixou o servico em aberto.

## Decisao
A condicao D usa o endpoint de moderacao da OpenAI (`omni-moderation-latest`),
que nao consome o credito da Anthropic. Isso introduz um segundo fornecedor, o
que nao conflita com a restricao de modelo unico: essa restricao vale para o
modelo gerador do assistente, e a moderacao nao gera resposta.

**Expectativa registrada antes da execucao:** um servico de moderacao classifica
categorias de dano, e nao injecao de instrucao. A condicao D deve apresentar
desempenho baixo em injecao direta e indireta por construcao, e nao por
inferioridade tecnica. Registrar isso antes evita que o resultado seja lido como
comparacao desleal, do mesmo modo que a proposta ja antecipa o baixo
reconhecimento de documentos brasileiros pelo Presidio.

## Alternativa considerada
Usar um classificador proprio como condicao D. Descartada por deixar de ser uma
ferramenta de terceiro, que e o que a condicao representa.

## Consequencia
Custo zero de credito. Exige conta na OpenAI com chave de API, e algumas contas
pedem meio de pagamento cadastrado mesmo para endpoint gratuito. **Verificar
isso na Etapa 0, nao no dia da execucao.**

## Data
2026-08-29
