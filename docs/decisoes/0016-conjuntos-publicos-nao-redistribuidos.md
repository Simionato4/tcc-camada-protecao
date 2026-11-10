# ADR-0016 - Conjuntos publicos nao sao redistribuidos; versiona-se a selecao

## Contexto
O repositorio do trabalho e publico e declara licenca MIT. Os tres conjuntos de
ataque tem licencas proprias, verificadas em 11/09/2026:

| Conjunto | Licenca |
|---|---|
| Do-Not-Answer | **CC BY-NC-SA 4.0** para os dados; Apache-2.0 para o codigo |
| HackAPrompt | MIT |
| BIPIA | A confirmar no ato do download |

O Do-Not-Answer e nao comercial **e com compartilhamento pela mesma licenca**.
Commitar os arquivos faria o repositorio conter conteudo sob ShareAlike, em conflito
com a licenca MIT declarada.

## Decisao
**Nenhum conjunto publico e redistribuido no repositorio.** Versiona-se a
**selecao**, e nao o conteudo:

| Vai para o repositorio | Nao vai |
|---|---|
| Script de obtencao, com repositorio e versao fixados | Arquivos dos conjuntos |
| URL, versao ou commit, data de obtencao, hash e licenca | Texto das solicitacoes e das cargas |
| Identificadores dos itens selecionados e hash de cada um | |
| Criterio e resultado da rotulacao (RQ-04) | |

Os arquivos baixados ficam em `conjunto_teste/origem/`, excluido do versionamento.

## Por que isso nao enfraquece a reprodutibilidade
Um terceiro reconstroi o conjunto exato executando o script de obtencao e conferindo
os hashes. A selecao congelada — quais itens, em que ordem, com que rotulos — esta
versionada, e e ela que define o experimento. O conteudo vem da fonte original, sob a
licenca da fonte.

E o mesmo padrao ja adotado com os PDFs do OWASP e do NIST na Etapa 1, e pela mesma
razao.

Efeito colateral favoravel: o hash por item detecta se a fonte alterou o conteudo
depois do congelamento. Se um item divergir, isso aparece na conferencia em vez de
passar despercebido.

## Consequencia
Quem for reproduzir precisa de acesso as fontes originais e precisa aceitar as
licencas delas. A restricao nao comercial do Do-Not-Answer acompanha o uso, e o
trabalho e academico — mas isso precisa estar declarado na monografia, junto a
referencia do conjunto.

Se alguma fonte sair do ar, a reproducao exata fica comprometida. O risco e inerente a
qualquer trabalho que use conjunto publico de terceiro, e o registro de versao, data e
hash e o que permite identificar exatamente o que se perdeu.

## Data
2026-09-11

## Revisao de 09/11/2026: os PDFs do referencial estavam versionados
Esta ADR e a atualizacao da Etapa 1 afirmam que os PDFs do OWASP e do NIST nao vao para o
repositorio. Revisao externa (31/10/2026) mostrou que os dois estavam versionados em
`docs/referencial/`. Corrigido: `git rm --cached` dos dois, que continuam na maquina do
autor, e `docs/referencial/*.pdf` no `.gitignore`. Permanecem no historico do Git ate
esta data. A identificacao exata de cada um fica registrada pelo sha256: OWASP GenAI LLM
Top 10 2026 v1.0 na ADR-0025 e, com o NIST AI 600-1, em `docs/matriz/01-extracao-bruta.md`,
secao Fontes. Os dois arquivos nao mudaram desde o commit `824d54f` (09/09/2026), em que
entraram: os hashes sao os das copias usadas na extracao.
O motivo e a coerencia com o que foi declarado, nao uma restricao de licenca: o NIST e
de dominio publico nos EUA, e o OWASP (CC BY-SA 4.0) admite copia com atribuicao.
