# Base de conhecimento — manifesto

Gerada por `scripts/gerar_base_conhecimento.py`. **Nenhum dado pessoal real**: todo
o conteudo vem do Faker `pt_BR` com semente fixa.

Para reconstruir de forma identica:

```
python scripts/gerar_base_conhecimento.py
python scripts/gerar_base_conhecimento.py --conferir
```

## Parametros

| Item | Valor |
|---|---|
| Semente | `20260829` |
| Documentos | 30 |
| Numeros de pedido | 10001 a 10030 |
| Faixa de tamanho | 532 a 658 caracteres |
| Tokens estimados | 173 a 214 |
| Ocorrencias de dado pessoal | 180 |

A estimativa de tokens usa 3.08 caracteres por token, calibrada
com medicao real: no teste de fumaca de 31/08/2026 um documento de 706 caracteres
consumiu cerca de 229 tokens de entrada. A faixa de 150 a 300 tokens do ADR-0007
corresponde a aproximadamente 460 a 930 caracteres.

## Gabarito

Cada documento traz `ocorrencias_dado_pessoal`, com tipo, valor e posicoes **no
texto original**, antes de qualquer normalizacao (RQ-07). O campo `natureza`
distingue `pessoa_natural` de `pessoa_juridica`: o CNPJ da transportadora e
identificador estruturado brasileiro, mas nao e dado pessoal de pessoa natural
(RQ-03).

Este gabarito serve a verificacao de integracao do criterio `PII-02`. Ele **nao
substitui** o corpus de 350 ocorrencias da Etapa 3, que e o conjunto congelado sobre
o qual precisao e revocacao sao medidas, e que precisara conter negativos dificeis
(RQ-02).

## Hashes

| Arquivo | SHA-256 |
|---|---|
| `documentos/doc-001.json` | `607644a2ac89732d2631bb9b7b46584a9e0e78b33d3f90f376d1956ec8438a0f` |
| `documentos/doc-002.json` | `edb1e8e7fbec896cad0df44f3866190739722c8df455031ca24a838201cd4826` |
| `documentos/doc-003.json` | `4bb2bd27df07bba7df1eefde6913f5638b884c0d62d2796b51c2f7013a10b41a` |
| `documentos/doc-004.json` | `a1ba7ef36298c38054bdeacb91b919015fdb1b2ce1554e114879659171eb7ad4` |
| `documentos/doc-005.json` | `e7b3d9985fa613da530163d012fa9256dd60cc8cc9c71d0f4235e2bab9466359` |
| `documentos/doc-006.json` | `d060075a3bf92e04452552ccb2b9503d19d79140d73fa66e1b6a768a76f61089` |
| `documentos/doc-007.json` | `7f0053a7bbd2d28f0f26063852234f64cdc7b93ba26e6f2fa2454b1aaa34dec8` |
| `documentos/doc-008.json` | `2135b9ea9d3c669f1b43cb63a13c442f628c59336d4452eb3ca5472432b25a81` |
| `documentos/doc-009.json` | `0b71de6e1b1db689c6206da3f5bf55f6405c133a5f921eeeb510d200ca8a1726` |
| `documentos/doc-010.json` | `70d9dfc2691c71bacb0b8b5af77e8095abfd26c5e94d0785e1e4d39cb5a0732d` |
| `documentos/doc-011.json` | `1cc1c7b3e4f8c44cbcda567eb2c4eccfc16f1b5fb07c9c90c2fbbcf9faa20a52` |
| `documentos/doc-012.json` | `4c441d814ede3b0c1ea8a0fb95cf3071c6409809c0ac4d6e331b5eae13463fba` |
| `documentos/doc-013.json` | `f6e28c458a457c510281738f2e7bf73d4e2d9e1bd4824fa16f22493b3f09517c` |
| `documentos/doc-014.json` | `62ab74dea759bd0da109a21df73ee665c8c2653bb0b2d2d23af7e907069428c7` |
| `documentos/doc-015.json` | `a3f68d5392113d26c7a43512cfb261ff61cfc4c8223d8718450a2621691ab72d` |
| `documentos/doc-016.json` | `f9277be24459f54d798bc0edc95f6792b3df9cf3160bd0893bf12f9c13a3b1a5` |
| `documentos/doc-017.json` | `d5d4b7d7464b057aab8c33d387cee228700e5a332ab01a53f0aca07f0be4d694` |
| `documentos/doc-018.json` | `79d90bd56c615e33fb18234d4c047cbd0cc2b3bc0d4958c8f02fb8f9a0d45799` |
| `documentos/doc-019.json` | `c99bd32310949e911332eb472ef0f5a1cf56ce3bf47fb341bf067346b6974d4c` |
| `documentos/doc-020.json` | `d54b3f515d2a8fc8c55b3b5b7a0977956c819afc351fbd1d5fd719c3871aeda4` |
| `documentos/doc-021.json` | `25c35d47e11e07ef483315d013185d4606ffde9d27264ad6c8b1ef062a9749df` |
| `documentos/doc-022.json` | `9a7af56866010ed8e1da7f889b396c2f4c4cd99e814e41f3fbf551bdd299e3ae` |
| `documentos/doc-023.json` | `31c69b4aa6976d6b1cf510093b031aab85d222030075c783c977116b1078aae3` |
| `documentos/doc-024.json` | `c76f870624ca788df89e94fad37762d1f8041e10f5a35dd5d9f3fd95b3d3fd03` |
| `documentos/doc-025.json` | `e5b79b53ab935a9d00db441b86ee72164f070e7e026dd719e63ea0cffe8d39f1` |
| `documentos/doc-026.json` | `2667ef183931a74f663859505644ae6bd7802221418ae80e24169110e63cc5f1` |
| `documentos/doc-027.json` | `0e271a705c3e26e1a993bc71349f4e92ba76f4e81dc28de29537b57a18225213` |
| `documentos/doc-028.json` | `aff3a1d7ae984ef0d889a5e5cc1918d567900896548153828199b1ec45479aa1` |
| `documentos/doc-029.json` | `39c0371a9dc28443ff2dd4c3311938fc4038fe8410edacf97f9efa84b70ed4df` |
| `documentos/doc-030.json` | `99d2a564f535aaf66a84418927bb8974abd5eb9dfe9d638d8b81bc8421a81063` |
| `perguntas_pareadas.json` | `ddf33084897289d12201f2ac7035b6809b8950e31b56f7d6c14ee40a21058ded` |
