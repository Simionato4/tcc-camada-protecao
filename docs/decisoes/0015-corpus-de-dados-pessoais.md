# ADR-0015 - Corpus de dados pessoais: 350 positivos mais negativos dificeis

## Contexto
A proposta aprovada declara 350 ocorrencias sinteticas de documentos pessoais
brasileiros, usadas para medir precisao e revocacao do mascaramento.

A revisao externa de 10/09/2026 observou que o corpus, como desenhado, so continha
positivos. Sem negativos, **a precisao e quase nao informativa**: um detector que
marcasse toda sequencia numerica obteria revocacao alta e precisao aparentemente boa,
e so os negativos o denunciariam. O requisito ficou registrado como RQ-02.

## Decisao

O corpus tem **duas contagens declaradas**, e nao uma:

| Parte | Papel na metrica |
|---|---|
| **350 ocorrencias validas** | Positivos. Numero preservado da proposta aprovada |
| **Negativos dificeis** | Sequencias que um detector ingenuo marcaria, e que nao sao documento valido |

Preservar o 350 importa: e numero que consta na proposta aprovada, e altera-lo
exigiria declarar mudanca de escopo por uma razao que nao e de escopo.

### Classes de negativo dificil

| Classe | Por que e dificil |
|---|---|
| Digito verificador invalido | Tem o formato exato de um documento, e so a validacao o distingue |
| Sequencia de mesmo comprimento | Codigo de rastreio, numero de nota, identificador interno |
| Formato parcial | Documento truncado ou incompleto |
| Repeticao trivial | Sequencias como onze digitos iguais, que alguns validadores aceitam por engano |
| Numero em contexto nao pessoal | Valor monetario, CEP, data com pontuacao semelhante |

A classe de **digito verificador invalido** e a que mais importa, e e a razao de a
camada usar validacao de digito e nao apenas correspondencia por padrao. Ela mede
exatamente a diferenca entre as duas abordagens comparadas.

### Natureza de cada ocorrencia
Cada item registra `natureza`, distinguindo `pessoa_natural` de `pessoa_juridica`.
CNPJ identifica pessoa juridica e **nao e, por si, dado pessoal de pessoa natural**
(RQ-03): permanece no corpus como identificador estruturado brasileiro, com o recorte
declarado.

### Gabarito
Tipo, valor e **posicoes no texto original**, antes de qualquer normalizacao (RQ-07),
como ja e feito na base de conhecimento. Geracao com semente fixa e reproducao
verificavel por hash.

## Alternativa considerada
Manter 350 no total, com uma fracao de negativos. Descartada porque reduziria os
positivos e alteraria um numero que consta na proposta aprovada, exigindo declaracao
de mudanca por uma razao que nao e de escopo.

## Consequencia
As metricas do eixo de dados pessoais passam a ter significado:

- **revocacao** medida sobre os 350 positivos;
- **precisao** medida sobre positivos e negativos em conjunto, de modo que marcar um
  negativo dificil **custa**;
- **degradacao por classe de negativo** reportavel, o que expoe onde cada abordagem
  falha.

Sem os negativos, a comparacao entre a camada e a ferramenta externa premiaria o
detector mais permissivo. Com eles, a validacao de digito verificador — que e o
mecanismo proprio da camada — pode ser avaliada pelo que ela realmente faz: separar
o que tem formato de documento do que e documento.

O corpus cresce, e com ele o tempo de geracao e de analise. Nao ha custo de credito:
o corpus e avaliado fora do fluxo do assistente (ADR-0003).

## Data
2026-09-11
