# ADR-0024 - Dado pessoal e licenca nos conjuntos publicos (RQ-17)

## Contexto
O RQ-17 corrige a restricao do trabalho: e "nenhum **dado pessoal** real", e nao "somente
dados sinteticos". Os conjuntos de ataque sao prompts reais publicados. A constituicao foi
corrigida em 10/09/2026 (principio II); faltavam a redacao do README e a verificacao do
conteudo e da licenca de cada conjunto quanto a dado pessoal, exigida pela constituicao
"antes do congelamento".

## Verificacao do conteudo (31/10/2026)
`scripts/verificar_dados_pessoais.py`, sobre **todos os casos dos conjuntos publicos que
entram no teste**: 939 do Do-Not-Answer, 75 cargas do BIPIA e 50 do HackAPrompt (40 do
`INJ-05`, 10 do `CTX-02`), 1.064 textos. O texto do HackAPrompt foi lido do parquet pelo
mesmo recorte usado na amostragem (`strip`), e os 50 hashes conferem com a selecao.

| Procura | Resultado |
|---|---|
| Endereco eletronico | 0 |
| Telefone (padrao internacional) | 0 |
| Numero de seguridade social dos EUA | 0 |
| Numero de cartao (13 a 19 digitos com Luhn valido) | 0 |
| Endereco IPv4 | 0 |
| Documento brasileiro ou celular valido (regra de colisao da ADR-0015) | 0 |
| URL | 4, nas cargas do BIPIA: `www.example.com` (dominio reservado, 2), e dois dominios comerciais genericos - nenhum identifica pessoa |
| Candidatos a nome (duas ou tres palavras com inicial maiuscula fora do inicio da frase) | 33 ocorrencias em 27 casos, examinadas uma a uma |

**Exame dos candidatos a nome.** Nenhum e pessoa privada identificavel:
- **figuras publicas**, chefes de Estado e celebridades citados por nome: `dna-0128`,
  `dna-0132` e `dna-0137` (area de origem: linguagem toxica) e `dna-0914`, `dna-0918`,
  `dna-0920`, `dna-0922`, `dna-0926` e `dna-0930` (area de origem: desinformacao);
- **lugares, grupos, organizacoes e obras** (pais, etnia, geracao, programa de governo,
  empresa, jogo, premio, cidade);
- **falsos positivos** do padrao (`hackaprompt-ctx-03`: "Hello Bot", "Hi Human").

**Prenomes isolados.** Fora do padrao acima, a varredura das 939 perguntas por palavras com
inicial maiuscula no meio da frase encontrou prenomes sem sobrenome (por exemplo, "Claire",
"Lakisha", "Jamal"), usados pelo Do-Not-Answer como preenchimento de modelo de pergunta,
inclusive nas 112 de privacidade do individuo. Prenome isolado, sem sobrenome nem outro
atributo, nao identifica pessoa.

**Conclusao.** Nos 1.064 casos nao ha identificador estruturado de pessoa, e os nomes
citados sao de figuras publicas ou prenomes isolados. O principio II da constituicao e
atendido: nenhum dado pessoal real entra no experimento.

**Limitacao declarada.** A procura por identificadores estruturados e exaustiva para os
padroes listados. A procura por nomes e heuristica, com exame manual dos candidatos, e nao
garante encontrar nome escrito de outra forma (por exemplo, so com minusculas).

Os trechos encontrados ficam em `conjunto_teste/revisao/dados_pessoais_publicos.json`,
fora do versionamento (ADR-0016), porque contem texto dos conjuntos.

## Licenca
| Conjunto | Licenca | Situacao |
|---|---|---|
| Do-Not-Answer | CC BY-NC-SA 4.0 (dados), Apache-2.0 (codigo) | uso academico, sem fim comercial; a restricao nao comercial e declarada na monografia junto a referencia |
| HackAPrompt | MIT | acesso restrito por aceite de condicoes, registrado |
| BIPIA | MIT (Microsoft Corporation), com ressalva para tres conjuntos de terceiros nao usados | reconciliada em 17/09/2026 no `LICENSE` da versao obtida (`ORIGEM.md`) |

**Divergencia corrigida.** A reconciliacao do BIPIA tinha sido escrita a mao no
`ORIGEM.md`, que e gerado por `scripts/obter_conjuntos.py`; o script e o `origem.json`
continuavam com "confirmar no arquivo LICENSE do repositorio", e rodar o script de novo
apagaria a reconciliacao. Corrigido: o script passa a conter a licenca reconciliada e o
texto da reconciliacao, o `origem.json` foi atualizado, e
`scripts/tests/test_obter_conjuntos.py` confere que o registro versionado e exatamente o
que o script gera, e que nenhuma licenca diz "confirmar".

Nenhum conjunto e redistribuido (ADR-0016): a questao e o uso, e as tres licencas o
permitem nas condicoes acima. Leitura de licenca feita pelo autor com apoio de assistente,
e nao parecer juridico.

## Decisao
Os tres conjuntos entram no congelamento como estao, sem remocao de caso. README
corrigido (regra 3). O RQ-17 fica com a aceitacao atendida; a mudanca de estado e feita
no fechamento da etapa.

## Alternativa considerada
Remover ou mascarar os casos que citam figuras publicas por nome. Descartada: figura
publica citada em pergunta sobre vida publica nao e o dado que o principio II protege, e
remover alteraria os 939 da comparacao com Alves et al. (ADR-0020, D7).

## Data
2026-10-31
