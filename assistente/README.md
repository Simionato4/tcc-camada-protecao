# Assistente de referencia

Fluxo do chatbot de atendimento. **E variavel de controle do experimento:** identico
nas quatro condicoes comparadas. Se ele mudasse entre condicoes, a diferenca
observada deixaria de ser atribuivel a estrategia de protecao.

## Estado atual — tarefa 2.7

Fluxo linear com cinco pontos de chamada HTTP, ja com o **modelo real**. O gasto e
controlado pela variavel `MODO_SIMULADO` no `.env`: com `1`, nenhuma requisicao sai
da maquina e o custo e zero.

```
Entrada do usuario  (webhook)
      ↓
Camada /entrada     ← ponto de intercepcao 1: mensagem do usuario
      ↓
Recuperador /buscar
      ↓
Montar contexto
      ↓
Camada /contexto    ← ponto de intercepcao 2: conteudo recuperado
      ↓
Modelo /gerar
      ↓
Camada /saida       ← ponto de intercepcao 3: resposta gerada
      ↓
Responder
```

Os tres pontos de intercepcao existem **desde a condicao A**, apontando para o
endpoint que apenas encaminha. Adiciona-los so na condicao B alteraria o fluxo entre
condicoes e quebraria a variavel de controle.

## Desvio por decisao de bloqueio (Etapa 4, Fase 0, 09/11/2026)

Depois de cada um dos tres pontos da camada, um no `IF` testa `decisao == "bloquear"`.
Verdadeiro: o no **Responder bloqueio** devolve a mensagem de bloqueio, com o ponto em
que ocorreu (`ponto_bloqueio`) e o campo `erro`, e o fluxo para ali; o modelo nao e
chamado depois de bloqueio na entrada ou no contexto. Falso: o fluxo segue como antes.
O desvio vale nas quatro condicoes; na condicao A a camada nunca bloqueia, entao o
caminho e o mesmo de antes. `scripts/tests/test_fluxo.py` confere a estrutura.

Ate 09/11/2026 o desvio nao existia (decisao da tarefa 2.2: primeiro provar que o n8n
orquestra as chamadas e exporta de forma reproduzivel). O fluxo nao esta entre os
arquivos congelados: o hash do fluxo usado e registrado em cada execucao.

## Como importar

1. Abra o n8n em `http://localhost:5678`
2. Menu do canto superior direito → **Import from File** → selecione `fluxo.json`
3. Salve e ative o fluxo

Se algum no acusar erro de parametro, corrija pela interface. **A versao exportada
depois do ajuste e a que vale**: reexporte por Download e substitua este arquivo. O
JSON versionado precisa ser exatamente o que roda, sob pena de o fluxo deixar de ser
reproduzivel por terceiros.

## Como testar

Com o ambiente de pe:

```powershell
$corpo = @{
  mensagem      = "Qual o status do pedido 10001?"
  id_requisicao = [guid]::NewGuid().ToString()
  condicao      = "A"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5678/webhook/atendimento" `
  -ContentType "application/json" -Body $corpo
```

Resposta esperada: um objeto com `resposta` comecando em `[MODELO SIMULADO]`,
`decisao` igual a `encaminhar`, `tempo_ms`, `versao_regras` e o `id_requisicao`
enviado.

Se o fluxo nao estiver ativo, use `/webhook-test/atendimento` e clique em **Test
workflow** no n8n antes de cada chamada.

## O que o modelo recebe

A mensagem enviada ao servico do modelo combina duas coisas, **ambas ja processadas
pela camada**:

```
Contexto recuperado:
<texto devolvido por /contexto>

Pergunta do cliente:
<texto devolvido por /entrada>
```

Usar o texto devolvido pela camada, e nao o original, e o que faz a condicao B
diferir da A. Se a camada mascarou um documento pessoal, e o texto mascarado que
chega ao modelo — que e precisamente o efeito que o experimento mede.

O prompt de sistema **nao** trafega pelo fluxo: e carregado pelo proprio servico do
modelo, a partir do arquivo versionado. Se o fluxo pudesse informa-lo, bastaria um
erro de configuracao para uma condicao rodar com prompt diferente das outras, sem
que nada acusasse.

## Enderecos internos

Os nos usam `http://camada:8000`, `http://recuperador:8100` e `http://modelo:8200`,
que sao os nomes dos
servicos na rede interna do Compose. Nao usam `localhost`: dentro do conteiner do
n8n, `localhost` e o proprio n8n.
