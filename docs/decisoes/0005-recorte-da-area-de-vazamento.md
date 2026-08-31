# ADR-0005 - A area de vazamento de informacao entra com 248 solicitacoes

## Contexto
A proposta cita 248 solicitacoes na area de risco de vazamento de informacao. O
plano de cortes citava 136. Os dois numeros vem da distribuicao real do
Do-Not-Answer:

| Tipo de dano | Linhas |
|---|---|
| Vazamento de informacao sensivel de organizacao ou governo | 136 |
| Comprometimento de privacidade por vazamento de informacao privada | 112 |
| Area de risco completa | 248 |

O recorte de 136 corresponde a categoria comparavel com Alves et al. (2025),
onde os autores registraram 122 falsos negativos. O de 112 trata de dados de
individuos, mais alinhado ao foco em dados pessoais deste trabalho.

## Decisao
A area entra completa, com 248 solicitacoes, e esse e o numero que vai para o
`CONGELADO.md`. O recorte de 136 fica reservado como plano de corte, acionado
apenas se o julgamento manual da condicao A ultrapassar 4 horas.

## Alternativa considerada
Usar so as 136 desde o inicio. Descartada por perder o subconjunto de dados de
individuos, que e o foco declarado do trabalho.

## Consequencia
Ganha comparabilidade com Alves et al. e alinhamento com o recorte, de uma vez
so. Custa 2 repeticoes extras de LLM sobre 248 casos (ADR-0001) e mais tempo de
julgamento manual.

## Data
2026-08-31

