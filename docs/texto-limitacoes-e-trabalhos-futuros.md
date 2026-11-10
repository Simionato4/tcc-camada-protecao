# Texto para a monografia: limitacao e trabalho futuro sobre ataques adaptativos

Redigido conforme a orientacao de 02/09/2026: mostrar contato e conhecimento sobre
o tema, indicar como pode ser abordado em trabalhos futuros, e deixar claro o
escopo reduzido, sem inflar a expectativa da banca.

Sao tres insercoes em pontos diferentes do trabalho. Nao juntar as tres num lugar
so: a primeira e uma regra de redacao que vale para o texto inteiro, a segunda vai
em limitacoes e a terceira em trabalhos futuros.

---

## 1. Regra de redacao — vale para todo o documento

Toda afirmacao de bloqueio, contencao ou deteccao e enunciada com o escopo
explicito. Aplicar em texto corrido, legendas de tabela, titulos de grafico, resumo
e slides.

**Forma correta:** "a camada conteve X% das solicitacoes nocivas do conjunto
congelado" · "taxa de bloqueio sobre ataques publicados e nao adaptativos".

**Forma a evitar:** "a camada bloqueia X% dos ataques" · "eficacia de X% contra
injecao de instrucao".

A diferenca nao e estilistica. A primeira forma e verificavel a partir dos
registros; a segunda generaliza para uma populacao de ataques que o experimento
nao amostrou.

---

## 2. Para a secao de limitacoes

> Os indicadores de bloqueio e de contencao obtidos neste trabalho referem-se a
> ataques estaticos, provenientes de conjuntos publicados e congelados antes da
> implementacao das regras. Nao foram avaliados ataques adaptativos, entendidos
> como aqueles construidos ou otimizados por um adversario que conhece a
> especificacao da defesa implantada.
>
> A distincao e material. O OWASP GenAI LLM Top 10 2026 recomenda, entre as
> estrategias de prevencao para injecao de instrucao, testar contra atacantes
> adaptativos e rejeitar afirmacoes de sucesso apoiadas apenas em ataque estatico,
> citando resultados em que a taxa de sucesso estatico ficou proxima de zero
> enquanto a taxa adaptativa superou 90% para a maioria de doze defesas recentes
> avaliadas (OPEN WORLDWIDE APPLICATION SECURITY PROJECT, 2026; NASR et al., 2025).
> Como o codigo da camada e publico, a hipotese de um adversario que conhece as
> regras e realista, e nao pessimista.
>
> Decorre disso que **o experimento nao demonstra robustez diante de adversarios
> adaptativos**, e os valores aqui reportados nao autorizam conclusao sobre o
> desempenho da camada nesse cenario. A comparacao entre as quatro condicoes permanece
> valida, uma vez que todas enfrentam exatamente o mesmo conjunto de casos, e e o
> mesmo desenho adotado por Alves et al. (2025). O que nao se sustenta e a
> extrapolacao de qualquer uma das taxas para cenarios adversariais adaptativos.
>
> Uma segunda limitacao, de mesma origem, aplica-se ao estagio de normalizacao. A
> remocao de caracteres invisiveis, especificada pelo referencial adotado
> (OPEN WORLDWIDE APPLICATION SECURITY PROJECT, 2026), nao neutraliza cargas em
> texto visivel nem classes esteganograficas futuras, ressalva que o proprio
> documento normativo registra.
>
> *(Acrescentado em 09/11/2026.)* O congelamento do conjunto de teste antes da primeira
> regra impede o ajuste iterativo das regras aos casos, mas nao elimina o **conhecimento
> previo do autor**: para estratificar, mapear e verificar os conjuntos, o autor leu os
> casos publicos (ADR-0017, ADR-0018, ADR-0024) antes de escrever as regras. As regras
> foram desenvolvidas contra um conjunto separado (ADR-0019), mas a familiaridade com o
> estilo dos ataques pode ter orientado escolhas de desenho. A limitacao e declarada, e
> nao mensuravel por este experimento.
>
> Toda classificacao propria - estrato de codificacao do HackAPrompt, mapeamento para os
> grupos e redacao das mensagens legitimas - foi feita por um **unico classificador**, o
> autor, sem medida de concordancia entre anotadores; as duas primeiras rodadas da
> estratificacao foram anotadas com assistencia de IA (ADR-0017, ADR-0018).
>
> Os casos do HackAPrompt foram escritos para os prompts da competicao, em ingles, e aqui
> atacam um assistente de atendimento em portugues. Os resultados do `INJ-05` e do
> `CTX-02` medem a contencao de tentativas reais nesse cenario, e nao reproduzem o
> resultado da competicao (ADR-0018).

