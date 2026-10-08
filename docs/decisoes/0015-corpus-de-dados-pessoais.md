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

---

## Revisao de 08/10/2026: tipos de documento, distribuicao e suporte ao CNPJ

### Tipos e distribuicao
A versao final da proposta localizada no Drive do autor (`propostatccgabriel`, 23/08/2026)
declara "350 ocorrencias sinteticas de documentos pessoais brasileiros, geradas com
semente fixa", sem tipos nem distribuicao. O autor nao sabe dizer qual das versoes de
22 e 23/08/2026 foi a submetida; nenhuma das lidas fixa a distribuicao.

O rascunho `metodologiav2.md` (14/08/2026), do proprio autor, fixa **50 ocorrencias para
cada um de 7 tipos**. Decisao do autor, 08/10/2026: **adotar essa distribuicao.** E a
unica escrita pelo autor, e e coerente com a justificativa da proposta final, que cita
como lacuna do Presidio cinco destes tipos.

| Tipo | Positivos | Natureza | Digito verificador |
|---|---:|---|---|
| CPF | 50 | `pessoa_natural` | sim |
| CNPJ | 50 | `pessoa_juridica` (RQ-03) | sim |
| Cartao Nacional de Saude (CNS) | 50 | `pessoa_natural` | sim |
| NIT / PIS | 50 | `pessoa_natural` | sim |
| Titulo de eleitor | 50 | `pessoa_natural` | sim |
| Telefone | 50 | `pessoa_natural` | nao |
| Endereco eletronico | 50 | `pessoa_natural` | nao |
| **Total** | **350** | | |

O RG fica fora, como no rascunho: nao tem digito verificador padronizado nacionalmente.

Duas consequencias para o desenho (tarefa 3.5), ainda abertas:
- telefone e endereco eletronico nao tem digito verificador, e a classe de negativo
  "digito verificador invalido" nao se aplica a eles; precisam de classes proprias;
- o rascunho dizia que todo o corpus seria gerado pelo Faker. Medido na maquina do
  experimento: o Faker 40.38.0 `pt_BR` oferece `cpf`, `cnpj` e `rg`, e nao CNS, PIS ou
  titulo. A `validate-docbr` 2.0.0 tem `generate` para os cinco documentos. A escolha do
  gerador fica para a 3.5, porque gerar e validar com a mesma biblioteca cria
  dependencia entre o gabarito e o detector avaliado.

### RQ-03: suporte ao CNPJ alfanumerico

| Campo | Registro |
|---|---|
| Claim | a `validate-docbr` 2.0.0 valida CNPJ numerico e alfanumerico pela regra publicada pela Receita Federal |
| Fonte 1 | Receita Federal, "Perguntas e respostas: CNPJ alfanumerico", pergunta 14 (calculo do DV) e 15 (validade dos numeros atuais): https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf |
| Fonte 2 | pagina da versao no PyPI: https://pypi.org/project/validate-docbr/2.0.0/ (lancada em 04/04/2026; "numerico e alfanumerico"; licenca MIT) |
| Fonte 3 | codigo da versao instalada, na maquina do experimento: conjunto de caracteres `A-Z` mais digitos, valor `ord(caractere) - 48` |
| Data da consulta | 2026-10-08 |
| O que a fonte oficial diz | inicio da atribuicao a partir de julho de 2026 (IN RFB 2.119/2022, alterada pela IN RFB 2.229/2024); cada caractere vale ASCII menos 48; modulo 11 com pesos de 5 a 2 e de 6 a 2; os numeros atuais continuam validos; exemplo `12.ABC.345/01DE-35` |
| Divergencia | **o documento nao diz o que ocorre quando o resto da divisao e 0 ou 1.** Nao se supoe a regra do CNPJ numerico |
| Decisao | suporte verificado por `scripts/tests/test_suporte_cnpj.py`, que implementa a regra publicada e confere a biblioteca contra ela no exemplo oficial, num CNPJ numerico e em 400 bases sorteadas com semente fixa, todas com resto 2 ou maior |
| Pendencia | regra para resto 0 ou 1: conferir no texto da IN RFB 2.229/2024 ou em nota tecnica oficial antes de o corpus incluir CNPJ com esses restos |
| Impacto | RQ-03 (verificacao por teste unitario); desenho dos formatos de CNPJ do corpus (tarefa 3.5) |

## Data da revisao
2026-10-08
