# ADR-0028 - Congelamento sem a revisao do orientador

## Contexto
Na orientacao de 21/10/2026 ficou combinado que os documentos seriam revisados pelo
orientador antes do congelamento do conjunto de teste. O roteiro de revisao foi preparado
em 31/10/2026 (`docs/revisao-orientador-pre-congelamento.md`, commit `550b87a`) e enviado
ao orientador no mesmo dia, por WhatsApp.

O congelamento e pre-condicao para escrever qualquer regra da camada (constituicao,
principio I), e a demonstracao com a camada e prevista para a apresentacao de 24/11/2026.
A constituicao nao exige a revisao do orientador para congelar: a exigencia vem do
combinado de 21/10.

## Decisao (do autor, 12/11/2026)
Congelar o conjunto de teste **sem a revisao do orientador**, com `scripts/congelar.py
--gravar`, no estado commitado em que estiver no momento do congelamento.

As quatro perguntas da secao 5 do roteiro (comparador Presidio, regras D8 e D9, escopo do
TCC1, liberacao do congelamento) sao registradas como risco aceito.

## Alternativas descartadas
| Alternativa | Por que nao |
|---|---|
| Congelar so parte do conjunto | O congelamento e unico (`congelar.py` recusa um segundo); congelar em partes abriria espaco para ajustar o resto depois de ver as regras |

## Consequencias
- Apontamento do orientador feito **depois** do congelamento nao altera o conjunto
  congelado: vira resultado, limitacao declarada ou trabalho futuro.
- Se o apontamento revelar **defeito de metodo** (por exemplo, formula errada), vale a regra
  de defeito: commit do estado defeituoso, ADR de revisao anexada e declaracao do desvio
  pos-congelamento na monografia. O desvio nunca e silencioso.
- O roteiro continua valido e e apresentado ao orientador na proxima oportunidade.
- O texto de `scripts/congelar.py` que menciona a revisao do orientador (linhas 5 e 277)
  fica como esta: descreve o combinado de 21/10, e esta ADR registra o desvio.

## Data
2026-11-12