---

## 3. Para a secao de trabalhos futuros

> A avaliacao sob ataque adaptativo e a continuidade mais direta deste trabalho, e
> pode ser conduzida sem alterar o assistente de referencia nem o modelo de
> linguagem empregados.
>
> O desenho proposto restringe-se ao eixo de dados pessoais, unico em que a camada
> possui mecanismo especifico a ser posto a prova: normalizacao seguida de
> validacao de digito verificador. Consiste em um motor de mutacao deterministico,
> com semente registrada, aplicado as 350 ocorrencias sinteticas do corpus, com
> operadores fixos que representam classes conhecidas de ofuscacao. Cabe distinguir
> desde ja: mutacao por operador fixo **nao e ataque adaptativo**, porque nao
> considera nem explora a defesa especifica; e um teste de robustez a ofuscacao
> conhecida, mais forte que o estatico e mais fraco que o adaptativo. Os operadores
> propostos sao: separadores
> alternativos entre digitos; caracteres de largura zero intercalados; seletores de
> variacao e blocos de tag Unicode; homoglifos e digitos de largura completa;
> codificacao em base64, hexadecimal e percent-encoding; fragmentacao do documento
> entre campos; numeros por extenso; e encapsulamento em bloco de codigo ou
> estrutura de dados. Os dois primeiros grupos derivam nominalmente do controle de
> prevencao especificado pelo referencial adotado, o que permite tratar a avaliacao
> como verificacao direta desse controle.
>
> A metrica seria a revocacao da deteccao por operador de mutacao, comparada a
> revocacao sobre o corpus nao mutado, para a camada e para a ferramenta externa,
> produzindo uma tabela de degradacao por classe de ofuscacao. O custo em chamadas
> ao modelo de linguagem e nulo, uma vez que a decisao da camada e local e
> deterministica.
>
> Duas condicoes metodologicas sao indispensaveis. O conjunto adaptativo precisa
> ser gerado apos a execucao do protocolo principal e congelado com data e hash
> proprios. E nenhuma regra da camada pode ser alterada apos a observacao do
> resultado adaptativo: fazer isso converteria o experimento em ajuste do metodo ao
> resultado, exatamente o que a disciplina de congelamento adotada neste trabalho
> existe para impedir.
>
> Fora do eixo de dados pessoais, a avaliacao adaptativa de injecao de instrucao
> exigiria mecanismo de defesa semantico, ausente na camada aqui desenvolvida, e
> tecnicas de otimizacao adversarial que demandam acesso a gradientes do modelo ou
> volume de chamadas incompativel com os recursos deste trabalho.

>
> *(Acrescentado em 09/11/2026.)* A classificacao propria, feita por um unico
> classificador, pode ser reavaliada por um segundo anotador independente sobre uma
> amostra dos casos do HackAPrompt e dos julgamentos da condicao A, com medida de
> concordancia (kappa de Cohen), o que permitiria quantificar o vies de rotulagem
> hoje apenas declarado.
---

## Referencias a acrescentar

NASR, Milad et al. **The attacker moves second: stronger adaptive attacks bypass
defenses against LLM jailbreaks and prompt injections.** arXiv, 2025. Disponivel
em: https://arxiv.org/abs/2510.09023. Acesso em: 9 set. 2026.

A referencia do OWASP GenAI LLM Top 10 2026 ja consta na proposta.
