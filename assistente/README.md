# Assistente de referencia

Fluxo do chatbot de atendimento. **E variavel de controle do experimento:** identico
nas quatro condicoes comparadas. Se ele mudasse entre condicoes, a diferenca
observada deixaria de ser atribuivel a estrategia de protecao.

## Estado atual — tarefa 2.2

Fluxo linear com os quatro pontos de chamada HTTP presentes, e **modelo simulado**:
nenhuma chamada a API, custo zero. A chamada real entra na tarefa 2.7, depois de o
fluxo estar validado de ponta a ponta.

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
Modelo (simulado)
      ↓
Camada /saida       ← ponto de intercepcao 3: resposta gerada
      ↓
Responder
```

Os tres pontos de intercepcao existem **desde a condicao A**, apontando para o
endpoint que apenas encaminha. Adiciona-los so na condicao B alteraria o fluxo entre
condicoes e quebraria a variavel de controle.

## O que ainda nao existe, e por que

**Desvio por decisao de bloqueio.** Quando a camada responde `decisao: "bloquear"`,
o fluxo deve interromper e devolver a mensagem de bloqueio, em vez de seguir para o
modelo. Fica para depois de 2.2 de proposito: o objetivo desta tarefa e descobrir,
com o menor custo possivel, se o n8n consegue orquestrar as quatro chamadas e ser
exportado de forma reproduzivel. Isso e o risco desconhecido, e e o gatilho do corte
C4 do plano de corte. Ramificacao condicional e recurso padrao da ferramenta e nao
oferece risco comparavel.

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

## Enderecos internos

Os nos usam `http://camada:8000` e `http://recuperador:8100`, que sao os nomes dos
servicos na rede interna do Compose. Nao usam `localhost`: dentro do conteiner do
n8n, `localhost` e o proprio n8n.
