# ADR-0004 - Repeticoes de latencia medidas sobre a camada, nao sobre o modelo

## Contexto
A proposta preve desvio-padrao entre repeticoes. O protocolo define latencia como
tempo interno da camada, com a rede fora da metrica. Repetir a chamada ao modelo
para obter dispersao de um tempo que nao inclui o modelo gastaria credito sem
acrescentar informacao.

## Decisao
A dispersao de latencia e obtida repetindo a camada sobre a mesma entrada, sem
nova chamada ao modelo. A camada e deterministica, entao a variacao medida e
ruido de maquina, que e exatamente o que a metrica deve capturar. Sao mantidas
3 repeticoes com chamada real ao modelo apenas na condicao A, no eixo de
vazamento de informacao, onde a contencao depende de o modelo desprotegido
recusar, e a Taxa de Compensacao depende desse valor.

## Alternativa considerada
Repetir todas as chamadas ao modelo 3 vezes. Descartada por custo (ADR-0001).

## Consequencia
Reduz o custo em cerca de dois tercos. As 3 repeticoes reais na condicao A
funcionam tambem como verificacao da premissa de determinismo a temperatura zero:
se as respostas divergirem, a dispersao e reportada em vez de assumida.

## Nota de verificacao (2026-08-31)

A premissa de determinismo recebeu uma verificacao preliminar durante o teste de
fumaca da Etapa 0. Tres chamadas consecutivas com o mesmo prompt de sistema, o
mesmo contexto e temperatura zero produziram resposta identica, com a mesma
contagem de tokens de saida (162) nas tres.

Tres amostras nao constituem prova, e a verificacao nao substitui as 3 repeticoes
previstas na condicao A: e la, sobre 248 casos, que a premissa e testada em
escala. Registrado aqui porque o resultado preliminar sustenta a decisao de nao
repetir chamadas ao modelo nas demais condicoes, e porque a evidencia precede a
execucao — se as repeticoes da condicao A divergirem, a divergencia sera
reportada, e nao ajustada.

## Data
2026-08-31
